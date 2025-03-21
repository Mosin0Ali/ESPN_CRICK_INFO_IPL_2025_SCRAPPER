from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime

import os
import json
import random
import time
import sys


def saveTable(points_table,image_url,data_folder):
    try:
        pt = []

        for idx, table in enumerate(points_table):
            if isinstance(table, dict):
                temp = {}
                temp['team_id'] = table['teamInfo']['objectId']
                temp['team'] = table['teamInfo']['longName']
                temp['image'] = image_url + table['teamInfo']['imageUrl']
                temp['played'] = table['matchesPlayed']
                temp['won'] = table['matchesWon']
                temp['lost'] = table['matchesLost']
                temp['tied'] = table['matchesTied'] if table['matchesTied'] else 0
                temp['points'] = table['points']
                temp['nrr'] = table['nrr'] if table['nrr'] else 0
                temp['team_slug'] = temp['team'].replace(' ','-')

                team_folder = data_folder +'/'+temp['team_slug']
                os.makedirs(team_folder, exist_ok=True)
                pt.append(temp)
            else:
                print(f"Skipping index {idx}: Expected dict, but got {type(table)}")

        filename = os.path.join(data_folder, "points_table.json")


        with open(filename, "w", encoding="utf-8") as file:
            json.dump(pt, file, indent=4, ensure_ascii=False)
        return pt
    except Exception as e:
        return False


def saveTeamPlayers(driver,team_url,folder_name):

    driver.get(team_url)
    time.sleep(5)

    try:
        script_tag = driver.find_element(By.ID, "__NEXT_DATA__")
        json_data = json.loads(script_tag.get_attribute("innerHTML"))  # Convert text to JSON

        # Extract relevant data
        extracted_data = json_data.get("props", {}).get("appPageProps", {}).get("data", {}).get("data", {}).get("content", {})

        extracted_data = json_data['props']['appPageProps']['data']['data']['content']['recentSquads'][0]['players']

        filename = os.path.join(folder_name)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(extracted_data, file, indent=4, ensure_ascii=False)
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False
    
def saveUnfilteredPlayerData(driver,player_url,save_path):
    try:
        driver.get(player_url)
        time.sleep(random.uniform(5, 12)) 

        script_tag = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__NEXT_DATA__")))
        json_data = json.loads(script_tag.get_attribute("innerHTML"))  # Convert text to JSON

        # Extract relevant data
        extracted_data = json_data.get("props", {}).get("appPageProps", {}).get("data", {}).get("data", {}).get("content", {})

        extracted_data = json_data['props']['appPageProps']['data']

        filename = os.path.join(save_path)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(extracted_data, file, indent=4, ensure_ascii=False)
        
        return True
    except KeyError as e:
        print(f"Key error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    

        return False

def scrapCricbuzzPlayer(driver,link,file_path):

    driver.get(link)
    time.sleep(3)
    try: 
         # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract key-value data
        data = {}
        labels = soup.find_all("div", class_="cb-col cb-col-40 text-bold cb-lst-itm-sm")
        values = soup.find_all("div", class_="cb-col cb-col-60 cb-lst-itm-sm")

        name = soup.find("h1", itemprop="name", class_="cb-font-40").text.strip()

        name = mapEspnCricPlayer(name)

        data['name'] = name

        for label, value in zip(labels, values):
            key = label.text.strip()
            val = value.text.strip()
            if(key == 'Born'):
                data['dob'] = formatDate(val)
            elif(key == 'Batting Style'):
                data['batting_style'] = val
            elif(key == 'Bowling Style'):
                data['bowling_style'] = val
            elif(key == 'Role'):
                data['role'] = val
        data['career_span'] = None
        data['country'] = file_path
        player_id = getPlayerIdFromName(file_path,name)
        data['player_id'] = player_id if player_id else random.randint(0, 4)


        batting_table = driver.find_element(By.CSS_SELECTOR, ".cb-plyr-tbl table")
        batting_rows = batting_table.find_elements(By.TAG_NAME, "tr")
        data['stats'] = {}

        for row in batting_rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 0:
                match_type = cols[0].text.strip()
                if match_type not in data['stats']:
                    data['stats'][match_type] = {}
                stats = {
                    "matches": cols[1].text.strip(),
                    "innings": cols[2].text.strip(),
                    "runs": cols[3].text.strip(),
                    "balls_faced": cols[4].text.strip(),
                    "highest_score": cols[5].text.strip(),
                    "average": cols[6].text.strip(),
                    "strike_rate": cols[7].text.strip(),
                    "notouts": cols[8].text.strip(),
                    "fours": cols[9].text.strip(),
                    "sixes": cols[10].text.strip(),
                    "fifties": cols[11].text.strip(),
                    "hundreds": cols[12].text.strip(),
                    "two-hundreds": cols[13].text.strip(),
                    "catches":'-',
                    "stumpings" : '-'
                }
                data['stats'][match_type]['Batting'] = stats

        # Extract bowling stats
        bowling_table = driver.find_element(By.CSS_SELECTOR, ".cb-plyr-tbl + .cb-plyr-tbl table")

        bowling_rows = bowling_table.find_elements(By.TAG_NAME, "tr")

        for row in bowling_rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 0:
                match_type = cols[0].text.strip()
                if match_type not in data['stats']:
                    data['stats'][match_type] = {}
                stats = {
                    "matches": cols[1].text.strip(),
                    "innings": cols[2].text.strip(),
                    "balls_bowled": cols[3].text.strip(),
                    "runs_conceeded": cols[4].text.strip(),
                    "wickets": cols[5].text.strip(),
                    "average": cols[6].text.strip(),
                    "economy": cols[7].text.strip(),
                    "strike_rate": cols[8].text.strip(),
                    "bbi": cols[9].text.strip(),
                    "best_figure": cols[10].text.strip(),
                    "five_wickets": cols[11].text.strip(),
                    "four_wickets": 0,
                    "ten_wickets": cols[12].text.strip(),
                }
                data['stats'][match_type]['BOWLING'] = stats
        return data
    except KeyError as e:
        print(f"Key error: {e}")

    except Exception as e:
        print(f"Error: {e}")

        return False


def formatDate(date_string):
    date_string_cleaned = date_string.split(' (')[0]
    date_object = datetime.strptime(date_string_cleaned, "%B %d, %Y")
    formatted_date = date_object.strftime("%Y-%m-%d")
    return formatted_date

def getPlayerIdFromName(team_name,player):
    file_path = 'data/team-data/' + team_name + '.json'
    with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)     
            for player_data in data:
                if player_data["player"]["longName"].lower() == player.lower():
                    return player_data["player"]["objectId"]
    return None

def mapEspnCricPlayer(name):
    player_map = {
        'Andre Siddarth C':'C Andre Siddarth',
        'Manvanth Kumar L':'Manvanth Kumar',
        'Ravisrinivasan Sai Kishore':'Sai Kishore',
        'Shahrukh Khan':'M Shahrukh Khan',
        'Varun Chakaravarthy':'Varun Chakravarthy',
        'Akash Maharaj Singh':'Akash Singh',
        'RS Hangargekar':'Rajvardhan Hangargekar',
        'Raj Bawa':'Raj Bawa',
        'Yudhvir Singh Charak':'Yudhvir Singh',
        'Rasikh Dar Salam':'Rasikh Salam',
        'Philip Salt':'Phil Salt',
        'Ajay Jadav Mandal':'Ajay Mandal'
        }
    return player_map.get(name, name)