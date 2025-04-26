import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create 'charts' folder if it doesn't exist
os.makedirs("charts", exist_ok=True)

# Load block data
data = pd.read_csv("block_data.csv")
payments = data["payment"].values

# Pool parameters
validators_my_pool = int(os.getenv("VALIDATORS_MY_POOL", "1350"))
blocks_per_validator_per_year = 2.5
blocks_my_pool = int(validators_my_pool * blocks_per_validator_per_year)

# Simulation settings
pool_sizes = [1, 10, 100, 300, 500, 1000]
n_simulations = 20000

# Function to simulate pool rewards (per block)
def simulate_pool_rewards(pool_size, payments, blocks_per_validator):
    rewards_per_simulation = []
    total_blocks = int(pool_size * blocks_per_validator)

    for _ in range(n_simulations):
        sampled_payments = np.random.choice(payments, total_blocks)
        avg_reward_per_block = np.mean(sampled_payments)
        rewards_per_simulation.append(avg_reward_per_block)

    return np.array(rewards_per_simulation)

# Run simulation for my pool (fixed)
rewards_my_pool = []
for _ in range(n_simulations):
    sampled_payments = np.random.choice(payments, blocks_my_pool)
    avg_reward_per_block = np.mean(sampled_payments)
    rewards_my_pool.append(avg_reward_per_block)
rewards_my_pool = np.array(rewards_my_pool)

# Simulate other pools
results = {}
for pool_size in pool_sizes:
    rewards = simulate_pool_rewards(pool_size, payments, blocks_per_validator_per_year)
    results[pool_size] = rewards

# Calculate probabilities of outperforming
probabilities = {}
for pool_size, rewards in results.items():
    prob = np.mean(rewards > rewards_my_pool)
    probabilities[pool_size] = prob

# --- Plotting ---

# 1. Blocks proposed per year
blocks_proposed = {pool_size: pool_size * blocks_per_validator_per_year for pool_size in pool_sizes}
blocks_proposed[validators_my_pool] = validators_my_pool * blocks_per_validator_per_year

pool_labels_extended = [str(p) for p in pool_sizes] + [f"{validators_my_pool} (Smooth)"]
blocks_values = list(blocks_proposed.values())

plt.figure(figsize=(12, 6))
colors_blocks = plt.cm.viridis(np.linspace(0.3, 0.7, len(blocks_values)))

