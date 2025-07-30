from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def scrape_google_scholar_headless(query, max_results=10):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://scholar.google.com")

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.submit()
    time.sleep(2)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    results = []
    for result in soup.select(".gs_ri")[:max_results]:
        title = result.select_one(".gs_rt").text
        snippet = result.select_one(".gs_rs").text if result.select_one(".gs_rs") else ""
        results.append({"title": title, "snippet": snippet})
    return results
