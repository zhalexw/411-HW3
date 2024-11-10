from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats,



)

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
def sample_meal3():
    return Meal(3, 'omlette', 'french', 12.1, 'MED')

@pytest.fixture
def sample_meals(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

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


##Create Meal 

def test_create_meal(mock_cursor):
    "Creating a meal"
    create_meal(meal ='steak', cuisine = 'american', price = 33.3, difficulty ='MED')

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ('steak', 'american', 33.3, 'MED')
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_duplicate_meal(mock_cursor):
    """Test error when adding a duplicate meal to the meal list."""
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")
    with pytest.raises(ValueError, match="Meal with name 'steak' already exists"):
        create_meal(meal ='steak', cuisine = 'american', price = 33.3, difficulty ='MED')


def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., not positive price)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -33.3. Price must be a positive number."):
         create_meal(meal ='steak', cuisine = 'american', price = -33.3, difficulty ='MED')

    # Attempt to create a meal with a non-integer/ float price
    with pytest.raises(ValueError, match="Invalid price: invalid. Price must be a positive number."):
        create_meal(meal ='steak', cuisine = 'american', price = 'invalid', difficulty ='MED')

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (e.g., not LOW, MED, HIGH)"""

    # Attempt to create a meal with an invalid difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: EZ. Must be 'LOW', 'MED', or 'HIGH'."):
         create_meal(meal ='steak', cuisine = 'american', price = 33.3, difficulty ="EZ")

  


##Delete Meal 

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from meals by meal ID."""

    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)


 
## Get meal by id

def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, 'steak', 'american', 33.3, 'MED', 0)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, 'steak', 'american', 33.3, 'MED')

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the song is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)


## Get meal by name 

def test_get_meal_by_name(mock_cursor):
    # Simulate that the meal exists (1, 'steak', 'american', 33.3, 'MED')
    mock_cursor.fetchone.return_value = (1, 'steak', 'american', 33.3, 'MED', False)

    # Call the function and check the result
    result = get_meal_by_name("meal")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, 'steak', 'american', 33.3, 'MED')

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ? ")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("meal",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_bad_name(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with name invalid not found"):
        get_meal_by_name("invalid")

##Help with thsi
def test_get_meal_already_deleted(mock_cursor):
    """Test error when trying to get a meal that's already marked as deleted."""



    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = (1, 'steak', 'american', 33.3, 'MED', True)

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with name steak has been deleted"):
        get_meal_by_name("steak")


## update meal stats

def test_update_meal_stats(mock_cursor):
    """Test updating the stats of a meal"""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID
    meal_id = 1
    result = "win"
    update_meal_stats(meal_id, result)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_meal_stats_deleted_id(mock_cursor):
    """Test error when trying to update stats for a deleted meal."""

    # Simulate that the meal exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted song
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

    # Ensure that no SQL query for updating play count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))


def test_update_meal_stats_bad_id(mock_cursor):
    """Test error when trying to update stats for a bad meal id."""
    mock_cursor.fetchone.return_value = None
    # Expect a ValueError when attempting to update a deleted song
    with pytest.raises(ValueError, match="Meal with ID 800 not found"):
        update_meal_stats(800, "win")

def test_update_meal_stats_invalid_result(mock_cursor):
    mock_cursor.fetchone.return_value = ([False])
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(1, 'draw')
    


#Figure out leaderboard
    ##bad sort parameetr 
    #leaderboard

## Help with this 
def test_get_leaderboard(mock_cursor):
    """Test retrieving all meals ordered by wins."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (2, 'salmon', 'norwegian', 27.3, 'LOW',100, 80, 0.8),
        (1, 'steak', 'american', 33.3, 'MED',100,  50, 0.5),
        (3, 'omlette', 'french', 12.1, 'MED',100, 30, 0.3)
    ]

    # Call the get_all_songs function with sort_by_play_count = True
    leaderboard = get_leaderboard()

    # Ensure the results are sorted by play count
    expected_result = [
        {"id": 2, "meal": "salmon", "cuisine": "norwegian", "price": 27.3, "difficulty": "LOW", "battles": 100, "wins": 80, "win_pct":80.0},
        {"id": 1, "meal": "steak", "cuisine": "american", "price": 33.3, "difficulty": "MED", "battles": 100, "wins": 50, "win_pct":50.0},
        {"id": 3, "meal": "omlette", "cuisine": "french", "price": 12.1, "difficulty": "MED", "battles": 100, "wins": 30, "win_pct":30.0}
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

def test_get_leaderboard_sort_by_win_pct(mock_cursor):
    """Test retrieving all meals ordered by wins pct."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (2, 'salmon', 'norwegian', 27.3, 'LOW',100, 80, 0.8),
        (1, 'steak', 'american', 33.3, 'MED',100,  50, 0.5),
        (3, 'omlette', 'french', 12.1, 'MED',100, 30, 0.3)
    ]

    # Call the get_all_songs function with sort_by_play_count = True
    leaderboard = get_leaderboard(sort_by = "win_pct")

    # Ensure the results are sorted by play count
    expected_result = [
        {"id": 2, "meal": "salmon", "cuisine": "norwegian", "price": 27.3, "difficulty": "LOW", "battles": 100, "wins": 80, "win_pct":80.0},
        {"id": 1, "meal": "steak", "cuisine": "american", "price": 33.3, "difficulty": "MED", "battles": 100, "wins": 50, "win_pct":50.0},
        {"id": 3, "meal": "omlette", "cuisine": "french", "price": 12.1, "difficulty": "MED", "battles": 100, "wins": 30, "win_pct":30.0}
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

def test_get_leaderboard_sort_by_badt(mock_cursor):
    """Test retrieving all meals ordered by bad sort by."""

    # Simulate that there are multiple songs in the database
    mock_cursor.fetchall.return_value = [
        (2, 'salmon', 'norwegian', 27.3, 'LOW',100, 80, 0.8),
        (1, 'steak', 'american', 33.3, 'MED',100,  50, 0.5),
        (3, 'omlette', 'french', 12.1, 'MED',100, 30, 0.3)
    ]

    # Call the get_all_songs function with sort_by_play_count = True

    # Ensure the results are sorted by play count
    # expected_result = ("Invalid sort_by parameter: meal")

    # assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"
    with pytest.raises(ValueError, match="Invalid sort_by parameter: meal"):
         get_leaderboard(sort_by = "meal")