bars = plt.bar(pool_labels_extended, blocks_values, color=colors_blocks)
for bar, value in zip(bars, blocks_values):
    plt.text(bar.get_x() + bar.get_width()/2, value + 20, f"{value:.1f} blocks",
             ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.title("Blocks Proposed Per Year by Each Pool")
plt.ylabel("Number of Blocks Proposed")
plt.xlabel("Pool Size (Validators)")
plt.grid(axis='y', alpha=0.3)
plt.ylim(0, max(blocks_values) * 1.15)
plt.savefig("charts/blocks_proposed_per_year.png", dpi=300, bbox_inches='tight')
plt.show()

# 2. Distribution of rewards per block (KDE plot, zoomed)
plt.figure(figsize=(14, 8))
colors = plt.cm.viridis(np.linspace(0.3, 0.7, len(pool_sizes)))

for idx, pool_size in enumerate(pool_sizes):
    sns.kdeplot(
        results[pool_size],
        fill=True,
        bw_adjust=1.2,
        label=f"Pool {pool_size} validators",
        color=colors[idx],
        alpha=0.5,
        clip=(0, 0.10)
    )

plt.axvline(np.mean(rewards_my_pool), color='black', linestyle='dashed', linewidth=2,
            label=f"Average Reward per Block ({validators_my_pool}-Validator Pool)")
plt.xlim(0, 0.10)
plt.title("Distribution of Average Reward per Block (Zoomed)")
plt.xlabel("Reward per Block (ETH)")
plt.ylabel("Density")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("charts/kde_rewards_per_block_no_fee.png", dpi=300, bbox_inches='tight')
plt.show()

# 3. Probability another pool beats mine (Bar Chart)
plt.figure(figsize=(10, 6))
pool_labels = [str(p) for p in pool_sizes]
probs = [probabilities[p] for p in pool_sizes]
colors = plt.cm.viridis(np.linspace(0.3, 0.7, len(probs)))

bars = plt.bar(pool_labels, probs, color=colors)
for bar in bars:
    bar.set_edgecolor("black")

plt.axhline(0.5, color='red', linestyle='dashed', linewidth=2, label="50% line")

plt.title(f"Probability of Other Pools Outperforming {validators_my_pool}-Validator Pool")
plt.ylabel("Probability")
plt.xlabel("Pool Size (validators)")
plt.ylim(0, 1)
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.savefig("charts/probability_outperform_no_fee.png", dpi=300, bbox_inches='tight')
plt.show()

# 4. Cumulative distribution (CDF Plot, zoomed)
plt.figure(figsize=(14, 8))

for idx, pool_size in enumerate(pool_sizes):
    sorted_rewards = np.sort(results[pool_size])
    cdf = np.arange(1, len(sorted_rewards)+1) / len(sorted_rewards)
    sorted_rewards = np.insert(sorted_rewards, 0, 0)
    cdf = np.insert(cdf, 0, 0)
    plt.plot(sorted_rewards, cdf, label=f"Pool {pool_size} validators", color=colors[idx], linewidth=2)

plt.axvline(np.mean(rewards_my_pool), color='black', linestyle='dashed', linewidth=2,
            label=f"Average Reward per Block ({validators_my_pool}-Validator Pool)")
plt.xlim(0, 0.10)
plt.ylim(0, 1)
plt.title("Cumulative Distribution Function (CDF) of Average Reward per Block (Zoomed)")
plt.xlabel("Reward per Block (ETH)")
plt.ylabel("Cumulative Probability")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("charts/cdf_rewards_no_fee.png", dpi=300, bbox_inches='tight')
plt.show()

# --- Second round with 7% fee discount ---
rewards_my_pool_discounted = rewards_my_pool * 0.93

# New probabilities
probabilities_discounted = {}
for pool_size, rewards in results.items():
    prob = np.mean(rewards > rewards_my_pool_discounted)
    probabilities_discounted[pool_size] = prob

# 5. Distribution (with 7% fee)
plt.figure(figsize=(14, 8))
for idx, pool_size in enumerate(pool_sizes):
    sns.kdeplot(
        results[pool_size],
        fill=True,
        bw_adjust=1.2,
        label=f"Pool {pool_size} validators",
        color=colors[idx],
        alpha=0.5,
        clip=(0, 0.10)
    )

plt.axvline(np.mean(rewards_my_pool_discounted), color='black', linestyle='dashed', linewidth=2,
            label=f"Average Reward per Block ({validators_my_pool}-Validator Pool, 7% Fee)")
plt.xlim(0, 0.10)
plt.title("Distribution of Average Reward per Block with 7% Fee (Zoomed)")
plt.xlabel("Reward per Block (ETH)")
plt.ylabel("Density")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("charts/kde_rewards_per_block_fee.png", dpi=300, bbox_inches='tight')
plt.show()

# 6. Probability another pool beats mine (7% fee case)
plt.figure(figsize=(10, 6))
probs = [probabilities_discounted[p] for p in pool_sizes]

bars = plt.bar(pool_labels, probs, color=colors)
for bar in bars:
    bar.set_edgecolor("black")

plt.axhline(0.5, color='red', linestyle='dashed', linewidth=2, label="50% line")

plt.title(f"Probability of Other Pools Outperforming {validators_my_pool}-Validator Pool (7% Fee)")
plt.ylabel("Probability")
plt.xlabel("Pool Size (validators)")
plt.ylim(0, 1)
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.savefig("charts/probability_outperform_fee.png", dpi=300, bbox_inches='tight')
plt.show()

# 7. Cumulative distribution (CDF with 7% fee)
plt.figure(figsize=(14, 8))

for idx, pool_size in enumerate(pool_sizes):
    sorted_rewards = np.sort(results[pool_size])
    cdf = np.arange(1, len(sorted_rewards)+1) / len(sorted_rewards)
    sorted_rewards = np.insert(sorted_rewards, 0, 0)
    cdf = np.insert(cdf, 0, 0)
    plt.plot(sorted_rewards, cdf, label=f"Pool {pool_size} validators", color=colors[idx], linewidth=2)

plt.axvline(np.mean(rewards_my_pool_discounted), color='black', linestyle='dashed', linewidth=2,
            label=f"Average Reward per Block ({validators_my_pool}-Validator Pool, 7% Fee)")
plt.xlim(0, 0.10)
plt.ylim(0, 1)
plt.title("CDF of Average Reward per Block with 7% Fee (Zoomed)")
plt.xlabel("Reward per Block (ETH)")
plt.ylabel("Cumulative Probability")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("charts/cdf_rewards_fee.png", dpi=300, bbox_inches='tight')
plt.show()

# Print probabilities
print("\n--- Probabilities (No Fee) ---")
for pool_size, prob in probabilities.items():
    print(f"Pool with {pool_size} validators beats Smooth: {prob*100:.2f}% chance")

print("\n--- Probabilities (With 7% Fee) ---")
for pool_size, prob in probabilities_discounted.items():
    print(f"Pool with {pool_size} validators beats Smooth (with fee): {prob*100:.2f}% chance")
