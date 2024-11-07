import requests
import csv
from collections import defaultdict

# URL to fetch the data
url = "https://sp-api.dappnode.io/memory/validators"

# Step 1: Fetch the data from the API
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    exit(1)

# Step 2: Filter and aggregate data based on criteria
filtered_validators = defaultdict(set)  # Dictionary to store unique validator indices per withdrawal address

# Valid status options
valid_statuses = {"active", "yellowcard", "redcard"}

# Process each validator in the data
for validator in data:
    status = validator.get("status")
    withdrawal_address = validator.get("withdrawal_address")
    validator_index = validator.get("validator_index")
    
    # Filter by status and ensure required fields are present
    if status in valid_statuses and withdrawal_address and validator_index is not None:
        filtered_validators[withdrawal_address].add(validator_index)

# Step 3: Prepare data for CSV output and sort it by unique_validator_count in descending order
csv_data = [
    {"withdrawal_address": withdrawal_address, "unique_validator_count": len(validator_indices)}
    for withdrawal_address, validator_indices in filtered_validators.items()
]

# Sort the data by 'unique_validator_count' in descending order
csv_data.sort(key=lambda x: x["unique_validator_count"], reverse=True)

# Step 4: Save data to CSV
output_filename = "validator_summary.csv"
with open(output_filename, mode='w', newline='') as csv_file:
    fieldnames = ["withdrawal_address", "unique_validator_count"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(csv_data)

print(f"Data has been saved to {output_filename} in descending order.")
