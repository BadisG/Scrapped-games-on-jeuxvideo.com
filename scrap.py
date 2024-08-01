import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import sys
import random
import re
import time
from playwright.sync_api import sync_playwright
import os

# Base URLs and headers for HTTP requests
base_url = 'https://www.jeuxvideo.com/tous-les-jeux/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

game_data = []

# Dictionary to convert French month names into numbers
months = {
    'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04', 'mai': '05', 'juin': '06',
    'juillet': '07', 'août': '08', 'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
}

def generate_random_date(year, month=None):
    if month is None:
        month = random.randint(1, 12)
    else:
        month = int(month)

    # Set the last day of the month
    if month in [1, 3, 5, 7, 8, 10, 12]:
        day = random.randint(1, 31)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    elif month == 2:
        if (int(year) % 4 == 0 and int(year) % 100 != 0) or (int(year) % 400 == 0):
            day = random.randint(1, 29)
        else:
            day = random.randint(1, 28)
    return f'{str(month).zfill(2)}/{str(day).zfill(2)}/{year}'

def generate_random_date_in_quarter(year, quarter):
    """Generates a random date in the specified quarter of the year."""
    if quarter == 1:  # 1er trimestre: Janvier, Février, Mars
        month = random.randint(1, 3)
        day = random.randint(1, 31) if month != 2 else random.randint(1, 28)
    elif quarter == 2:  # 2ème trimestre: Avril, Mai, Juin
        month = random.randint(4, 6)
        day = random.randint(1, 30) if month in [4, 6] else random.randint(1, 31)
    elif quarter == 3:  # 3ème trimestre: Juillet, Août, Septembre
        month = random.randint(7, 9)
        day = random.randint(1, 31) if month != 9 else random.randint(1, 30)
    elif quarter == 4:  # 4ème trimestre: Octobre, Novembre, Décembre
        month = random.randint(10, 12)
        day = random.randint(1, 31) if month != 11 else random.randint(1, 30)
    return f"{str(month).zfill(2)}/{str(day).zfill(2)}/{year}"

def generate_random_date_in_semester(year, semester):
    """Generates a random date in the specified semester of the year."""
    if semester == 1:  # 1er semestre: Janvier à Juin
        month = random.randint(1, 6)
    else:  # 2ème semestre: Juillet à Décembre
        month = random.randint(7, 12)
    
    # Set the last day of the month
    if month in [1, 3, 5, 7, 8, 10, 12]:
        day = random.randint(1, 31)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    elif month == 2:
        if (int(year) % 4 == 0 and int(year) % 100 != 0) or (int(year) % 400 == 0):
            day = random.randint(1, 29)
        else:
            day = random.randint(1, 28)
    
    return f"{str(month).zfill(2)}/{str(day).zfill(2)}/{year}"

def convert_date(date_str):
    try:
        # Treatment of quarter cases
        if "trimestre" in date_str:
            parts = date_str.split()
            quarter = int(parts[0][0])  # Récupérer le numéro du trimestre
            year = parts[-1]  # Dernier élément est l'année
            return generate_random_date_in_quarter(year, quarter)


        # Replace “1er” with “1” before dividing
        date_str = date_str.replace('1er', '1')
        parts = date_str.split()

        if "semestre" in date_str:
            parts = date_str.split()
            semester = 1 if "1" in parts[0] else 2
            year = parts[-1]
            return generate_random_date_in_semester(year, semester)        

        if len(parts) == 1:  # Only the year is known
            return generate_random_date(parts[0])

        if len(parts) == 2:  # Month and year are known
            month, year = parts
            month = months[month.lower()]
            return generate_random_date(year, month)

        day, month, year = parts
        month = months[month.lower()]
        return f'{month}/{day.zfill(2)}/{year}'
    except (ValueError, KeyError):
        return date_str  # Return original string if analysis fails

def has_donner_mon_avis(game):
    hub_items = game.find_all('div', class_='hubItem__2vsQLM')
    for item in hub_items:
        if 'Donner mon avis' in item.get_text():
            return True
    return False

def has_disabled_user_rating(game):
    disabled_items = game.find_all('div', class_='hubItem__2vsQLM isDisabled__3yKedx')
    for item in disabled_items:
        if '- -/20' in item.get_text():
            return True
    return False

def get_max_pages():
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('div', class_='pagination__oJAlxz')
    if not pagination:
        print("No pagination found")
        return 1

    # Search for the last span with data-xxx=“true”.
    last_page_span = pagination.find_all('span', {'data-xxx': 'true'})
    if last_page_span:
        last_page = last_page_span[-1].text.strip()
        if last_page.isdigit():
            return int(last_page)

    # If not found, search for all elements with a page number
    page_elements = pagination.find_all(['a', 'span'], class_='page__3yoZnY')
    page_numbers = [int(el.text.strip()) for el in page_elements if el.text.strip().isdigit()]

    if page_numbers:
        return max(page_numbers)

    return 1

