import requests
from collections import Counter

# Fetch data from the API
url = "https://sp-api.dappnode.io/memory/validators"
response = requests.get(url)
data = response.json()

# Count all beacon_statuses
beacon_statuses = [item["beacon_status"] for item in data if "beacon_status" in item]
status_counts = Counter(beacon_statuses)

# Filter for 'withdrawal_done' and count withdrawal_address
withdrawal_done_addresses = [
    item["withdrawal_address"]
    for item in data
    if item.get("beacon_status") == "withdrawal_done"
]
top_withdrawals = Counter(withdrawal_done_addresses).most_common(10)

# Write everything to results.txt
with open("results.txt", "w") as f:
    f.write("Unique beacon_status values and their counts:\n\n")
    for status, count in status_counts.items():
        f.write(f"{status}: {count}\n")

    f.write("\nTop 10 withdrawal addresses with 'withdrawal_done' status:\n\n")
    for address, count in top_withdrawals:
        f.write(f"{address}: {count}\n")

print("Results saved to results.txt")
