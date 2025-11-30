from langchain.tools import tool
from utils.logger import get_logger

_logs = get_logger(__name__)


@tool
def quick_meal_planner(days: int = 3, dietary_preference: str = "no preference") -> str:
    """
    Create a simple dinner plan for a given number of days
    and a dietary preference.

    Parameters
    ----------
    days : int, optional
        Number of days to plan for (default is 3). Values less than 1
        will be reset to 1; values greater than 7 will be capped at 7.
    dietary_preference : str, optional
        Dietary preference for the plan. Supported values:
        - "no preference"
        - "vegetarian"
        - "low-carb"

    Returns
    -------
    str
        A multi-line string describing a simple dinner plan.
    """
    _logs.debug(
        f"quick_meal_planner called with days={days}, "
        f"dietary_preference={dietary_preference!r}"
    )

    # Clamp days to a reasonable range
    if days < 1:
        _logs.warning("Requested days < 1; resetting to 1.")
        days = 1
    if days > 7:
        _logs.warning("Requested days > 7; capping to 7.")
        days = 7

    preference = dietary_preference.strip().lower()

    if preference in ["vegetarian", "veggie"]:
        base_meals = [
            "Veggie stir-fry with tofu and rice",
            "Lentil soup with crusty bread",
            "Roasted vegetables with quinoa",
            "Chickpea curry with rice",
            "Pasta with tomato sauce and grilled vegetables",
        ]
        label = "Vegetarian plan"
    elif preference in ["low-carb", "keto"]:
        base_meals = [
            "Grilled chicken with salad and olive oil",
            "Baked salmon with steamed broccoli",
            "Egg and vegetable omelette",
            "Beef stir-fry with non-starchy vegetables",
            "Turkey lettuce wraps with avocado",
        ]
        label = "Low-carb plan"
    else:
        base_meals = [
            "Roast chicken with potatoes and salad",
            "Spaghetti with meat sauce and mixed greens",
            "Stir-fried beef with rice and vegetables",
            "Baked fish with roasted potatoes and veggies",
            "Homemade chili with bread or rice",
        ]
        label = "Balanced plan"

    plan_lines = [f"{label} for {days} day(s):", ""]

    for day in range(1, days + 1):
        meal = base_meals[(day - 1) % len(base_meals)]
        plan_lines.append(f"Day {day}: {meal}")

    plan_lines.append("")
    plan_lines.append(
        "You can adjust sides, seasonings, and portion sizes based on your taste "
        "and what you already have at home."
    )

    result = "\n".join(plan_lines)
    _logs.debug("quick_meal_planner created the following plan:\n" + result)

    return result
