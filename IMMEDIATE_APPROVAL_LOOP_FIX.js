// IMMEDIATE FIX FOR APPROVAL LOOP
// Add this to StrategyConfig.tsx to break the approval loop

const handleSubmit = async () => {
  console.log('🚀 Starting position creation process...');
  
  if (!address || !volatilityData?.current_price) {
    console.error('❌ Missing required data');
    toast.error('Missing required data');
    return;
  }

  try {
    setLoading(true);
    
    // Calculate amounts with correct decimals
    const amount0BigInt = parseUnits(amount0, token0Symbol === 'USDC' ? 6 : 18);
    const amount1BigInt = parseUnits(amount1, token1Symbol === 'USDC' ? 6 : 18);
    
    console.log('🔍 Approval check:', {
      token0Symbol,
      token1Symbol,
      token0Allowance: token0Allowance?.toString(),
      token1Allowance: token1Allowance?.toString(),
      amount0BigInt: amount0BigInt.toString(),
      amount1BigInt: amount1BigInt.toString()
    });
    
    // CRITICAL FIX: Check if allowances are sufficient
    const needsToken0Approval = !token0Allowance || token0Allowance < amount0BigInt;
    const needsToken1Approval = !token1Allowance || token1Allowance < amount1BigInt;
    
    console.log('📋 Approval needed:', {
      needsToken0Approval,
      needsToken1Approval
    });
    
    // BREAK THE LOOP: If no approval needed, go directly to position creation
    if (!needsToken0Approval && !needsToken1Approval) {
      console.log('✅ No approval needed - proceeding directly to position creation');
      setCurrentStep('Creating Position');
      toast.info('Creating position...');
      await createPosition();
      return;
    }
    
    // Only approve if actually needed
    if (needsToken0Approval) {
      console.log('⚠️  Token0 approval needed');
      setCurrentStep(`Approving ${token0Symbol}`);
      toast.info(`Approving ${token0Symbol}...`);
      await approveToken(finalToken0Address, amount0BigInt);
      return; // Wait for approval
    }
    
    if (needsToken1Approval) {
      console.log('⚠️  Token1 approval needed');
      setCurrentStep(`Approving ${token1Symbol}`);
      toast.info(`Approving ${token1Symbol}...`);
      await approveToken(finalToken1Address, amount1BigInt);
      return; // Wait for approval
    }
    
  } catch (error) {
    console.error('Error in handleSubmit:', error);
    toast.error('Failed to create position');
  } finally {
    setLoading(false);
  }
};
