# DAIO Reward System

A loyalty system that tracks how long users have held DAIO tokens and calculates rewards based on holding duration. Frontend implementation coming soon. 
-twitter https://x.com/DAIOrganization

## Features

- Track token holding duration for any wallet
- Calculate reward tiers based on holding period
- Support for multiple token accounts per wallet
- Real-time reward tier calculation

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Solana RPC URL (optional):
```
SOLANA_RPC_URL=your_rpc_url_here
```

If no RPC URL is provided, the system will use the public Solana mainnet endpoint.

## Usage

Run the script:
```bash
python daio_reward_system.py
```

Enter a wallet address when prompted to check its token holding duration and reward tier.

## Reward Tiers

- Diamond Tier: 1+ year holding (2.0x multiplier)
- Gold Tier: 6+ months holding (1.5x multiplier)
- Silver Tier: 3+ months holding (1.25x multiplier)
- Bronze Tier: Less than 3 months (1.0x multiplier)

## Technical Details

The system tracks tokens deployed from the address:
`GF6AF7pJZnKNeZvLQ8Jwx7j2uSWSNRZMgan3BCbHbVSr`
