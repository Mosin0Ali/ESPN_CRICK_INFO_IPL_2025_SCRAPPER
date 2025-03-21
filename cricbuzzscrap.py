from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
import os 
import functions
import time
import random

teams = {
            'Chennai-Super-Kings':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56913',
            'Rajasthan-Royals':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56917',
            'Delhi-Capitals':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56933',
            'Gujarat-Titans':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56957',
            'Kolkata-Knight-Riders':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56921',
            'Lucknow-Super-Giants':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56965',
            'Mumbai-Indians':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56949',
            'Punjab-Kings':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56941',
            'Royal-Challengers-Bengaluru':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56929',
            'Sunrisers-Hyderabad':'https://www.cricbuzz.com/cricket-series/squads/9237/players/56925'

        }

data_folder = "data"

options = webdriver.ChromeOptions()
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=options)

try:

    for filePath,url in teams.items():
        driver.get(url)
        time.sleep(3)

        try: 
            a_tags = driver.find_elements(By.TAG_NAME, "a")
            # Extract href attributes
            hrefs = [a.get_attribute("href") for a in a_tags if a.get_attribute("href")]

            for hre in hrefs:
                data = functions.scrapCricbuzzPlayer(driver,hre,filePath)
                if(data):
                    save_path = data_folder + '/' + filePath + '/' + str(data['player_id']) + '.json'
                    filename = os.path.join(save_path)
                    with open(filename, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)
                else:
                    print("Something went worong")   

        except Exception as e:
            print(f"Error: {e}")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()