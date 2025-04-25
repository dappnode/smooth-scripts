import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load block data
data = pd.read_csv("block_datacharts.csv")
payments = data["payment"].values

# Pool parameters
validators_my_pool = 1350
blocks_per_validator_per_year = 2.5
blocks_my_pool = int(validators_my_pool * blocks_per_validator_per_year)

# Simulation settings
pool_sizes = [1, 10, 100, 500, 1000]
n_simulations = 10000

# Function to simulate pool rewards (per block)
def simulate_pool_rewards(pool_size, payments, blocks_per_validator):
    rewards_per_simulation = []
    total_blocks = int(pool_size * blocks_per_validator)

    for _ in range(n_simulations):
        sampled_payments = np.random.choice(payments, total_blocks)
        avg_reward_per_block = np.mean(sampled_payments)
        rewards_per_simulation.append(avg_reward_per_block)

    return np.array(rewards_per_simulation)

# Run simulation for smooth (fixed)
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

# Calculate probabilities of outperforming smooth
probabilities = {}
for pool_size, rewards in results.items():
    prob = np.mean(rewards > rewards_my_pool)
    probabilities[pool_size] = prob

# --- Plotting ---

# 1. Distribution of rewards per block (KDE plot, zoomed)
plt.figure(figsize=(14, 8))
colors = plt.cm.plasma(np.linspace(0, 1, len(pool_sizes)))

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

plt.axvline(np.mean(rewards_my_pool), color='black', linestyle='dashed', linewidth=2, label="Smooth Avg Reward per Block")
plt.xlim(0, 0.10)
plt.title("Distribution of Average Reward per Block (Zoomed)")
plt.xlabel("Reward per Block (ETH)")
plt.ylabel("Density")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# 2. Probability another pool beats mine (Bar Chart)
plt.figure(figsize=(10, 6))
pool_labels = [str(p) for p in pool_sizes]
probs = [probabilities[p] for p in pool_sizes]
colors = plt.cm.viridis(np.linspace(0, 1, len(probs)))

bars = plt.bar(pool_labels, probs, color=colors)
for bar in bars:
    bar.set_edgecolor("black")

plt.title("Probability of Other Pools Outperforming Smooth")
plt.ylabel("Probability")
plt.xlabel("Pool Size (validators)")
plt.ylim(0, 1)
plt.grid(axis='y', alpha=0.3)
plt.show()

# 3. Cumulative distribution (CDF Plot, zoomed and starting at (0,0))
plt.figure(figsize=(14, 8))

for idx, pool_size in enumerate(pool_sizes):
    sorted_rewards = np.sort(results[pool_size])
    cdf = np.arange(1, len(sorted_rewards)+1) / len(sorted_rewards)
    
    # Insert (0,0) manually to start cleanly
    sorted_rewards = np.insert(sorted_rewards, 0, 0)
    cdf = np.insert(cdf, 0, 0)

    plt.plot(sorted_rewards, cdf, label=f"Pool {pool_size} validators", color=colors[idx], linewidth=2)

plt.axvline(np.mean(rewards_my_pool), color='black', linestyle='dashed', linewidth=2, label="Smooth Avg Reward per Block")
plt.xlim(0, 0.10)
plt.ylim(0, 1)  # Ensure the Y-axis goes exactly from 0 to 1
plt.title("Cumulative Distribution Function (CDF) of Average Reward per Block (Zoomed)")
plt.xlabel("Reward per Block (ETH)")
plt.ylabel("Cumulative Probability")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()


# Print probabilities
print("\n--- Probabilities ---")
for pool_size, prob in probabilities.items():
    print(f"Pool with {pool_size} validators beats mine: {prob*100:.2f}% chance")