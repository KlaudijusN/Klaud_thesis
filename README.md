# Klaudijus_Thesis
This repository contains:
- Data acquisition code used for API and web scraping with Selenium for FFF process
- Data of CMM and FFF
- Data analysis of FFF data
- Data analysis of CMM

The data folder contains all the raw data from printing and CMM. CMM folder contains data analysis of CMM data. FFF folder contains two subfolders, data acquisition, and data analysis. The data acquisition folder contains all the code used to acquire the data, where markforged_selenium.py requires additional dependency "login.py" to work. Data analysis are separate for each machine, which contains one file for cleaning of data and second for visualization

# Dependencies
- pandas
- datetime
- sqlite3
- time
- requests
- json
- matplotlib
- seaborn
- webdriver_manager
- selenium

# Selenium requirements
- Chrome browser
- Chromedriver
