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

#Unit tests for prep combatant
def test_prep_combatant(battle_model, sample_combatant1):
    """tests adding a meal to combatant list"""
    battle_model.prep_combatant(sample_combatant1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'sushi'

def test_prep_combatant_full(battle_model, sample_combatant1):
    """test error when combatant list full"""
    battle_model.combatants.extend(sample_combatant_list)
    assert len(battle_model.combatants) == 2

    battle_model.prep_combatant(sample_combatant1)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_combatant1)


#Unit tests for get combatants
def test_get_combatants(battle_model):
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
    assert battle_model.get_battle_score(sample_combatant1) == ans


#Unit tests for clear combatants
def test_clear_combatants(battle_model):
    """tests clearing combatant list"""
    battle_model.combatants.extend(sample_combatant_list)
    assert len(battle_model.combatants) == 2

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0


#Unit tests for battle
def test_battle(battle_model):
    """tests doing battle between two meals"""
    battle_model.combatants.extend(sample_combatant_list)
    assert len(battle_model.combatants) == 2

    winner = battle_model.battle()
    #check one combatant has been removed
    assert len(battle_model.combatants) == 1
    
    #check that winner remains in combatant list
    for i in battle_model.combatants:
        if i != None:
            assert i.meal == winner

def test_battle_not_enough_combatants(battle_model):
    """tests doing battle with not enough combatants"""
    battle_model.combatants.append(sample_combatant1)
    assert len(battle_model.combatants) == 1

    battle_model.battle()
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()
    




