from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def debug_page_structure():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://bringatrailer.com/honda/s2000/"
    print(f"DEBUG: Opening {url}...")
    driver.get(url)
    time.sleep(5) # Let it load
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    # 1. SEARCH FOR CARDS
    # Let's look for common container names
    print("\n--- SEARCHING FOR CONTAINERS ---")
    potential_classes = ['listing-card', 'auction-item', 'content-main', 'group-item', 'auctions-list']
    
    for cls in potential_classes:
        found = soup.find_all(div=True, class_=cls) # Search vaguely
        if not found:
             # Try finding ANY tag with that class
             found = soup.find_all(class_=cls)
        print(f"Class '{cls}': Found {len(found)} elements.")

    # 2. DUMP FIRST 500 CHARACTERS OF HTML
    # This helps us see if we are being blocked or served a different mobile page
    print("\n--- HTML SNIPPET ---")
    print(soup.prettify()[:500])

if __name__ == "__main__":
    debug_page_structure()