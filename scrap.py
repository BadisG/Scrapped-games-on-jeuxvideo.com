import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import sys

base_url = 'https://www.jeuxvideo.com/tous-les-jeux/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

game_data = []

# Dictionary for converting month names in French to numbers
months = {
    'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04', 'mai': '05', 'juin': '06',
    'juillet': '07', 'août': '08', 'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
}

def convert_date(date_str):
    try:
        # Replace "1er" with "1" before splitting
        date_str = date_str.replace('1er', '1')
        day, month, year = date_str.split()
        month = months[month.lower()]
        return f'{year}-{month}-{day.zfill(2)}'
    except (ValueError, KeyError):
        return ''

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

# Function to get the maximum number of pages
def get_max_pages():
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('div', class_='pagination__oJAlxz')
    if not pagination:
        print("No pagination found")
        return 1
    
    # Look for the last span with data-xxx="true"
    last_page_span = pagination.find_all('span', {'data-xxx': 'true'})
    if last_page_span:
        last_page = last_page_span[-1].text.strip()
        if last_page.isdigit():
            return int(last_page)
    
    # If not found, look for all elements with a page number
    page_elements = pagination.find_all(['a', 'span'], class_='page__3yoZnY')
    page_numbers = [int(el.text.strip()) for el in page_elements if el.text.strip().isdigit()]
    
    if page_numbers:
        return max(page_numbers)
    
    return 1

# Get the maximum number of pages
max_pages = get_max_pages()

# Ask the user to choose the first and last page to scrape
start_page = int(input(f"Choose the first page to be scrapped (1 to {max_pages}): "))
end_page = int(input(f"Choose the last page to be scrapped ({start_page} to {max_pages}): "))

if start_page < 1:
    start_page = 1
if end_page > max_pages:
    end_page = max_pages

for page in range(start_page, end_page + 1):
    url = f'{base_url}?p={page}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Ensure the request was successful
    soup = BeautifulSoup(response.content, 'html.parser')
    games = soup.find_all('div', class_='container__3Ow3zD')

    for index, game in enumerate(games, 1):
        title_elem = game.find('h2')
        title = title_elem.text.strip() if title_elem else ''
        console = ''
        if not has_donner_mon_avis(game):
            if title_elem:
                for em in title_elem.find_all_next('em'):
                    if 'sur ' in em.text:
                        console = em.text.replace('sur ', '')
                        break

        # Remove "sur <console>" from the title
        title = title.split(' sur ')[0]
        user_note_elem = game.find('span', class_='userRating__1y96su')
        user_note = user_note_elem.text.strip() if user_note_elem else ''
        if user_note == 'N/A' or user_note == '- -/20':
            user_note = ''
        elif '/20' in user_note:
            user_note = user_note.replace('/20', '').strip()

        release_date_elem = game.find('span', class_='releaseDate__1RvUmc')
        release_date = release_date_elem.span.text.strip() if release_date_elem and release_date_elem.span else ''
        release_date = convert_date(release_date)

        if has_disabled_user_rating(game):
            console = ''
        game_data.append([title, user_note, release_date, console])
    
    total_pages = end_page - start_page + 1
    current_page = page - start_page + 1
    print(f"\r{current_page} in {total_pages} scrapped pages...", end='')

# Write the data to a CSV file
with open('games.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Title', 'User Note', 'Release Date', 'Console'])
    csvwriter.writerows(game_data)
print("\nData has been written to games.csv")
