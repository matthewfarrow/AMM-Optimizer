// FRONTEND FIX: Skip approval when allowances are sufficient
// Add this to StrategyConfig.tsx in the handleSubmit function

const checkAndSkipApproval = async () => {
  console.log('🔍 Checking if approval is needed...');
  
  // Check current allowances
  const token0Allowance = await readContract({
    address: finalToken0Address as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: [address, UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`],
  });
  
  const token1Allowance = await readContract({
    address: finalToken1Address as `0x${string}`,
    abi: ERC20_ABI,
    functionName: 'allowance',
    args: [address, UNISWAP_V3_ADDRESSES.NONFUNGIBLE_POSITION_MANAGER as `0x${string}`],
  });
  
  // Calculate required amounts
  const amount0Desired = parseUnits(amount0, token0Symbol === 'USDC' ? 6 : 18);
  const amount1Desired = parseUnits(amount1, token1Symbol === 'USDC' ? 6 : 18);
  
  console.log('💰 Allowance check:', {
    token0Allowance: token0Allowance.toString(),
    token1Allowance: token1Allowance.toString(),
    amount0Desired: amount0Desired.toString(),
    amount1Desired: amount1Desired.toString()
  });
  
  // Check if approval is needed
  const needsToken0Approval = token0Allowance < amount0Desired;
  const needsToken1Approval = token1Allowance < amount1Desired;
  
  if (needsToken0Approval) {
    console.log('⚠️  Token0 approval needed');
    await approveToken(finalToken0Address, amount0Desired);
    return false; // Wait for approval
  }
  
  if (needsToken1Approval) {
    console.log('⚠️  Token1 approval needed');
    await approveToken(finalToken1Address, amount1Desired);
    return false; // Wait for approval
  }
  
  console.log('✅ No approval needed - proceeding to position creation');
  return true; // Can proceed directly
};

// Update handleSubmit function
const handleSubmit = async () => {
  console.log('🚀 Starting position creation process...');
  
  // Check if approval is needed
  const canProceed = await checkAndSkipApproval();
  
  if (canProceed) {
    // Skip approval, go directly to position creation
    console.log('🎯 Skipping approval - creating position directly');
    await createPosition();
  } else {
    // Approval is in progress, wait for it to complete
    console.log('⏳ Waiting for approval to complete...');
  }
};
