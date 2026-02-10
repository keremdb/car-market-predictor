import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

def get_listing_urls(model_url="https://bringatrailer.com/honda/s2000/"):
    """
    Fetches the model page and extracts listing URLs.
    """
    print(f"Connecting to {model_url}...")
    response = requests.get(model_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'lxml')
    
    listing_urls = set()
    
    # BaT usually puts listings inside a 'div' with class 'listing-card' or similar.
    # We will look for ANY link that contains '/listing/' to be safe.
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/listing/' in href and 'bringatrailer.com' in href:
            clean_url = href.split('?')[0]
            listing_urls.add(clean_url)
            
    # Convert to list and sort to keep order consistent
    return sorted(list(listing_urls))

def parse_listing(url):
    """
    Extracts data from a SINGLE listing page.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, 'lxml')
        
        # CRITICAL FIX: Initialize dictionary with None to prevent KeyError
        data = {
            'url': url, 
            'title': 'Unknown', 
            'price': None, 
            'sold_date': None,
            'mileage': None
        }
        
        # 1. Title
        title_tag = soup.find('h1', class_='post-title')
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)

        # 2. Price (The tricky part)
        # BaT layout changes. We try multiple places.
        info_bar = soup.find('div', class_='listing-available-info')
        if info_bar:
            # Look for the bold value span
            price_span = info_bar.find('span', class_='info-value')
            if price_span:
                price_text = price_span.get_text(strip=True)
                # Clean "$35,000" -> 35000
                if '$' in price_text:
                    clean_price = price_text.replace('$', '').replace(',', '')
                    if clean_price.isdigit():
                        data['price'] = int(clean_price)
        
        # 3. Features (Mileage, etc.)
        essentials = soup.find('div', class_='essentials')
        if essentials:
            for item in essentials.find_all('li'):
                text = item.get_text(strip=True)
                if 'Mileage' in text:
                    data['mileage'] = text.replace('Mileage:', '').strip()
                # Add other features here if you want

        return data

    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

def main():
    # 1. Get URLs
    all_urls = get_listing_urls("https://bringatrailer.com/honda/s2000/")
    
    # If we still only find 2, we might need to change strategies, 
    # but at least the code won't crash.
    print(f"Found {len(all_urls)} potential car listings.")
    
    # Limit to 5 for testing
    cars_to_scrape = all_urls[:5] 
    
    results = []
    for i, url in enumerate(cars_to_scrape):
        print(f"[{i+1}/{len(cars_to_scrape)}] Processing: {url}")
        car_data = parse_listing(url)
        if car_data:
            print(f"   -> Found: {car_data['title']} | Price: {car_data['price']}")
            results.append(car_data)
        
        time.sleep(2) # Respectful delay

    # 2. Save to CSV (With Safety Check)
    if results:
        df = pd.DataFrame(results)
        
        # SAFETY CHECK: Only drop if the column actually exists
        if 'price' in df.columns:
            # Separate sold vs unsold
            sold_df = df.dropna(subset=['price'])
            print(f"\nSummary: Scraped {len(df)} cars. {len(sold_df)} have prices.")
            
            sold_df.to_csv('s2000_data.csv', index=False)
            print("Saved s2000_data.csv")
        else:
            print("\nWARNING: No prices found in any listings. Check selector logic.")
            # Save whatever we got anyway so you can inspect it
            df.to_csv('s2000_debug.csv', index=False)
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()