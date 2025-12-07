import matplotlib.pyplot as plt

#1
def plot_average_calories(calorie_dict):
    """
    Input example → {"Vegetarian":2200, "Chicken":1900, "Seafood":2500}
    """

    categories = list(calorie_dict.keys())
    values = list(calorie_dict.values())

    plt.figure(figsize=(8,4))
    bars = plt.bar(categories, values)

    # color variation for creativity
    for i, bar in enumerate(bars):
        bar.set_color(plt.cm.viridis(i / len(bars)))

    plt.title("Average Calories by Meal Category", fontsize=14, weight="bold")
    plt.ylabel("Calories")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()



#2
def plot_recipe_cost(cost_dict):
    """
    Input example → {52771: 36.44, 52833: 27.10, 52945: 64.38}
    """

    ids   = list(cost_dict.keys())
    prices = list(cost_dict.values())

    # convert to labels like "Meal 1", "Meal 2"
    labels = [f"Meal {i+1}" for i in range(len(ids))]

    plt.figure(figsize=(8,4))
    bars = plt.bar(labels, prices, color="lightcoral")

    plt.title("Estimated Grocery Cost Per Recipe", fontsize=14, weight="bold")
    plt.ylabel("Estimated Cost ($)")
    plt.grid(axis="y", alpha=0.4)

    # label bars with values
    for i, price in enumerate(prices):
        plt.text(i, price+0.5, f"${price:.2f}", ha="center")

    plt.tight_layout()
    plt.show()



#3
def plot_healthy_score(score_dict):
    """
    Input example → {52771: 6.5, 52777: 4.5, 52945: 8.0}
    """

    ids = list(score_dict.keys())
    scores = list(score_dict.values())

    labels = [f"Meal {i+1}" for i in range(len(ids))]

    plt.figure(figsize=(8,4))
    bars = plt.bar(labels, scores, color="mediumseagreen")

    plt.title("Healthy & Available Recipe Score", fontsize=14, weight="bold")
    plt.ylabel("Score (Higher = Healthier + More Available)")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    # annotate values on top
    for i, score in enumerate(scores):
        plt.text(i, score+0.3, f"{score:.1f}", ha="center")

    plt.tight_layout()
    plt.show()