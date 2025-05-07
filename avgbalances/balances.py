import requests

# Constants
URL = "https://sp-api.dappnode.io/memory/validators"
GWEI_IN_ETH = 1e9
EFFECTIVE_BALANCE_THRESHOLD_GWEI = 32 * GWEI_IN_ETH
OUTPUT_FILE = "results.txt"

def fetch_validator_data():
    response = requests.get(URL)
    response.raise_for_status()
    return response.json()

def analyze_validators(validators):
    # Count how many have effective balance > 32 ETH
    more_than_32_count = sum(
        int(v["beacon_effective_balance_gwei"]) > EFFECTIVE_BALANCE_THRESHOLD_GWEI
        for v in validators
    )

    # Sort by effective balance in descending order
    sorted_validators = sorted(
        validators,
        key=lambda v: int(v["beacon_effective_balance_gwei"]),
        reverse=True
    )

    top_10 = sorted_validators[:10]
    return more_than_32_count, top_10

def save_results(more_than_32_count, top_10):
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"Validators with more than 32 ETH effective balance: {more_than_32_count}\n\n")
        f.write("Top 10 Validators by Effective Balance (in ETH):\n")
        for i, v in enumerate(top_10, 1):
            balance_eth = int(v["beacon_effective_balance_gwei"]) / GWEI_IN_ETH
            f.write(f"{i}. Validator Index: {v['validator_index']} - {balance_eth:.4f} ETH\n")

def main():
    validators = fetch_validator_data()
    more_than_32_count, top_10 = analyze_validators(validators)
    save_results(more_than_32_count, top_10)
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