def get_game_details(game_url):
    response = requests.get(game_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    user_note = ''
    num_reviews = ''
    console = ''

    # Search for User Rating and console name
    user_container = soup.find('div', class_='gameCharacteristicsMain__reviewContainer gameCharacteristicsMain__reviewContainer--userOpinion')
    if user_container:
        user_gauge = user_container.find('text', class_=lambda x: x and 'gaugeText' in x)
        if user_gauge:
            user_note = user_gauge.text.strip()
            if user_note == '--':
                user_note = ''
            print(f"User Rating: {user_note}")

        # Search for number of Ratings
        count_span = user_container.find('span', class_=lambda x: x and 'count' in x)
        if count_span:
            num_reviews = re.search(r'\((\d+)\)', count_span.text)
            if num_reviews:
                num_reviews = num_reviews.group(1)
                print(f"Number of Ratings: {num_reviews}")

        # Search for console name
        console_span = user_container.find('span', class_='gameCharacteristicsMain__gaugeLabel')
        if console_span:
            console = console_span.text.strip()
            print(f"Console: {console}")

    if not user_note and not num_reviews and not console:
        print("User Rating: None")
        print("Number of Ratings: None")
        print("Console: None")

    return user_note, num_reviews, console


def get_game_urls(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        game_url_elems = page.query_selector_all('a.gameTitleLink__196nPy')
        game_urls = ['https://www.jeuxvideo.com' + elem.get_attribute('href') for elem in game_url_elems]
        browser.close()
    return game_urls

# Get maximum number of pages
max_pages = get_max_pages()

# Ask the user to choose the first and last pages to scrape
start_page = int(input(f"Choose the first page to be scrapped (1 to {max_pages}): "))
end_page = int(input(f"Choose the last page to be scrapped ({start_page} to {max_pages}): "))

if start_page < 1:
    start_page = 1
if end_page > max_pages:
    end_page = max_pages

# Check if the CSV file already exists
csv_filename = 'games.csv'
file_exists = os.path.isfile(csv_filename)

# Try to open the CSV file
while True:
    try:
        # Open the CSV file in append mode if the file already exists, otherwise in write mode.
        with open(csv_filename, 'a' if file_exists else 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write header only if file is opened in write mode
            if not file_exists:
                writer.writerow(['Title', 'User Rating', 'Initial Release Date', 'Console', 'Number of Ratings', 'Page Number'])
        break
    except PermissionError:
        input(f"The file {csv_filename} is open in another application. Please close it and press Enter to try again...")

# Main scraping loop
for page in range(start_page, end_page + 1):
    url = f'{base_url}?p={page}'
    game_urls = get_game_urls(url)
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Ensure the request was successful
    soup = BeautifulSoup(response.content, 'html.parser')
    games = soup.find_all('div', class_='container__3Ow3zD')
    
    page_game_data = []  # Store data for the current page
    
    for index, (game, game_url) in enumerate(zip(games, game_urls), 1):
        title_elem = game.find('h2')
        if title_elem:
            full_title = title_elem.text.strip()
            # Separate title and console
            parts = full_title.split(' sur ')
            title = parts[0].strip()
            console = parts[1].strip() if len(parts) > 1 else ''
        else:
            title = ''
            console = ''
        
        release_date_elem = game.find('span', class_='releaseDate__1RvUmc')
        release_date = release_date_elem.span.text.strip() if release_date_elem and release_date_elem.span else ''
        release_date = convert_date(release_date)
        
        print(f"Found game URL: {game_url}")
        print(f"Title: {title}")
        print(f"Initial Release Date: {release_date}")
        user_note, num_reviews, console = get_game_details(game_url)
        
        page_game_data.append([str(title), user_note, release_date, console, num_reviews, page])
        
        # Skip a line between two games
        print("")

    # Append the data for this page to the CSV file
    while True:
        try:
            with open(csv_filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(page_game_data)
            break
        except PermissionError:
            input(f"The file {csv_filename} is open in another application. Please close it and press Enter to try again...")
    
    total_pages = end_page - start_page + 1
    current_page = page - start_page + 1
    print(f"{current_page} in {total_pages} scrapped pages...")
    print(f"Data for page {page} saved to {csv_filename}")
    print("")

print(f"The Web scrapping process has been successfully completed.")

# Add this line to keep the console open
input("Press Enter to close the console...")
