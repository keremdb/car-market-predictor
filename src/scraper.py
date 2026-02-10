import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import csv
import os

# CONFIGURATION
# Pretend to be a real browser to avoid being blocked immediately
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def get_soup(url):
    """
    Fetches the URL and returns a BeautifulSoup object.
    Includes error handling for network issues.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # Raise error for 404/500 codes
        return BeautifulSoup(response.content, 'lxml')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_listing(url):
    """
    Extracts data from a SINGLE Bring a Trailer sold listing.
    """
    soup = get_soup(url)
    if not soup:
        return None

    data = {'url': url}
    
    # 1. EXTRACT TITLE
    try:
        data['title'] = soup.find('h1', class_='post-title').get_text(strip=True)
    except AttributeError:
        data['title'] = None

    # 2. EXTRACT SOLD PRICE
    # BaT usually puts the price in a class like "info-value" inside the "listing-available-info" bar
    try:
        # Look for the 'Sold for' text and grab the bold text next to it
        info_bar = soup.find('div', class_='listing-available-info')
        if info_bar:
            price_text = info_bar.find('span', class_='info-value').get_text(strip=True)
            # Clean string: "$35,000" -> 35000
            data['price'] = int(price_text.replace('$', '').replace(',', ''))
        else:
            data['price'] = None
    except (AttributeError, ValueError):
        data['price'] = None

    # 3. EXTRACT "BaT ESSENTIALS" (The rich feature data)
    # These are usually in a <ul> list inside a div class "essentials"
    essentials = soup.find('div', class_='essentials')
    if essentials:
        items = essentials.find_all('li')
        for item in items:
            text = item.get_text(strip=True)
            # Text looks like: "Transmission: 6-Speed Manual"
            if ':' in text:
                key, value = text.split(':', 1)
                data[key.strip()] = value.strip()

    return data

def main():
    # TEST LIST: 3 actual sold listings (S2000s) to verify the code works
    # In Week 2, you will replace this with a loop that generates these URLs automatically
    test_urls = [
        "https://bringatrailer.com/listing/2004-honda-s2000-112/",
        "https://bringatrailer.com/listing/2008-honda-s2000-137/",
        "https://bringatrailer.com/listing/2006-honda-s2000-155/"
    ]

    all_cars = []

    print(f"Starting scrape of {len(test_urls)} cars...")

    for url in test_urls:
        print(f"Scraping: {url}...")
        car_data = parse_listing(url)
        
        if car_data:
            all_cars.append(car_data)
            print(f" -> Success! Found: {car_data.get('title', 'Unknown')}")
        
        # POLITE DELAY: Wait 3-6 seconds between requests
        time.sleep(random.uniform(3, 6))

    # SAVE TO CSV
    df = pd.DataFrame(all_cars)
    
    # Simple cleaning for the CSV (Handling missing columns gracefully)
    output_file = 'bat_s2000_data.csv'
    df.to_csv(output_file, index=False)
    print(f"\nDone! Data saved to {output_file}")
    print(df.head())

if __name__ == "__main__":
    main()