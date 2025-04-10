import requests
import json

def fetch_validators_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        return []

def wei_to_eth(wei_value):
    return wei_value / 1e18

def calculate_total_rewards(validators):
    total_pending_rewards = 0
    total_accumulated_rewards = 0
    
    for validator in validators:
        total_pending_rewards += int(validator.get("pending_rewards_wei", 0))
        total_accumulated_rewards += int(validator.get("accumulated_rewards_wei", 0))
    
    return total_pending_rewards, total_accumulated_rewards

def main():
    url = "https://sp-api.dappnode.io/memory/validators"
    validators = fetch_validators_data(url)
    total_pending, total_accumulated = calculate_total_rewards(validators)
    
    total_pending_eth = wei_to_eth(total_pending)
    total_accumulated_eth = wei_to_eth(total_accumulated)
    total_rewards_eth = wei_to_eth(total_pending + total_accumulated)
    
    print(f"Total Pending Rewards (ETH): {total_pending_eth}")
    print(f"Total Accumulated Rewards (ETH): {total_accumulated_eth}")
    print(f"Total Rewards (ETH): {total_rewards_eth}")

if __name__ == "__main__":
    main()