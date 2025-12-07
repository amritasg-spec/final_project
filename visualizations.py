import matplotlib.pyplot as plt

# 1. Average Calories Plot
def plot_average_calories(calorie_dict):
    categories = list(calorie_dict.keys())
    values = list(calorie_dict.values())

    fig, ax = plt.subplots(figsize=(10, 4))

    bars = ax.bar(categories, values)

    # color variation for creativity
    for i, bar in enumerate(bars):
        bar.set_color(plt.cm.viridis(i / len(bars)))

    ax.set_title("Average Calories by Meal Category", fontsize=16, weight="bold")
    ax.set_ylabel("Calories")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # rotate category labels if needed
    ax.set_xticklabels(categories, rotation=30, ha="right", fontsize=9)

    plt.tight_layout()
    plt.show()

# 2. Estimated Grocery Cost Plot
def plot_recipe_cost(cost_dict):
    ids    = list(cost_dict.keys())
    prices = list(cost_dict.values())
    labels = [f"Meal {i+1}" for i in range(len(ids))]

    fig, ax = plt.subplots(figsize=(12, 4))

    bars = ax.bar(labels, prices, color="lightcoral")

    ax.set_title("Estimated Grocery Cost Per Recipe", fontsize=16, weight="bold")
    ax.set_ylabel("Estimated Cost ($)")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    # Improve X label readability
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)

    # Label each bar
    for i, price in enumerate(prices):
        ax.text(i, price + (max(prices) * 0.03), f"${price:.2f}",
                ha="center", fontsize=8)

    # Prevent labels touching the top
    ax.set_ylim(0, max(prices) * 1.15)

    plt.tight_layout()
    plt.show()

# 3. Healthy Score Plot
def plot_healthy_score(score_dict):
    ids    = list(score_dict.keys())
    scores = list(score_dict.values())
    labels = [f"Meal {i+1}" for i in range(len(ids))]

    fig, ax = plt.subplots(figsize=(12, 4))

    bars = ax.bar(labels, scores, color="mediumseagreen")

    ax.set_title("Healthy & Available Recipe Score", fontsize=16, weight="bold")
    ax.set_ylabel("Score (Higher = Healthier + More Available)")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    # Improve X label readability
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)

    # annotate values on top
    for i, score in enumerate(scores):
        ax.text(i, score + 0.05, f"{score:.1f}",
                ha="center", fontsize=8)

    ax.set_ylim(0, max(scores) * 1.15)

    plt.tight_layout()
    plt.show()
