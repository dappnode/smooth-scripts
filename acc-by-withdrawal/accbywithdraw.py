import requests
import csv
import json
from collections import defaultdict

# Validator API endpoint
validators_url = "http://65.109.102.216/memory/validators"
# Fees info API endpoint
feesinfo_url = "http://65.109.102.216/memory/feesinfo"

# Conversion factor from wei to ether
WEI_TO_ETH = 10**18

# Make requests to the two API endpoints
validators_response = requests.get(validators_url)
feesinfo_response = requests.get(feesinfo_url)

# Check if both requests were successful
if validators_response.status_code == 200 and feesinfo_response.status_code == 200:
    # Parse the JSON responses
    validators_data = validators_response.json()
    feesinfo_data = feesinfo_response.json()

    # Dictionary to accumulate rewards for each withdrawal address (in wei)
    rewards_by_address = defaultdict(int)

    # Sum up accumulated rewards by withdrawal address from the validators endpoint
    for validator in validators_data:
        withdrawal_address = validator["withdrawal_address"]
        accumulated_rewards_wei = int(validator["accumulated_rewards_wei"])
        rewards_by_address[withdrawal_address] += accumulated_rewards_wei

    # Include the pool fee data
    pool_fee_address = feesinfo_data["pool_fee_address"]
    pool_accumulated_fees = int(feesinfo_data["pool_accumulated_fees"])
    rewards_by_address[pool_fee_address] += pool_accumulated_fees

    # Sort the results by total accumulated rewards in descending order (for CSV)
    sorted_rewards = sorted(rewards_by_address.items(), key=lambda x: x[1], reverse=True)

    # Write the results to a CSV file (in wei)
    with open('accumulated_rewards_wei.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['withdrawaladdress', 'totalaccumulated_wei'])
        for address, total_rewards in sorted_rewards:
            csvwriter.writerow([address, total_rewards])

    # Build the JSON structure with ETH values as numbers, sorted in descending order
    json_data = {
        "symbol": "ETH",
        "addresses": {
            address: round(total_rewards / WEI_TO_ETH, 18)  # Convert to ETH and round to 18 decimals
            for address, total_rewards in sorted_rewards  # Use sorted rewards for order
        }
    }

    # Write the JSON to a file
    with open('accumulated_rewards_eth.json', 'w') as jsonfile:
        json.dump(json_data, jsonfile, indent=2)

    # Save the list of addresses to a text file
    with open('addresses.txt', 'w') as addrfile:
        for address in rewards_by_address.keys():
            addrfile.write(f"{address}\n")  # Write each address on a new line

    print("Results written to 'accumulated_rewards_wei.csv', 'accumulated_rewards_eth.json', and 'addresses.txt'")
else:
    print(f"Failed to fetch data. Status codes: validators: {validators_response.status_code}, feesinfo: {feesinfo_response.status_code}")
