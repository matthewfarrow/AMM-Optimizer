#!/bin/bash

# Setup script for AMM Optimizer

echo "Setting up AMM Optimizer..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p data

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
else
    echo ".env file already exists"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your private key and RPC URL"
echo "2. Edit config/pools.yaml with actual pool addresses"
echo "3. Update src/dex/blackhole.py with actual Blackhole DEX ABIs"
echo "4. Run examples: python scripts/examples.py"
echo "5. Run optimizer: python scripts/run_optimizer.py --pool AVAX-USDC --capital 1000"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
