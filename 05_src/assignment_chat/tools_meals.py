from langchain.tools import tool
import json
import requests
from utils.logger import get_logger

_logs = get_logger(__name__)

@tool
def get_recipe_by_ingredient(ingredient: str) -> str:
    """
    Finds a recipe based on an available ingredient using TheMealDB API.
    First search for meals containing the ingredient, then retrieve
    the full recipe details for the first matching meal.
    
    Args:
        ingredient: A food ingredient (e.g., "chicken", "beef", "rice")
    
    Returns:
        A formatted recipe with ingredients and instructions, or an error message
    """
    _logs.debug(f'Getting a recipe for ingredient: {ingredient}')
    
    # Step 1: Search for recipes containing this ingredient
    meal_id = search_recipes_by_ingredient(ingredient)
    
    if not meal_id:
        return f"No recipes found containing {ingredient}. Please try a different ingredient."
    
    # Step 2: Get full recipe details using the meal ID
    recipe = get_full_recipe_details(meal_id)
    
    _logs.debug(f'Successfully retrieved recipe')
    return recipe


def search_recipes_by_ingredient(ingredient: str) -> str:
    """
    Searche for recipes containing the specified ingredient and returns
    the ID of the first matching meal.
    """
    url = "https://www.themealdb.com/api/json/v1/1/filter.php"
    params = {
        "i": ingredient
    }
    
    try:
        _logs.debug(f'Searching for recipes with ingredient: {ingredient}')
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        resp_dict = json.loads(response.text)
        meals = resp_dict.get("meals")
        
        if not meals or meals is None:
            _logs.warning(f"No meals found for ingredient: {ingredient}")
            return None
        
        # Get the first meal from the results
        first_meal = meals[0]
        meal_id = first_meal.get("idMeal")
        meal_name = first_meal.get("strMeal")
        
        _logs.debug(f"Found {len(meals)} recipes. Selected first: {meal_name} (ID: {meal_id})")
        return meal_id
        
    except requests.exceptions.RequestException as e:
        _logs.error(f"API request error for ingredient {ingredient}: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        _logs.error(f"Error parsing response for ingredient {ingredient}: {e}")
        return None
    except Exception as e:
        _logs.error(f"Unexpected error searching for ingredient {ingredient}: {e}")
        return None


def get_full_recipe_details(meal_id: str) -> str:
    """
    Retrieves full recipe details for a specific meal ID and formats
    them into a readable recipe.
    """
    url = "https://www.themealdb.com/api/json/v1/1/lookup.php"
    params = {
        "i": meal_id
    }
    
    try:
        _logs.debug(f'Fetching full recipe details for meal ID: {meal_id}')
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        resp_dict = json.loads(response.text)
        meals = resp_dict.get("meals")
        
        if not meals or len(meals) == 0:
            _logs.error(f"No recipe details found for meal ID: {meal_id}")
            return "Recipe details not found."
        
        meal = meals[0]
        
        # Extract recipe information
        recipe_name = meal.get("strMeal", "Unknown Recipe")
        category = meal.get("strCategory", "Not specified")
        cuisine = meal.get("strArea", "Not specified")
        instructions = meal.get("strInstructions", "No instructions available.")
        youtube_link = meal.get("strYoutube", "")
        thumbnail = meal.get("strMealThumb", "")
        
        # Extract and format ingredients with measurements
        ingredients_list = []
        for i in range(1, 21):  # MealDB has up to 20 ingredients
            ingredient_key = f"strIngredient{i}"
            measure_key = f"strMeasure{i}"
            
            ingredient = meal.get(ingredient_key, "")
            measure = meal.get(measure_key, "")
            
            # Clean up the values and check if ingredient exists
            if ingredient and ingredient.strip():
                ingredient = ingredient.strip()
                measure = measure.strip() if measure else ""
                if measure:
                    ingredients_list.append(f"  • {measure} {ingredient}")
                else:
                    ingredients_list.append(f"  • {ingredient}")
        
        # Format the complete recipe
        recipe = f"""
***{recipe_name}***
{'=' * 60}

Category: {category}
Cuisine: {cuisine}

**INGREDIENTS:**
{chr(10).join(ingredients_list)}

**INSTRUCTIONS:**
{instructions}
"""
        
        # Add YouTube link if available
        #if youtube_link:
        #   recipe += f"\n📺 Video Tutorial: {youtube_link}"
        
        #recipe += "\n\n🔗 Source: TheMealDB"
        
        _logs.debug(f'Successfully formatted recipe: {recipe_name}')
        return recipe
        
    except requests.exceptions.RequestException as e:
        _logs.error(f"API request error for meal ID {meal_id}: {e}")
        return f"Error retrieving recipe details: Network error"
    except (KeyError, json.JSONDecodeError) as e:
        _logs.error(f"Error parsing recipe details for meal ID {meal_id}: {e}")
        return f"Error parsing recipe details"
    except Exception as e:
        _logs.error(f"Unexpected error getting recipe for meal ID {meal_id}: {e}")
        return f"Unexpected error retrieving recipe: {str(e)}"