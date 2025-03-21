# ESPN-CRICKINFO-DATA-SCRAPPER-IPL2025 (CrickBuzz Included) 🏏

A powerful Python-based web scraper that extracts comprehensive cricket data from ESPN Cricinfo & CrickBuzz. Easily collect **team data**, **player profiles**, **player statistics**, and **points tables** for the Indian Premier League 2025.

## Features
- ✅ **Team Data**: Get team details, squad lists, and player information.
- ✅ **Player Profiles**: Extract player bios, career stats, batting & bowling records, and performance history.
- ✅ **Player Stats**: Collect up-to-date match statistics, averages, rankings, and more.
- ✅ **Points Table**: Scrape the latest tournament points tables with net run rates, matches played, wins/losses, etc.
- ✅ **Supports Multiple Formats**: Works with Tests, ODIs, T20Is, and domestic leagues like IPL, BBL, PSL, etc.
- ✅ **Clean JSON Output**: Outputs well-structured JSON data ready for use in apps, dashboards, or analytics.

## Use Cases
- 🏆 Build cricket analytics platforms
- 📊 Power fantasy cricket applications
- 🔍 Historical data analysis
- 📰 Automate content generation for blogs and media

## Tech Stack
- **Python** 🐍
- **Selenium**
- **BeautifulSoup**


## Installation

1. Create a virtual environment:
   ```bash
   python -m venv espncrickinfoscrapper
2. ```bash
   cd espncrickinfoscrapper
3. ```bash
   source bin/activate
4. ```bash
   pip install requirements.txt
5. ```bash
   python PointsTable.py
6. ```bash
   python TeamData.py

# Crickbuzz Scrapping
When running TeamData.py if it fails try running cricbuzzscrap.py which will scrape from crickbuzz and map the data to ESPN's Players so you dont need to worry about data loss. But it has few params like caught and recent stats missing which are present in ESPN so you might need to handle them properly.

# Disclaimer
This project is for educational purposes only. Make sure to respect ESPN Cricinfo’s terms of service and use responsibly.

