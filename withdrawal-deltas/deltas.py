import requests
import csv
from collections import defaultdict
from decimal import Decimal, ROUND_DOWN

# Function to fetch and parse data from the given endpoint
def fetch_data(url):
    response = requests.get(url)
    return response.json()

# Function to convert wei to ETH and round to 4 decimals
def wei_to_eth(wei_value):
    eth_value = Decimal(wei_value) / Decimal(10**18)
    return eth_value.quantize(Decimal('0.0001'), rounding=ROUND_DOWN)  # Round down to 4 decimals

# Fetch data from the two endpoints
proposed_blocks_url = "https://sp-api.dappnode.io/memory/proposedblocks"
validators_url = "https://sp-api.dappnode.io/memory/validators"

proposed_blocks = fetch_data(proposed_blocks_url)
validators = fetch_data(validators_url)

# Initialize dictionaries to store aggregated data by withdrawal address
proposed_blocks_data = defaultdict(lambda: {'reward_sum': Decimal('0'), 'validator_count': 0})
validators_data = defaultdict(lambda: {'accumulated_rewards_sum': Decimal('0'), 'validator_ids': set()})

# Process proposed blocks data
for block in proposed_blocks:
    address = block['withdrawal_address']
    proposed_blocks_data[address]['reward_sum'] += wei_to_eth(block['reward_wei'])  # Convert to ETH

# Process validators data
for validator in validators:
    address = validator['withdrawal_address']
    # Sum both accumulated_rewards_wei and pending_rewards_wei, converting to ETH
    accumulated_rewards_eth = wei_to_eth(validator['accumulated_rewards_wei'])
    pending_rewards_eth = wei_to_eth(validator['pending_rewards_wei'])
    
    validators_data[address]['accumulated_rewards_sum'] += (accumulated_rewards_eth + pending_rewards_eth)
    validators_data[address]['validator_ids'].add(validator['validator_index'])

# Prepare data for CSV output and track delta statistics
output_data = []
positive_delta_count = 0
negative_delta_count = 0
zero_delta_count = 0

for address in set(proposed_blocks_data) | set(validators_data):  # Union of addresses from both datasets
    reward_sum = proposed_blocks_data[address]['reward_sum']
    accumulated_rewards_sum = validators_data[address]['accumulated_rewards_sum']
    validator_count = len(validators_data[address]['validator_ids'])
    delta = accumulated_rewards_sum - reward_sum

    # Round the delta to 4 decimals
    delta = delta.quantize(Decimal('0.0001'), rounding=ROUND_DOWN)

    # Track positive, negative, and zero delta counts
    if delta > 0:
        positive_delta_count += 1
    elif delta < 0:
        negative_delta_count += 1
    else:
        zero_delta_count += 1

    output_data.append({
        'withdrawal_address': address,
        'num_validator_ids': validator_count,
        'accumulated_rewards_sum_eth': accumulated_rewards_sum,  # Store in ETH
        'reward_sum_eth': reward_sum,  # Store in ETH
        'delta_eth': delta  # Store in ETH
    })

# Calculate the statistics
total_withdrawal_keys = len(output_data) - zero_delta_count  # Exclude keys with a delta of 0
positive_delta_percentage = (positive_delta_count / total_withdrawal_keys) * 100 if total_withdrawal_keys > 0 else 0

# Write the results to deltas.csv
with open('deltas.csv', 'w', newline='') as csvfile:
    fieldnames = ['withdrawal_address', 'num_validator_ids', 'accumulated_rewards_sum_eth', 'reward_sum_eth', 'delta_eth']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(output_data)

# Write the statistics to deltas_stats.csv
with open('deltas_stats.csv', 'w', newline='') as statsfile:
    stats_writer = csv.writer(statsfile)
    stats_writer.writerow(['Statistic', 'Value'])
    stats_writer.writerow(['Unique Withdrawal Keys', len(output_data)])
    stats_writer.writerow(['Withdrawal Keys at 0', zero_delta_count])
    stats_writer.writerow(['Withdrawal Keys with Positive Delta', positive_delta_count])
    stats_writer.writerow(['Withdrawal Keys with Negative Delta', negative_delta_count])
    stats_writer.writerow(['% of Positive Delta Withdrawal Keys', f'{positive_delta_percentage:.2f}%'])

# Log the total keys with positive and negative delta
print(f"Total keys with positive delta: {positive_delta_count}")
print(f"Total keys with negative delta: {negative_delta_count}")
print("deltas.csv and deltas_stats.csv files created successfully.")
