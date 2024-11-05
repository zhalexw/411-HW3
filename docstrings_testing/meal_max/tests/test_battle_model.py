import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """fixture to provide new instance of BattleModel for each test"""
    return BattleModel()

@pytest.fixture
def sample_combatant1():
    return Meal(1, 'sushi', 'japanese', 3.95, 'MED')

@pytest.fixture
def sample_combatant2():
    return Meal(2, 'pizza', 'italian', 24.95, 'LOW')

@pytest.fixture
def sample_combatant_list(sample_combatant1, sample_combatant2):
    return [sample_combatant1, sample_combatant2]