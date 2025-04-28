import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# --- Configurations ---
load_dotenv()
n_simulations = int(os.getenv("NUM_CALLS", "20000"))
validators_my_pool = int(os.getenv("VALIDATORS_MY_POOL", "1350"))
pool_fee = float(os.getenv("POOL_FEE", "0.93"))

os.makedirs("charts", exist_ok=True)

# --- Load Data ---
data = pd.read_csv("block_data.csv")
payments = data["payment"].values
blocks_per_validator_per_year = 2.5
blocks_my_pool = validators_my_pool * blocks_per_validator_per_year
pool_sizes = [1, 10, 100, 300, 500, 1000]

# --- Helper Functions ---
def simulate_pool_rewards(pool_size, payments, blocks_per_validator, n_simulations):
    total_blocks = int(pool_size * blocks_per_validator)
    return np.array([
        np.mean(np.random.choice(payments, total_blocks))
        for _ in range(n_simulations)
    ])

def plot_bar_chart(labels, values, title, ylabel, xlabel, filename, add_line=None):
    plt.figure(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0.3, 0.7, len(values)))
    bars = plt.bar(labels, values, color=colors, edgecolor='black')

    if add_line is not None:
        plt.axhline(add_line, color='red', linestyle='--', linewidth=2, label=f"{add_line*100:.0f}% Line")
        plt.legend()

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.grid(axis='y', alpha=0.3)
    plt.ylim(0, 1 if ylabel == "Probability" else max(values) * 1.15)
    plt.savefig(f"charts/{filename}", dpi=300, bbox_inches='tight')
    plt.close()

def plot_kde(results_dict, my_pool_mean, title, filename, label_suffix="", xlim=(0, 0.10)):
    plt.figure(figsize=(14, 8))
    colors = plt.cm.viridis(np.linspace(0.3, 0.7, len(results_dict)))

    for idx, (pool_size, rewards) in enumerate(results_dict.items()):
        sns.kdeplot(
            rewards, fill=True, bw_adjust=1.2,
            label=f"Pool {pool_size} validators{label_suffix}",
            color=colors[idx], alpha=0.5, clip=xlim
        )

    plt.axvline(my_pool_mean, color='black', linestyle='dashed', linewidth=2, label="My Pool Average")
    plt.title(title)
    plt.xlabel("Reward per Block (ETH)")
    plt.ylabel("Density")
    plt.xlim(xlim)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"charts/{filename}", dpi=300, bbox_inches='tight')
    plt.close()

def plot_cdf(results_dict, my_pool_mean, title, filename, label_suffix="", xlim=(0, 0.10)):
    plt.figure(figsize=(14, 8))
    colors = plt.cm.viridis(np.linspace(0.3, 0.7, len(results_dict)))

    for idx, (pool_size, rewards) in enumerate(results_dict.items()):
        sorted_rewards = np.sort(rewards)
        cdf = np.arange(1, len(sorted_rewards)+1) / len(sorted_rewards)
        plt.plot(np.insert(sorted_rewards, 0, 0), np.insert(cdf, 0, 0),
                 label=f"Pool {pool_size} validators{label_suffix}",
                 color=colors[idx], linewidth=2)

    plt.axvline(my_pool_mean, color='black', linestyle='dashed', linewidth=2, label="My Pool Average")
    plt.title(title)
    plt.xlabel("Reward per Block (ETH)")
    plt.ylabel("Cumulative Probability")
    plt.xlim(xlim)
    plt.ylim(0, 1)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"charts/{filename}", dpi=300, bbox_inches='tight')
    plt.close()

# --- Simulations ---
rewards_my_pool = simulate_pool_rewards(validators_my_pool, payments, blocks_per_validator_per_year, n_simulations)
results = {pool_size: simulate_pool_rewards(pool_size, payments, blocks_per_validator_per_year, n_simulations)
           for pool_size in pool_sizes}

probabilities = {pool_size: np.mean(rewards > rewards_my_pool) for pool_size, rewards in results.items()}

# --- Plots (No Fee) ---
plot_bar_chart(
    labels=[str(p) for p in pool_sizes],
    values=list(probabilities.values()),
    title=f"Probability Other Pools Outperform {validators_my_pool}-Validator Pool",
    ylabel="Probability",
    xlabel="Pool Size (Validators)",
    filename="probability_outperform_no_fee.png",
    add_line=0.5
)
plot_kde(results, np.mean(rewards_my_pool), "Distribution of Average Reward per Block (Zoomed)",
         "kde_rewards_per_block_no_fee.png")
