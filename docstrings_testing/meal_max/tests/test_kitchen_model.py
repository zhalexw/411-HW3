import pytest 

from meal_max.models.kitchen_model import KitchenModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def kitchen_model():
    """Fixture to provide a new instance of KitchenModel for each test."""
    return KitchenModel()

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

def test_create_meal(kitchen_model, sample_meal1):
    "Creating a meal"
    kitchen_model.create_meal(sample_meal1)
    assert len(kitchen_model.Meal) == 1
    assert kitchen_model.Meal[0].meal == "steak"

def test_create_duplicate_meal(kitchen_model, sample_meal1):
    """Test error when adding a duplicate meal to the meal list."""
    kitchen_model.create_meal(sample_meal1)
    with pytest.raises(ValueError, match="Meal with ID 1 already exists in the Meal List"):
         kitchen_model.create_meal(sample_meal1)



##Clear Meal 

def test_clear_meals(kitchen_model, sample_meal1):
    "Test clearing entire meals table"

    kitchen_model.create_meal(sample_meal1)
    kitchen_model.clear_meals()
    assert len(kitchen_model.Meal) == 0 , "Meal Table should be empty after clearing"



##Delete Meal 

def test_delete_meal_by_meal_id(kitchen_model, sample_meals):
    """Test removing a meal from the meal table by meal_id."""
    kitchen_model.Meals.extend(sample_meals)
    assert len(kitchen_model.Meals) == 2
    kitchen_model.delete_meal(1)
    assert len(kitchen_model.Meals) == 1, f"Expected 1 meal, but got {len(kitchen_model.Meals)}"
    assert kitchen_model.Meals[0].id == 2, "Expected meal with id 2 to remain"

    

## Get Leaderboard not sure

 
## Get meal by id

def test_get_meal_by__id(kitchen_model, sample_meal1):
    """Test successfully retrieving a meal from the meal table by meal ID."""
    kitchen_model.create_meal(sample_meal1)
    retreived_meal = kitchen_model.get_meal_by_id(1)

    assert retreived_meal.id == 1
    assert retreived_meal.meal == 'steak'
    assert retreived_meal.cuisine == 'american'
    assert retreived_meal.price == 33.3
    assert retreived_meal.difficulty == 'MED'



## Get meal by name 

def test_get_meal_by__name(kitchen_model, sample_meal1):
    """Test successfully retrieving a meal from the meal table by meal name."""
    kitchen_model.create_meal(sample_meal1)
    retreived_meal = kitchen_model.get_meal_by_name(1)

    assert retreived_meal.id == 1
    assert retreived_meal.meal == 'steak'
    assert retreived_meal.cuisine == 'american'
    assert retreived_meal.price == 33.3
    assert retreived_meal.difficulty == 'MED'
## update meal stats

#def test_update_meal_stats(kitchen_model, sample_meal1) Not sure