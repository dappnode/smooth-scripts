import requests
import json

# Endpoints
VALIDATORS_ENDPOINT = "https://sp-api.dappnode.io/memory/validators"
BEACON_CHAIN_ENDPOINT = "http://localhost:5052/eth/v1/beacon/states/finalized/validators"

# Fetch validators data from the first API call
def fetch_validators():
    response = requests.get(VALIDATORS_ENDPOINT)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

# Call the second API with validator indices
def fetch_validator_statuses(indices):
    payload = {
        "ids": indices,
        "statuses": []  # Empty to get all statuses
    }
    response = requests.post(BEACON_CHAIN_ENDPOINT, json=payload)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

# Save results to a file, create if it doesn't exist, overwrite if it does
def save_results(status_counts, non_active_validators, non_active_with_pending_count, total_pending_wei, max_pending_validator):
    file_path = "validator_results.txt"
    
    # 'w' mode opens the file for writing, creates if not exists, and overwrites if exists
    with open(file_path, "w") as file:
        # Write the count of validators in each status
        file.write("Validator Status Counts:\n")
        for status, count in status_counts.items():
            file.write(f"{status}: {count}\n")
        
        file.write("\nNon-Active Validators Details:\n")
        for validator in non_active_validators:
            file.write(f"Index: {validator['index']}, Pending Rewards: {validator['pending_rewards_wei']}, Status: {validator['status']}\n")
        
        # Write the count and sum of validators not in 'active_ongoing' with non-zero pending rewards
        file.write("\nSummary of Non-Active Validators with Pending Rewards:\n")
        file.write(f"Count of Non-Active Validators with Pending Wei != 0: {non_active_with_pending_count}\n")
        file.write(f"Total Pending Wei for Non-Active Validators: {total_pending_wei}\n")
        
        # Write the validator with the most pending rewards (if any)
        if max_pending_validator:
            file.write("\nValidator with the Most Pending Rewards (Not 'active_ongoing'):\n")
            file.write(f"Index: {max_pending_validator['index']}, Pending Rewards: {max_pending_validator['pending_rewards_wei']}, Status: {max_pending_validator['status']}\n")

def main():
    # Step 1: Fetch validator data
    validators = fetch_validators()

    # Extract indices and prepare a mapping of index to details for later use
    indices = []
    validator_map = {}
    for validator in validators:
        index = validator['validator_index']
        indices.append(str(index))
        validator_map[index] = {
            "pending_rewards_wei": int(validator['pending_rewards_wei']),
            "status": validator['status']
        }

    # Step 2: Fetch statuses of these validators from the second endpoint
    beacon_data = fetch_validator_statuses(indices)
    status_counts = {
        "pending_initialized": 0,
        "pending_queued": 0,
        "active_ongoing": 0,
        "active_exiting": 0,
        "active_slashed": 0,
        "exited_unslashed": 0,
        "exited_slashed": 0,
        "withdrawal_possible": 0,
        "withdrawal_done": 0
    }
    non_active_validators = []

    # Variables to track non-active validators with pending rewards
    non_active_with_pending_count = 0
    total_pending_wei = 0
    max_pending_validator = None

    # Process each validator's status from the response
    for validator in beacon_data['data']:
        index = int(validator['index'])
        status = validator['status']
        pending_rewards_wei = validator_map[index]['pending_rewards_wei']

        # Count the statuses
        if status in status_counts:
            status_counts[status] += 1
        
        # If the status is not 'active_ongoing', save its details
        if status != "active_ongoing":
            non_active_validators.append({
                "index": index,
                "pending_rewards_wei": pending_rewards_wei,
                "status": status
            })
            
            # If the pending rewards are not zero, update count and sum
            if pending_rewards_wei != 0:
                non_active_with_pending_count += 1
                total_pending_wei += pending_rewards_wei
                
                # Check if this is the maximum pending rewards validator so far
                if not max_pending_validator or pending_rewards_wei > max_pending_validator['pending_rewards_wei']:
                    max_pending_validator = {
                        "index": index,
                        "pending_rewards_wei": pending_rewards_wei,
                        "status": status
                    }

    # Step 3: Save the results to a file
    save_results(status_counts, non_active_validators, non_active_with_pending_count, total_pending_wei, max_pending_validator)

if __name__ == "__main__":
    main()
