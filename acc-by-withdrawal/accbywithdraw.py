import requests
import csv
import json
from collections import defaultdict
from decimal import Decimal, getcontext
from json import JSONEncoder

# Set the precision for Decimal operations
getcontext().prec = 28  # Adjust as needed for your requirements

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return format(obj, '.18f')  # Ensure Decimal objects are formatted correctly
        return JSONEncoder.default(self, obj)

# Validator API endpoint
validators_url = "https://sp-api.dappnode.io/memory/validators"
# Fees info API endpoint
feesinfo_url = "https://sp-api.dappnode.io//memory/feesinfo"

# Conversion factor from wei to ether as a Decimal
WEI_TO_ETH = Decimal('10') ** 18

# Make requests to the two API endpoints
validators_response = requests.get(validators_url)
feesinfo_response = requests.get(feesinfo_url)

# Check if both requests were successful
if validators_response.status_code == 200 and feesinfo_response.status_code == 200:
    # Parse the JSON responses
    validators_data = validators_response.json()
    feesinfo_data = feesinfo_response.json()

    # Dictionary to accumulate rewards for each withdrawal address (in wei)
    rewards_by_address = defaultdict(Decimal)

    # Allowed beacon statuses
    allowed_statuses = {"active_ongoing", "yellowcard", "redcard"}

    # Sum up accumulated rewards by withdrawal address from the validators endpoint
    for validator in validators_data:
        if validator["beacon_status"] in allowed_statuses:
            withdrawal_address = validator["withdrawal_address"]
            accumulated_rewards_wei = Decimal(validator["accumulated_rewards_wei"])
            rewards_by_address[withdrawal_address] += accumulated_rewards_wei

    # Include the pool fee data
    pool_fee_address = feesinfo_data["pool_fee_address"]
    pool_accumulated_fees = Decimal(feesinfo_data["pool_accumulated_fees"])
    rewards_by_address[pool_fee_address] += pool_accumulated_fees

    # Sort the results by total accumulated rewards in descending order (for CSV)
    sorted_rewards = sorted(rewards_by_address.items(), key=lambda x: x[1], reverse=True)

    # Write the results to a CSV file (in ether)
    with open('accumulated_rewards_eth.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['withdrawaladdress', 'totalaccumulated_eth'])
        for address, total_rewards in sorted_rewards:
            eth_amount = total_rewards / WEI_TO_ETH  # Convert wei to ether
            csvwriter.writerow([address, format(eth_amount, '.18f')])  # Write formatted ether amounts

    # Build the JSON structure with ETH values as numbers, sorted in descending order
    json_data = {
        "symbol": "ETH",
        "addresses": {
            address: total_rewards / WEI_TO_ETH
            for address, total_rewards in sorted_rewards
        }
    }

    # Write the JSON to a file using the custom encoder
    with open('accumulated_rewards_eth.json', 'w') as jsonfile:
        json.dump(json_data, jsonfile, cls=CustomEncoder, indent=2)

    # Save the list of addresses to a text file
    with open('addresses.txt', 'w') as addrfile:
        for address in rewards_by_address.keys():
            addrfile.write(f"{address}\n")

    print("Results written to 'accumulated_rewards_eth.csv', 'accumulated_rewards_eth.json', and 'addresses.txt'")
else:
    print(f"Failed to fetch data. Status codes: validators: {validators_response.status_code}, feesinfo: {feesinfo_response.status_code}")
