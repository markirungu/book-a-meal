import requests


THEMEALDB_URL = 'https://www.themealdb.com/api/json/v1/1/search.php'


def search_public_recipes(query):
    if not query:
        return []

    response = requests.get(THEMEALDB_URL, params={'s': query}, timeout=8)
    response.raise_for_status()
    data = response.json() or {}
    meals = data.get('meals') or []

    results = []
    for meal in meals[:10]:
        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}')
            measure = meal.get(f'strMeasure{i}')
            if ingredient and ingredient.strip():
                entry = f"{measure.strip()} {ingredient.strip()}" if measure and measure.strip() else ingredient.strip()
                ingredients.append(entry)

        results.append({
            'external_id': meal.get('idMeal'),
            'name': meal.get('strMeal'),
            'description': meal.get('strInstructions', '')[:240],
            'image_url': meal.get('strMealThumb'),
            'ingredients': ingredients,
            'source': 'themealdb',
        })

    return results
