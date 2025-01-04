from solana.rpc.api import Client
from datetime import datetime
import os
import time
import schedule
import pytz
from dotenv import load_dotenv
from solders.pubkey import Pubkey
from quantum_ai_utils import QuantumAIUtils

class DAIORewardSystem:
    def __init__(self):
        load_dotenv()
        self.client = Client(os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com'))
        self.deployer_address = Pubkey.from_string("GF6AF7pJZnKNeZvLQ8Jwx7j2uSWSNRZMgan3BCbHbVSr")
        self.pst_timezone = pytz.timezone('America/Los_Angeles')
        self.quantum_ai = QuantumAIUtils()
        
        # Initialize storage for tracking wallets
        self.wallets_to_track = set()

    def add_wallet_to_track(self, wallet_address):
        """Add a wallet address to track"""
        self.wallets_to_track.add(wallet_address)
        print(f"Now tracking wallet: {wallet_address}")

    def remove_wallet_to_track(self, wallet_address):
        """Remove a wallet address from tracking"""
        self.wallets_to_track.discard(wallet_address)
        print(f"Stopped tracking wallet: {wallet_address}")

    def get_token_holding_duration(self, wallet_address):
        """
        Check how long a specific wallet has held tokens from the DAIO system deployer
        
        Args:
            wallet_address (str): The wallet address to check
            
        Returns:
            dict: Information about token holding duration
        """
        try:
            # Get token account info
            token_accounts = self.client.get_token_accounts_by_owner(
                wallet_address,
                {'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'}  # Solana Token Program ID
            )

            if not token_accounts['result']['value']:
                return {"error": "No token accounts found for this wallet"}

            # Get current time
            current_time = datetime.fromisoformat("2025-01-03T17:17:01-08:00")
            
            holding_info = []
            
            for account in token_accounts['result']['value']:
                account_pubkey = account['pubkey']
                
                # Get token mint info
                account_info = self.client.get_account_info(account_pubkey)
                if not account_info['result']['value']:
                    continue

                # Get mint address from token account
                token_data = account_info['result']['value']['data']
                mint_address = token_data['parsed']['info']['mint']

                # Check if this token was deployed by our deployer
                mint_info = self.client.get_account_info(mint_address)
                if not mint_info['result']['value']:
                    continue

                token_creator = mint_info['result']['value']['owner']
                if token_creator != str(self.deployer_address):
                    continue

                # Get account history for valid token
                history = self.client.get_signature_for_address(account_pubkey)
                
                if history['result']:
                    # Get the earliest transaction
                    earliest_tx = history['result'][-1]
                    acquisition_time = datetime.fromtimestamp(earliest_tx['blockTime'])
                    
                    holding_duration = current_time - acquisition_time
                    
                    holding_info.append({
                        'token_account': account_pubkey,
                        'mint_address': mint_address,
                        'holding_duration_days': holding_duration.days,
                        'acquisition_date': acquisition_time.isoformat(),
                    })
            
            return {
                'wallet_address': wallet_address,
                'holdings': holding_info
            }
            
        except Exception as e:
            return {"error": f"Error checking token holding duration: {str(e)}"}

    def calculate_rewards(self, holding_duration_days, wallet_address):
        """
        Calculate rewards based on holding duration with quantum boost
        
        Args:
            holding_duration_days (int): Number of days tokens have been held
            wallet_address (str): The wallet address for quantum seed generation
            
        Returns:
            dict: Reward information
        """
        # Get quantum seed for this wallet
        quantum_seed = self.quantum_ai.generate_quantum_seed(wallet_address)
        
        # Calculate base tier
        if holding_duration_days >= 365:  # 1 year
            tier = "Diamond"
            base_multiplier = 2.0
        elif holding_duration_days >= 180:  # 6 months
            tier = "Gold"
            base_multiplier = 1.5
        elif holding_duration_days >= 90:  # 3 months
            tier = "Silver"
            base_multiplier = 1.25
        else:
            tier = "Bronze"
            base_multiplier = 1.0
            
        # Apply quantum boost
        quantum_boost = self.quantum_ai.quantum_boost_multiplier(holding_duration_days, quantum_seed)
        final_multiplier = base_multiplier * quantum_boost
            
        return {
            "tier": tier,
            "base_multiplier": base_multiplier,
            "quantum_boost": quantum_boost,
            "final_multiplier": final_multiplier,
            "holding_days": holding_duration_days,
            "quantum_seed": quantum_seed
        }

    async def check_all_wallets(self):
        """Check all tracked wallets and print their holding information"""
        print(f"\nRunning scheduled check at {datetime.now(self.pst_timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        if not self.wallets_to_track:
            print("No wallets are currently being tracked.")
            return
            
        for wallet in self.wallets_to_track:
            print(f"\nChecking wallet: {wallet}")
            holding_info = self.get_token_holding_duration(wallet)
            
            if "error" in holding_info:
                print(f"Error: {holding_info['error']}")
                continue
                
            if not holding_info['holdings']:
                print("No tokens from the DAIO deployer found in this wallet.")
                continue
            
            # Get AI analysis of holding pattern
            ai_analysis = await self.quantum_ai.analyze_holding_pattern(holding_info)
            print("\nAI Analysis:", ai_analysis['analysis'])
            print(f"Analysis Quantum Confidence: {ai_analysis['quantum_confidence']:.2%}")
                
            for holding in holding_info['holdings']:
                print(f"\nToken Account: {holding['token_account']}")
                print(f"Mint Address: {holding['mint_address']}")
                print(f"Holding Duration: {holding['holding_duration_days']} days")
                print(f"Acquisition Date: {holding['acquisition_date']}")
                
                rewards = self.calculate_rewards(holding['holding_duration_days'], wallet)
                print(f"Reward Tier: {rewards['tier']}")
                print(f"Base Multiplier: {rewards['base_multiplier']}x")
                print(f"Quantum Boost: {rewards['quantum_boost']:.3f}x")
                print(f"Final Multiplier: {rewards['final_multiplier']:.3f}x")
                print(f"Quantum Seed: {rewards['quantum_seed']}")

def main():
    reward_system = DAIORewardSystem()
    
    # Schedule the check to run every day at 4:21 PM PST
    schedule.every().day.at("16:21").do(reward_system.check_all_wallets)
    
    print("DAIO Reward System Tracker")
    print("Running continuously. Will check wallets every day at 4:21 PM PST")
    print("Available commands:")
    print("1. add <wallet_address> - Start tracking a wallet")
    print("2. remove <wallet_address> - Stop tracking a wallet")
    print("3. list - List all tracked wallets")
    print("4. check - Run an immediate check of all wallets")
    print("5. exit - Exit the program")
    
    while True:
        try:
            # Run pending scheduled tasks
            schedule.run_pending()
            
            # Get user input
            command = input("\nEnter command: ").strip().lower()
            
            if command == "exit":
                break
            elif command.startswith("add "):
                wallet = command[4:].strip()
                reward_system.add_wallet_to_track(wallet)
            elif command.startswith("remove "):
                wallet = command[7:].strip()
                reward_system.remove_wallet_to_track(wallet)
            elif command == "list":
                print("\nTracked wallets:")
                for wallet in reward_system.wallets_to_track:
                    print(wallet)
            elif command == "check":
                reward_system.check_all_wallets()
            else:
                print("Invalid command. Please try again.")
                
            # Sleep briefly to prevent high CPU usage
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
