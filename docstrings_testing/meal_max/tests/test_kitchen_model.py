import pytest 

from meal_max.models.kitchen_model import Meal

@pytest.fixture
def meal():
    return Meal()

@pytest.fixture
def sample_meal1():
    return Meal(1, 'steak', 'american', 33.3, 'MED')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'salmon', 'norwegian', 27.3, 'LOW')

@pytest.fixture
def sample_meals(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]



##Create Meal 

def test_create_meal(meal, sample_meal1):
    "Creating a meal"
    meal.create_meal(sample_meal1)
    assert len(meal.Meal) == 1
    assert meal.Meal[0].meal == "steak"

def test_create_duplicate_meal(meal, sample_meal1):
    """Test error when adding a duplicate meal to the meal list."""
    meal.create_meal(sample_meal1)
    with pytest.raises(ValueError, match="Meal with ID 1 already exists in the Meal List"):
         meal.create_meal(sample_meal1)



##Clear Meal 

def test_clear_meals(meal, sample_meal1):
    "Test clearing entire meals table"

    meal.create_meal(sample_meal1)
    meal.clear_meals()
    assert len(meal.Meal) == 0 , "Meal Table should be empty after clearing"



##Delete Meal 

def test_delete_meal_by_meal_id(meal, sample_meals):
    """Test removing a meal from the meal table by meal_id."""
    meal.Meals.extend(sample_meals)
    assert len(meal.Meals) == 2
    meal.delete_meal(1)
    assert len(meal.Meals) == 1, f"Expected 1 meal, but got {len(meal.Meals)}"
    assert meal.Meals[0].id == 2, "Expected meal with id 2 to remain"

    

## Get Leaderboard not sure

 
## Get meal by id

def test_get_meal_by__id(meal, sample_meal1):
    """Test successfully retrieving a meal from the meal table by meal ID."""
    meal.create_meal(sample_meal1)
    retreived_meal = meal.get_meal_by_id(1)

    assert retreived_meal.id == 1
    assert retreived_meal.meal == 'steak'
    assert retreived_meal.cuisine == 'american'
    assert retreived_meal.price == 33.3
    assert retreived_meal.difficulty == 'MED'



## Get meal by name 

def test_get_meal_by__name(meal, sample_meal1):
    """Test successfully retrieving a meal from the meal table by meal name."""
    meal.create_meal(sample_meal1)
    retreived_meal = meal.get_meal_by_name(1)

    assert retreived_meal.id == 1
    assert retreived_meal.meal == 'steak'
    assert retreived_meal.cuisine == 'american'
    assert retreived_meal.price == 33.3
    assert retreived_meal.difficulty == 'MED'
## update meal stats

#def test_update_meal_stats(meal, sample_meal1) Not sure