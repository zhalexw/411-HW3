#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

############################################################
#
# Meal Management
#
############################################################

clear_catalog() {
    echo "Clearing the meals..."
    curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

create_meal() {
    meal=$1
    cuisine=$2
    price=$3
    difficulty=$4
    
    echo "Adding meal ($meal - $cuisine, $price) to kitchen..."
    curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'

    if [ $? -eq 0 ]; then
        echo "Meal added successfully."
    else
        echo "Failed to add meal."
        exit 1
    fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  name=$1

  echo "Getting meal by name (Name: '$name')..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$name")
  echo $response
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (name $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name."
    exit 1
  fi
}


############################################################
#
# Battle Management
#
############################################################

battle() {
    echo "Two meals enter, one meal leaves"
    curl -s -X GET "$BASE_URL/battle" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Initiated battle successfully"
    else
        echo "Failed to initiate battle"
        exit 1
    fi
}

clear_combatants() {
  echo "Clearing all combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

prep_combatant() {
  meal=$1

  echo "Preparing meal: $meal"
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}")
  echo $response
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal prepped for battle successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to prep meal for battle."
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

get_leaderboard() {
  echo "Getting leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by wins):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal leaderboard."
    exit 1
  fi
}


check_health
check_db

clear_catalog

create_meal "vindaloo" "indian" 20.0 "HIGH"
create_meal "fried_rice" "asian" 7.5 "LOW"
create_meal "pasta" "italian" 30.0 "MED"

get_meal_by_name "pasta"

clear_combatants

prep_combatant "vindaloo"
prep_combatant "fried_rice"

battle

get_meal_by_id 1

delete_meal_by_id 1

get_leaderboard