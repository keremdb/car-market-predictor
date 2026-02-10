import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Keep browser open to see the scrolling
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_s2000_data():
    driver = setup_driver()
    
    # TRICK: Use the SEARCH page, not the Model page.
    # The search page lists Sold items more consistently.
    url = "https://bringatrailer.com/search/?s=honda+s2000"
    
    print(f"Opening {url}...")
    driver.get(url)
    time.sleep(5) 
    
    # SCROLLING
    # Search results are infinite. We scroll 15 times to get ~300 cars.
    body = driver.find_element(By.TAG_NAME, 'body')
    for i in range(15):
        print(f"Scrolling... ({i+1}/15)")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2) 
        
    print("Extracting HTML...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return soup

def parse_html(soup):
    print("Parsing HTML...")
    listings = []
    
    # On the Search Page, items are usually in 'div' with class 'search-result'
    # But sometimes they stick to 'listing-card'. We search for BOTH.
    cards = soup.find_all('div', class_='search-result')
    if len(cards) < 5:
        print(" 'search-result' class yielded few results. Trying 'listing-card'...")
        cards = soup.find_all('div', class_='listing-card')
        
    print(f"Found {len(cards)} total cards.")
    
    for card in cards:
        data = {}
        
        # 1. LINK & TITLE
        link_tag = card.find('a', href=True)
        if link_tag:
            data['url'] = link_tag['href']
            # Title is often the text of the link
            data['title'] = link_tag.get_text(strip=True)
        
        # 2. PRICE (The most important part)
        # We look for text that says "Sold for $..." or "Bid to $..."
        # It's usually in a subtitle or meta div
        text_content = card.get_text(" ", strip=True)
        
        # Simple extraction logic: Find the "$" and grab the number
        if "Sold for" in text_content:
            try:
                # Example: "... Sold for $35,000 ..."
                part = text_content.split("Sold for")[-1] # Get everything after "Sold for"
                price_part = part.split("$")[1]           # Get everything after the first "$"
                price_clean = price_part.split(" ")[0]    # Get the number until the next space
                price_clean = price_clean.replace(',', '').replace('.', '')
                
                if price_clean.isdigit():
                    data['price'] = int(price_clean)
                    data['status'] = 'Sold'
            except:
                data['price'] = None
        
        elif "Bid to" in text_content:
            # Active or Unsold auction
            try:
                part = text_content.split("Bid to")[-1]
                price_part = part.split("$")[1]
                price_clean = price_part.split(" ")[0]
                price_clean = price_clean.replace(',', '').replace('.', '')
                if price_clean.isdigit():
                    data['price'] = int(price_clean)
                    data['status'] = 'Bid (Unsold/Live)'
            except:
                data['price'] = None
                
        # 3. MILEAGE (From Title)
        if 'title' in data:
            title = data['title']
            # Look for "24k-Mile" or "12,000-Mile"
            if '-Mile' in title:
                try:
                    mile_str = title.split('-Mile')[0].strip()
                    # Handle "24k"
                    if 'k' in mile_str.lower():
                        num = float(mile_str.lower().replace('k', ''))
                        data['mileage'] = int(num * 1000)
                    else:
                        data['mileage'] = int(mile_str.replace(',', ''))
                except:
                    data['mileage'] = None

        # Only save if we found a price
        if 'price' in data and data['price'] is not None:
            listings.append(data)
            
    return listings

def main():
    soup = get_s2000_data()
    data = parse_html(soup)
    
    if data:
        df = pd.DataFrame(data)
        print(f"\nSuccess! Scraped {len(df)} cars.")
        
        # Filter for only SOLD cars (since we want market value, not failed bids)
        df_sold = df