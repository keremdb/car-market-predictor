from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def inspect_one_card():
    # Setup Headless Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://bringatrailer.com/honda/s2000/"
    print(f"Opening {url}...")
    driver.get(url)
    
    # Wait for the "meat" to load
    time.sleep(5)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    # Grab the FIRST card we find
    card = soup.find('div', class_='listing-card')
    
    if card:
        print("\n--- HTML OF ONE CAR CARD ---")
        print(card.prettify())
        print("\n----------------------------")
    else:
        print("Still couldn't find a 'listing-card'. The site might have changed the container name.")

if __name__ == "__main__":
    inspect_one_card()