import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO, filename="sp_api_logs.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

# Function to fetch data from API
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None

# Function to save data to JSON file
def save_to_json(data, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving data to {filename}: {e}")

# Main function
def main():
    # Step 1: Call and store result in a JSON file
    validators_url = "https://sp-api.dappnode.io/memory/validators"
    validators_data = fetch_data(validators_url)
    if validators_data:
        save_to_json(validators_data, "validators.json")
        logging.info("Validators data saved to validators.json")
    else:
        logging.error("Failed to fetch validators data. Exiting.")
        return

    # Step 2: Extract unique validator keys with status "yellowcard", "redcard", or "active"
    validator_keys = set()
    for validator in validators_data:
        if validator["status"] in ["yellowcard", "redcard", "active"]:
            validator_keys.add(validator["validator_key"])

    # Step 3: Fetch registered relays for each validator key
    wrong_fee_validators = set()
    for key in validator_keys:
        relay_url = f"https://sp-api.dappnode.io/registeredrelays/{key}"
        relay_data = fetch_data(relay_url)
        if relay_data:
            if not relay_data.get("correct_fee_relayers"):
                logging.warning(f"{key}: WRONG FEE RECIPIENT")
                wrong_fee_validators.add(key)
            else:
                logging.info(f"{key}: OK")
        else:
            logging.error(f"Failed to fetch relay data for {key}")

        time.sleep(3)  # Wait for 3 seconds between requests

    # Step 4: Save wrong fee validators to JSON file
    save_to_json(list(wrong_fee_validators), "wrong_fee_validators.json")
    logging.info("Wrong fee validators saved to wrong_fee_validators.json")

if __name__ == "__main__":
    main()
