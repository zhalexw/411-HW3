import pytest
import re
import sqlite3
from contextlib import contextmanager

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """fixture to provide new instance of BattleModel for each test"""
    return BattleModel()

@pytest.fixture
def mock_random_float(mocker):
    """Mock getting random number for battle"""
    return mocker.patch("meal_max.utils.random_utils.get_random")

@pytest.fixture
def sample_combatant1():
    return Meal(1, 'sushi', 'japanese', 3.95, 'MED')

@pytest.fixture
def sample_combatant2():
    return Meal(2, 'pizza', 'italian', 24.95, 'LOW')

@pytest.fixture
def sample_combatant_list(sample_combatant1, sample_combatant2):
    return [sample_combatant1, sample_combatant2]

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

#Unit tests for prep combatant
def test_prep_combatant(battle_model, sample_combatant1):
    """tests adding a meal to combatant list"""
    battle_model.prep_combatant(sample_combatant1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'sushi'

def test_prep_combatant_full(battle_model, sample_combatant1, sample_combatant_list):
    """test error when combatant list full"""
    battle_model.combatants.extend(sample_combatant_list)
    assert len(battle_model.combatants) == 2

    #battle_model.prep_combatant(sample_combatant1)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_combatant1)


#Unit tests for get combatants
def test_get_combatants(battle_model, sample_combatant_list):
    """tests retrieving combatant list"""
    battle_model.combatants.extend(sample_combatant_list)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == 'sushi'
    assert combatants[1].meal == 'pizza'


#Unit tests for get battle score
def test_get_battle_score(battle_model, sample_combatant1):
    """tests calculating battle score for sushi"""
    ans = 29.6 #3.95*len("japanese")-2
    #24.95*len("italian")-3 = 171.65
    assert battle_model.get_battle_score(sample_combatant1) == ans


#Unit tests for clear combatants
def test_clear_combatants(battle_model, sample_combatant_list):
    """tests clearing combatant list"""
    battle_model.combatants.extend(sample_combatant_list)
    assert len(battle_model.combatants) == 2

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0


#Unit tests for battle
def test_battle(battle_model, mocker, sample_combatant_list):
    """tests doing battle between two meals"""
    battle_model.combatants.extend(sample_combatant_list)
    assert len(battle_model.combatants) == 2

    mocker.patch.object(battle_model, "get_battle_score", side_effect=[29.6, 171.65])
    mock_random = mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.39)
    mock_update_meal_stats = mocker.patch("meal_max.models.battle_model.update_meal_stats")


    assert battle_model.battle() == 'sushi'

    mock_update_meal_stats.assert_any_call(1, 'win')
    mock_update_meal_stats.assert_any_call(2, 'loss')

    #check loser has been removed and winner stays
    assert battle_model.combatants[0].meal == 'sushi'
    assert len(battle_model.combatants) == 1


def test_battle_not_enough_combatants(battle_model, sample_combatant1):
    """tests doing battle with not enough combatants"""
    battle_model.prep_combatant(sample_combatant1)
    assert len(battle_model.combatants) == 1

    #battle_model.battle()
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()
    




