"""
fetch_data.py

This script fetches Premier League standings data for multiple seasons from the SportsDB API.
It processes and cleans the data to make it more structured and user-friendly. The cleaned data 
is saved into a JSON file called `data.json`.

The flow of the program is as follows:
1. The `get_seasons()` function retrieves the seasons for which data is needed.
2. The `fetch_data()` function fetches the standings data for each season using the SportsDB API.
3. The `clean_season_data()` function processes and structures the raw data.
4. The cleaned data is saved to `data.json` in a structured format.

This script can be run independently or its main function can be called from another script.

Imports:
    - `requests`: To make HTTP requests to the SportsDB API.
    - `json`: To save the cleaned data to a JSON file.
    - `logging`: To log the progress, success, and errors.
    - `datetime`: To determine the current season.

Functions:
    - `get_seasons()`: Retrieves the last 5 Premier League seasons, considering the current year and month.
    - `fetch_data(seasons)`: Fetches and processes the Premier League data for the provided list of seasons.
    - `clean_season_data(standings_data)`: Cleans and structures the raw standings data into a usable format.
    - `main()`: The main function of the script, which ties everything together by calling the relevant functions.

Usage:
    To run this script and fetch the data for the current seasons, simply run:
    python fetch_pl_data.py

    This will fetch the data, clean it, and save it to `data.json`.
"""

import requests
import logging
import json
import datetime

def parse_int(value, default=0):
    """
    Safely convert a value to an integer.

    This function attempts to convert the input `value` to an integer. 
    If conversion fails due to a `TypeError` or `ValueError`, it logs a warning 
    and returns the specified default value.

    Args:
        value (any): The input value to convert.
        default (int, optional): The fallback value if conversion fails. Defaults to 0.

    Returns:
        int: The converted integer or the default value if conversion fails.
    """

    try:
        return int(value)
    except (TypeError, ValueError) as e:
        logging.warning(f"Failed to convert value '{value}' to int. Returning default ({default}). Error: {e}")
        return default

def clean_season_data(season_data):
    """
    Clean and transforms the season data from the standings.

    This function processes a list of club standings, extracting relevant details and 
    transforming the data into a structured dictionary. If any required value is missing 
    or cannot be parsed into an integer, it logs a warning and uses default values.

    Args:
        season_data (list): A list of dictionaries containing club standings data.

    Returns:
        dict: A dictionary where the keys are club rankings (int) and the values are dictionaries 
              with club data including name, badge URL, points, and other stats.
    """

    season_dict = {}
    for club in season_data:
        try:
            rank = parse_int(club.get("intRank"))
            club_data = {
                "club": club.get("strTeam", "Unknown club"),
                "badge_url": club.get("strBadge"),
                "points": parse_int(club.get("intPoints")),
                "form": club.get("strForm", ""),
                "played": parse_int(club.get("intPlayed")),
                "won": parse_int(club.get("intWin")),
                "drawn": parse_int(club.get("intDraw")),
                "lost": parse_int(club.get("intLoss")),
                "goals for": parse_int(club.get("intGoalsFor")),
                "goals against": parse_int(club.get("intGoalsAgainst"))
            }
            season_dict[rank] = club_data
        except Exception as e:
            logging.warning(f"Error processing club data for {club.get('strTeam', 'Unknown club')}: {e}")
    
    return season_dict

def get_seasons():
    """
    Return a list of the current and nine previous Premier League seasons.

    The Premier League season runs from August to May. This function determines the current 
    season based on the current date and returns the last five seasons in the format "YYYY-YYYY".

    Returns:
        list: A list of strings representing the last ten Premier League seasons.
    """

    now = datetime.datetime.now()
    # Adjust for seasons starting in August
    year = now.year if now.month >= 8 else now.year - 1 
    return [f"{year - i}-{year - i + 1}" for i in range(10)]

def fetch_data(seasons):
    """
    Fetche season data for the Premier League from the SportsDB API and cleans it.

    This function iterates over a list of season years, fetches the standings data from 
    the SportsDB API, and processes it using the `clean_season_data` function. The cleaned 
    data is saved to a local JSON file called "data.json".

    Args:
        seasons (list): A list of season years (e.g., ["2022-23", "2021-22"]).
    """

    BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
    session = requests.Session()

    data = {}
    for season in seasons:
        try:
            standings_url = f"{BASE_URL}/lookuptable.php?l=4328&s={season}"
            logging.info(f"Fetching data for season {season} from {standings_url}")
            standings_response = session.get(standings_url)
            standings_response.raise_for_status()  # Raise error for invalid responses
            raw_data = standings_response.json().get("table", [])

            if raw_data:
                season_data = clean_season_data(raw_data)
                data[season] = season_data
                logging.info(f"Successfully fetched and cleaned data for season {season}")
            else:
                logging.warning(f"No data found for season {season}.")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data for season {season}: {e}")
        except Exception as e:
            logging.error(f"Error processing season {season}: {e}")
    
    session.close()

    try:
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)
        logging.info("Data successfully saved to 'data.json'.")
    except Exception as e:
        logging.error(f"Error saving data to 'data.json': {e}")

def main():
    """
    Main function to fetch and clean the Premier League season data.

    This function retrieves the list of seasons using `get_seasons()`, 
    fetches the standings data for each season via `fetch_data()`, and logs the progress.
    """
    try:
        logging.info("Starting the data fetching process.")
        
        seasons = get_seasons()
        logging.info(f"Seasons retrieved: {seasons}")

        fetch_data(seasons)
        
        logging.info("Data fetching and processing complete.")
    
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