plot_cdf(results, np.mean(rewards_my_pool), "CDF of Average Reward per Block (Zoomed)",
         "cdf_rewards_no_fee.png")

# --- Apply Pool Fee ---
rewards_my_pool_discounted = rewards_my_pool * pool_fee
probabilities_discounted = {pool_size: np.mean(rewards > rewards_my_pool_discounted)
                             for pool_size, rewards in results.items()}

# --- Plots (With Fee) ---
plot_bar_chart(
    labels=[str(p) for p in pool_sizes],
    values=list(probabilities_discounted.values()),
    title=f"Probability Other Pools Outperform {validators_my_pool}-Validator Pool (Fee)",
    ylabel="Probability",
    xlabel="Pool Size (Validators)",
    filename="probability_outperform_fee.png",
    add_line=0.5
)
plot_kde(results, np.mean(rewards_my_pool_discounted),
         "Distribution of Average Reward per Block with Fee (Zoomed)",
         "kde_rewards_per_block_fee.png")
plot_cdf(results, np.mean(rewards_my_pool_discounted),
         "CDF of Average Reward per Block with Fee (Zoomed)",
         "cdf_rewards_fee.png")

# --- Smooth + Small Pool ---
combined_results = {}
for pool_size in pool_sizes:
    total_validators = validators_my_pool + pool_size
    combined_rewards = simulate_pool_rewards(total_validators, payments, blocks_per_validator_per_year, n_simulations)
    combined_results[pool_size] = combined_rewards * pool_fee

probabilities_combined = {pool_size: np.mean(results[pool_size] > combined_rewards)
                           for pool_size, combined_rewards in combined_results.items()}

# --- Plots (Smooth + Small Pool) ---
plot_bar_chart(
    labels=[str(p) for p in pool_sizes],
    values=list(probabilities_combined.values()),
    title=f"Probability Pool Beats (Smooth + Pool with Fee)",
    ylabel="Probability",
    xlabel="Pool Size (Validators)",
    filename="probability_combined_smooth_plus_pool_fee.png",
    add_line=0.5
)
plot_kde(combined_results, np.mean(rewards_my_pool_discounted),
         "Distribution of Average Reward per Block (Smooth + Pool with Fee, Zoomed)",
         "kde_combined_smooth_plus_pool_fee.png", label_suffix=" (Smooth + Fee)")
plot_cdf(combined_results, np.mean(rewards_my_pool_discounted),
         "CDF of Average Reward per Block (Smooth + Pool with Fee, Zoomed)",
         "cdf_combined_smooth_plus_pool_fee.png", label_suffix=" (Smooth + Fee)")

# --- Pie Chart: Rewards by Block Size ---
high = payments[payments >= 1].sum()
medium = payments[(payments >= 0.1) & (payments < 1)].sum()
low = payments[payments < 0.1].sum()

plt.figure(figsize=(8, 8))
plt.pie(
    [high, medium, low],
    labels=['≥1 ETH', '0.1–1 ETH', '0–0.1 ETH'],
    autopct='%1.1f%%',
    startangle=140,
    colors=['#FF6B6B', '#FFD93D', '#6BCB77'],
    wedgeprops={'edgecolor': 'black'}
)
plt.title("Distribution of Total Rewards by Block Size", fontsize=16)
plt.savefig("charts/pie_total_rewards_distribution.png", dpi=300, bbox_inches='tight')
plt.close()

# --- Final Results Printing ---
print("\n--- Probabilities (No Fee) ---")
for pool_size, prob in probabilities.items():
    print(f"Pool with {pool_size} validators beats Smooth: {prob*100:.2f}% chance")

print("\n--- Probabilities (With Fee) ---")
for pool_size, prob in probabilities_discounted.items():
    print(f"Pool with {pool_size} validators beats Smooth (with fee): {prob*100:.2f}% chance")

print("\n--- Probabilities (Pool > Smooth+Pool with Fee) ---")
for pool_size, prob in probabilities_combined.items():
    print(f"Pool with {pool_size} validators beats Smooth+{pool_size} validators (with fee): {prob*100:.2f}% chance")
