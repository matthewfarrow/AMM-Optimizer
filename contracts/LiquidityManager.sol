// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;


import "@openzeppelin/contracts/token/ERC721/IERC721Enumerable.sol";
import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";
//import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
//import "@uniswap/v3-core/contracts/libraries/TickMath.sol";
import "@uniswap/v3-periphery/contracts/interfaces/INonfungiblePositionManager.sol";
import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";



interface ISwapRouter {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
}

/**
 * @title LiquidityManager
 * @dev Manages automated Uniswap V3 liquidity positions with multicall support
 * @notice This contract holds user funds and executes rebalancing commands from the backend
 */
contract LiquidityManager is ReentrancyGuard, Ownable {
    using SafeERC20 for IERC20;
    using Address for address;

    // Uniswap V3 contracts
    INonfungiblePositionManager public immutable positionManager;
    ISwapRouter public immutable swapRouter;

    // User position tracking
    struct UserPosition {
        uint256 tokenId;
        address token0;
        address token1;
        uint24 fee;
        int24 tickLower;
        int24 tickUpper;
        uint256 depositedAmount0;
        uint256 depositedAmount1;
        uint256 createdAt;
        bool active;
    }

    // Whitelist management
    mapping(address => bool) public whitelistedUsers;
    mapping(address => UserPosition[]) public userPositions;
    mapping(uint256 => address) public positionToUser;

    // Events
    event UserWhitelisted(address indexed user, bool whitelisted);
    event PositionCreated(
        address indexed user,
        uint256 indexed tokenId,
        address token0,
        address token1,
        uint256 amount0,
        uint256 amount1
    );
    event PositionClosed(address indexed user, uint256 indexed tokenId);
    event EmergencyWithdraw(address indexed user, uint256 amount0, uint256 amount1);
    event CommandsExecuted(address indexed executor, uint256 commandCount);

    // Modifiers
    modifier onlyWhitelisted() {
        require(whitelistedUsers[msg.sender], "User not whitelisted");
        _;
    }

    modifier onlyPositionOwner(uint256 tokenId) {
        require(positionToUser[tokenId] == msg.sender, "Not position owner");
        _;
    }

    constructor(
        address _positionManager,
        address _swapRouter
    ) {
        positionManager = INonfungiblePositionManager(_positionManager);
        swapRouter = ISwapRouter(_swapRouter);
    }

    /**
     * @dev Whitelist or remove a user
     * @param user Address to whitelist/remove
     * @param whitelisted True to whitelist, false to remove
     */
    function setWhitelistStatus(address user, bool whitelisted) external onlyOwner {
        whitelistedUsers[user] = whitelisted;
        emit UserWhitelisted(user, whitelisted);
    }

    /**
     * @dev Batch whitelist multiple users
     * @param users Array of addresses to whitelist
     * @param whitelisted True to whitelist, false to remove
     */
    function batchSetWhitelistStatus(address[] calldata users, bool whitelisted) external onlyOwner {
        for (uint256 i = 0; i < users.length; i++) {
            whitelistedUsers[users[i]] = whitelisted;
            emit UserWhitelisted(users[i], whitelisted);
        }
    }

	function withdrawLiquidity(uint256 tokenId) external {
		require(msg.sender == funder, "Unauthorized");

		manager.safeTransferFrom(address(this), msg.sender, tokenId);

		uint8 index = indexFromPositionId[tokenId];
		Position storage position = positions[index];
		if (index < nLiquidityPositions && position.tokenId == tokenId) {
			numLiquidityPositionsByToken[position.base]--;
			numLiquidityPositionsByToken[position.quote]--;
			nLiquidityPositions--;
			if (nLiquidityPositions > 0) {
				positions[index] = positions[nLiquidityPositions];
				indexFromPositionId[positions[index].tokenId] = index;
			}
		}
	}

	function closeLiquidity(uint256 tokenId) public override {
		(,,,,,,, uint128 liquidity,,,,) = manager.positions(tokenId);
		uint8 index = indexFromPositionId[tokenId];
		Position storage position = positions[index];

		if (liquidity > 0) {
			// amount0Min and amount1Min are price slippage checks
			// if the amount received after burning is not greater than these minimums, transaction will fail
			INonfungiblePositionManager.DecreaseLiquidityParams memory params =
				INonfungiblePositionManager.DecreaseLiquidityParams({
					tokenId: tokenId,
					liquidity: liquidity,
					amount0Min: 0,
					amount1Min: 0,
					deadline: block.timestamp
				});

			manager.decreaseLiquidity(params);

			emit LiquidityModified(tokenId, position.base, position.quote, -int128(liquidity));

			// This is required for us to actually get the tokens out of the position
			collectFees(tokenId);
		}
	}

	// Destroys and liquidates the current liquidity position, if it exists.  Does not convert tokens.
	function destroyPosition(uint256 tokenId) external override {
		require(msg.sender == controller, "Unauthorized");

		uint8 index = indexFromPositionId[tokenId];
		Position storage position = positions[index];

		address base = position.base;
		address quote = position.quote;
		uint256 baseBal = contractBalance(base);
		uint256 quoteBal = contractBalance(quote);
		closeLiquidity(tokenId);
		collectFees(tokenId);
		manager.burn(tokenId);

		uint256 baseTaken = (contractBalance(base)) - baseBal;
		uint256 quoteTaken = (contractBalance(quote))- quoteBal;

		numLiquidityPositionsByToken[base]--;
		numLiquidityPositionsByToken[quote]--;
		nLiquidityPositions--;
		if (nLiquidityPositions > 0) {
			positions[index] = positions[nLiquidityPositions];
			indexFromPositionId[positions[index].tokenId] = index;
		}

		// We need to call this because of the possible situation where we sent all
		// of one token to the liquidity position, but received only the other token
		// back.
		if (baseTaken < 1000) onSendToken(base);
		if (quoteTaken < 1000) onSendToken(quote);

		emit PositionBurned(tokenId, base, quote, baseTaken, quoteTaken);
	}

	// Creates a new liquidity position with the given parameters, and returns the position ID.
	// This function will automatically swap tokens to fill the position if needed, first between quote and base,
	// then from available WETH, USDC, or ETH reserves.  If these are not available, the function will revert.
	// Prices are specified in quote per 1e12 base, where base is the other token traded on the pool.
	// toAdd is in quote units.
	function createV3Position(IUniswapV3Pool pool, address base, address quote, uint80 lowPrice12, uint80 highPrice12, uint256 toAdd) external override returns (uint256 tokenId, uint8 idx) {
		require(msg.sender == controller, "Unauthorized");
		require(nLiquidityPositions < positions.length, "Out of memory");
		require(base != quote, "Same token");

		// Get info on the tokens
		int8 decimalDiff = int8(IERC20(base).decimals()) - int8(IERC20(quote).decimals());

		// Convert prices
		// Note that these are in the pool's native ordering, not necessarily ours.
		uint160 sqrtRatioAX96 = correctPriceDirection(base, quote, getSqrtPriceX96FromPrice(decimalDiff, lowPrice12));
		uint160 sqrtRatioBX96 = correctPriceDirection(base, quote, getSqrtPriceX96FromPrice(decimalDiff, highPrice12));
		(uint160 sqrtRatioX96,,,,,,) = pool.slot0();
		if (sqrtRatioAX96 > sqrtRatioBX96)
			(sqrtRatioAX96, sqrtRatioBX96) = (sqrtRatioBX96, sqrtRatioAX96);

		// Get other random data about the pool
		uint128 liquidity = getLiquidityForAmount0(sqrtRatioAX96, sqrtRatioBX96, toAdd);

		uint256 feeGrowth;
		(tokenId, feeGrowth) = _mintV3Raw(pool, base, quote, sqrtRatioX96, sqrtRatioAX96, sqrtRatioBX96, liquidity);

		numLiquidityPositionsByToken[base]++;
		numLiquidityPositionsByToken[quote]++;
		positions[nLiquidityPositions] = Position(pool, feeGrowth, tokenId, base, quote);
		indexFromPositionId[tokenId] = nLiquidityPositions;
		idx = nLiquidityPositions;
		nLiquidityPositions++;

		// Not called because it won't do anything here
		// onSendToken(base);
		// onSendToken(quote);

		emit PositionMinted(tokenId, base, quote, lowPrice12, highPrice12, toAdd);
	}

	function _mintV3Raw(IUniswapV3Pool pool, address base, address quote, uint160 sqrtRatioX96, uint160 sqrtRatioAX96, uint160 sqrtRatioBX96, uint128 liquidity) internal returns (uint256 tokenId, uint256 feeGrowth) {
		// Much wow, such solidity!
		// Boy do we love stack limitations!!!
		uint72 tickVals = uint72(uint24(pool.tickSpacing()));
		unchecked {
			tickVals |= uint72(uint24((TickMath.getTickAtSqrtRatio(sqrtRatioAX96) / int24(uint24(tickVals))) * int24(uint24(tickVals)))) << 24;
			tickVals |= uint72(uint24((TickMath.getTickAtSqrtRatio(sqrtRatioBX96) / int24(uint24(tickVals))) * int24(uint24(tickVals)))) << 48;
		}

		tokenId = _odeToSolidity(base, quote, sqrtRatioX96, liquidity, tickVals, pool.fee());

		feeGrowth = address(base) < quote ? pool.feeGrowthGlobal0X128() : pool.feeGrowthGlobal1X128();
	}

	function _odeToSolidity(address base, address quote, uint160 sqrtRatioX96, uint128 liquidity, uint72 tickVals, uint24 fee) internal returns (uint256 tokenId) {

		address token0 = base > quote ? quote : base;
		address token1 = base > quote ? base : quote;

		// Calculate amounts of each token
		(uint256 amount0, uint256 amount1) = utils.getAmountsForLiquidity(
			sqrtRatioX96,
			TickMath.getSqrtRatioAtTick(int24(uint24(tickVals >> 24))),
			TickMath.getSqrtRatioAtTick(int24(uint24(tickVals >> 48))),
			liquidity
		);

		obtainTokens(token0, token1, amount0, amount1);

		INonfungiblePositionManager.MintParams memory params =
			INonfungiblePositionManager.MintParams({
				token0: token0,
				token1: token1,
				fee: fee,
				tickLower: int24(uint24(tickVals >> 24)),
				tickUpper: int24(uint24(tickVals >> 48)),
				amount0Desired: amount0,
				amount1Desired: amount1,
				amount0Min: 0,
				amount1Min: 0,
				recipient: address(this),
				deadline: block.timestamp
			});

		(tokenId,,,) = manager.mint(params);
	}

	function onERC721Received(address, address, uint256, bytes calldata) external returns (bytes4) {
		return this.onERC721Received.selector;
	}

    /**
     * @dev Create a new liquidity position
     * @param params Mint parameters for the position
     * @return tokenId The NFT token ID of the created position
     */
    function createPosition(INonfungiblePositionManager.MintParams calldata params)
        external
        onlyWhitelisted
        nonReentrant
        returns (uint256 tokenId)
    {
        // Transfer tokens from user to this contract
        IERC20(params.token0).safeTransferFrom(msg.sender, address(this), params.amount0Desired);
        IERC20(params.token1).safeTransferFrom(msg.sender, address(this), params.amount1Desired);

        // Approve position manager to spend tokens
        IERC20(params.token0).approve(address(positionManager), params.amount0Desired);
        IERC20(params.token1).approve(address(positionManager), params.amount1Desired);

        // Create position
        uint256 amount0;
        uint256 amount1;
        (tokenId, , amount0, amount1) = positionManager.mint(
            INonfungiblePositionManager.MintParams({
                token0: params.token0,
                token1: params.token1,
                fee: params.fee,
                tickLower: params.tickLower,
                tickUpper: params.tickUpper,
                amount0Desired: params.amount0Desired,
                amount1Desired: params.amount1Desired,
                amount0Min: params.amount0Min,
                amount1Min: params.amount1Min,
                recipient: address(this), // Contract receives the NFT
                deadline: params.deadline
            })
        );

        // Store position info
        userPositions[msg.sender].push(
            UserPosition({
                tokenId: tokenId,
                token0: params.token0,
                token1: params.token1,
                fee: params.fee,
                tickLower: params.tickLower,
                tickUpper: params.tickUpper,
                depositedAmount0: amount0,
                depositedAmount1: amount1,
                createdAt: block.timestamp,
                active: true
            })
        );

        positionToUser[tokenId] = msg.sender;

        emit PositionCreated(msg.sender, tokenId, params.token0, params.token1, amount0, amount1);
    }

    /**
     * @dev Execute multiple commands in a single transaction (only owner/backend)
     * @param commands Array of encoded function calls
     */
    function executeCommands(bytes[] calldata commands) external onlyOwner {
        for (uint256 i = 0; i < commands.length; i++) {
            address(this).functionCall(commands[i]);
        }
        emit CommandsExecuted(msg.sender, commands.length);
    }

    /**
     * @dev Decrease liquidity of a position
     * @param tokenId Position NFT token ID
     * @param liquidity Amount of liquidity to remove
     * @param amount0Min Minimum amount of token0 to receive
     * @param amount1Min Minimum amount of token1 to receive
     * @param deadline Transaction deadline
     */
    function decreaseLiquidity(
        uint256 tokenId,
        uint128 liquidity,
        uint256 amount0Min,
        uint256 amount1Min,
        uint256 deadline
    ) external onlyOwner {
        positionManager.decreaseLiquidity(
            DecreaseLiquidityParams({
                tokenId: tokenId,
                liquidity: liquidity,
                amount0Min: amount0Min,
                amount1Min: amount1Min,
                deadline: deadline
            })
        );
    }

    /**
     * @dev Increase liquidity of a position
     * @param tokenId Position NFT token ID
     * @param amount0Desired Desired amount of token0
     * @param amount1Desired Desired amount of token1
     * @param amount0Min Minimum amount of token0 to add
     * @param amount1Min Minimum amount of token1 to add
     * @param deadline Transaction deadline
     */
    function increaseLiquidity(
        uint256 tokenId,
        uint256 amount0Desired,
        uint256 amount1Desired,
        uint256 amount0Min,
        uint256 amount1Min,
        uint256 deadline
    ) external onlyOwner {
        // Approve tokens
        address token0 = _getPositionToken0(tokenId);
        address token1 = _getPositionToken1(tokenId);
        
        IERC20(token0).approve(address(positionManager), amount0Desired);
        IERC20(token1).approve(address(positionManager), amount1Desired);

        positionManager.increaseLiquidity(
            IncreaseLiquidityParams({
                tokenId: tokenId,
                amount0Desired: amount0Desired,
                amount1Desired: amount1Desired,
                amount0Min: amount0Min,
                amount1Min: amount1Min,
                deadline: deadline
            })
        );
    }

    /**
     * @dev Collect fees from a position
     * @param tokenId Position NFT token ID
     * @param recipient Address to receive the fees
     * @param amount0Max Maximum amount of token0 to collect
     * @param amount1Max Maximum amount of token1 to collect
     */
    function collectFees(
        uint256 tokenId,
        address recipient,
        uint128 amount0Max,
        uint128 amount1Max
    ) external onlyOwner {
        positionManager.collect(
            CollectParams({
                tokenId: tokenId,
                recipient: recipient,
                amount0Max: amount0Max,
                amount1Max: amount1Max
            })
        );
    }

    /**
     * @dev Swap tokens using Uniswap V3
     * @param tokenIn Input token address
     * @param tokenOut Output token address
     * @param fee Pool fee tier
     * @param amountIn Amount of input token
     * @param amountOutMinimum Minimum amount of output token
     * @param deadline Transaction deadline
     * @param sqrtPriceLimitX96 Price limit (0 for no limit)
     */
    function swapTokens(
        address tokenIn,
        address tokenOut,
        uint24 fee,
        uint256 amountIn,
        uint256 amountOutMinimum,
        uint256 deadline,
        uint160 sqrtPriceLimitX96
    ) external onlyOwner {
        IERC20(tokenIn).approve(address(swapRouter), amountIn);
        
        swapRouter.exactInputSingle(
            ISwapRouter.ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: fee,
                recipient: address(this),
                deadline: deadline,
                amountIn: amountIn,
                amountOutMinimum: amountOutMinimum,
                sqrtPriceLimitX96: sqrtPriceLimitX96
            })
        );
    }

    /**
     * @dev Withdraw a position (user can withdraw their position)
     * @param tokenId Position NFT token ID
     */
    function withdrawPosition(uint256 tokenId) external onlyPositionOwner(tokenId) nonReentrant {
        // Get position info
        (, , address token0, address token1, , , , uint128 liquidity, , , , ) = positionManager.positions(tokenId);
        
        if (liquidity > 0) {
            // Remove all liquidity
            positionManager.decreaseLiquidity(
                DecreaseLiquidityParams({
                    tokenId: tokenId,
                    liquidity: liquidity,
                    amount0Min: 0,
                    amount1Min: 0,
                    deadline: block.timestamp + 300
                })
            );
        }

        // Collect any remaining tokens
        positionManager.collect(
            CollectParams({
                tokenId: tokenId,
                recipient: msg.sender,
                amount0Max: type(uint128).max,
                amount1Max: type(uint128).max
            })
        );

        // Transfer NFT to user
        positionManager.burn(tokenId);

        // Mark position as inactive
        _markPositionInactive(msg.sender, tokenId);

        emit PositionClosed(msg.sender, tokenId);
    }

    /**
     * @dev Emergency withdraw function for users
     * @param token0 Token0 address
     * @param token1 Token1 address
     */
    function emergencyWithdraw(address token0, address token1) external onlyWhitelisted nonReentrant {
        uint256 balance0 = IERC20(token0).balanceOf(address(this));
        uint256 balance1 = IERC20(token1).balanceOf(address(this));

        if (balance0 > 0) {
            IERC20(token0).safeTransfer(msg.sender, balance0);
        }
        if (balance1 > 0) {
            IERC20(token1).safeTransfer(msg.sender, balance1);
        }

        emit EmergencyWithdraw(msg.sender, balance0, balance1);
    }

    /**
     * @dev Get user's positions
     * @param user User address
     * @return Array of user positions
     */
    function getUserPositions(address user) external view returns (UserPosition[] memory) {
        return userPositions[user];
    }

    /**
     * @dev Get position details by token ID
     * @param tokenId Position NFT token ID
     * @return Position details
     */
    function getPosition(uint256 tokenId) external view returns (UserPosition memory) {
        address user = positionToUser[tokenId];
        require(user != address(0), "Position not found");
        
        UserPosition[] memory positions = userPositions[user];
        for (uint256 i = 0; i < positions.length; i++) {
            if (positions[i].tokenId == tokenId) {
                return positions[i];
            }
        }
        revert("Position not found");
    }

    /**
     * @dev Check if user is whitelisted
     * @param user User address
     * @return True if whitelisted
     */
    function isWhitelisted(address user) external view returns (bool) {
        return whitelistedUsers[user];
    }

    // Internal functions

    function _getPositionToken0(uint256 tokenId) internal view returns (address) {
        (, , address token0, , , , , , , , , ) = positionManager.positions(tokenId);
        return token0;
    }

    function _getPositionToken1(uint256 tokenId) internal view returns (address) {
        (, , , address token1, , , , , , , , ) = positionManager.positions(tokenId);
        return token1;
    }

    function _markPositionInactive(address user, uint256 tokenId) internal {
        UserPosition[] storage positions = userPositions[user];
        for (uint256 i = 0; i < positions.length; i++) {
            if (positions[i].tokenId == tokenId) {
                positions[i].active = false;
                break;
            }
        }
    }

    // Receive ETH (for WETH wrapping if needed)
    receive() external payable {}
}
