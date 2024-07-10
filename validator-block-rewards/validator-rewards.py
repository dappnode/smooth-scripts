import requests
import os
from web3 import Web3
from dotenv import load_dotenv
import statistics
import csv

def fetch_rewards_data(api_url, slot_bounds, validator_indices, include_indices):
    response = requests.get(api_url)
    if response.status_code != 200:
        raise ValueError("Failed to retrieve data from API")
    
    if include_indices:
        filter_condition = lambda x: int(x['validator_index']) not in validator_indices
    else:
        filter_condition = lambda x: int(x['validator_index']) in validator_indices

    rewards = [
        {
            'slot': entry['slot'],
            'validator_index': entry['validator_index'],
            'reward_eth': Web3.from_wei(int(entry['reward_wei']), 'ether')
        }
        for entry in response.json()
        if slot_bounds[0] <= entry['slot'] < slot_bounds[1] and filter_condition(entry)
    ]
    print(f"Total blocks Proposed: {len(rewards)}")
    return rewards

def calculate_stats(rewards):
    if not rewards:
        print("No valid entries found.")
        return None, None
    reward_values = [entry['reward_eth'] for entry in rewards]
    median_reward = statistics.median(reward_values)
    average_reward = sum(reward_values) / len(reward_values)
    return median_reward, average_reward

def save_rewards_to_csv(rewards, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['slot', 'validator_index', 'reward_eth']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rewards)

def main():
    load_dotenv(override=True)
    print("Start Slot: ", os.getenv("START_SLOT"))
    print("End Slot: ", os.getenv("END_SLOT"))
    print("Reverse: ", os.getenv("REVERSE"))
    print("Validator Index: ", os.getenv("INDEX"))

    api_url = "https://sp-api.dappnode.io/memory/proposedblocks"
    slot_bounds = (int(os.getenv("START_SLOT")), int(os.getenv("END_SLOT")))
    validator_indices = set(map(int, os.getenv("INDEX").split(',')))
    reverse = os.getenv("REVERSE", "False").lower() in ['true', '1', 't', 'y', 'yes']  # default is False

    rewards = fetch_rewards_data(api_url, slot_bounds, validator_indices, reverse)
    if rewards:
        median_reward, average_reward = calculate_stats(rewards)
        print ("Validator Indices lenght: ", len(validator_indices))
        print(f"Median Reward: {median_reward} ETH")
        print(f"Average Reward: {average_reward} ETH")
        save_rewards_to_csv(rewards, 'rewards.csv')
        print("Rewards saved to rewards.csv")
    else:
        print("No valid entries found.")

if __name__ == "__main__":
    main()
