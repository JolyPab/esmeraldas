from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# Настройки браузера
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Инициализация браузера
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

base_url = "https://www.esmeraldas.gob.ec"
sections = [
    "/index.php/tramites",
    "/index.php/direcciones"
]

all_links = []

for section in sections:
    full_url = base_url + section
    print(f"🔍 Открываем: {full_url}")
    browser.get(full_url)
    time.sleep(4)

    anchors = browser.find_elements(By.XPATH, "//a[@href]")
    for a in anchors:
        href = a.get_attribute("href")
        if href and href.startswith(base_url) and href not in all_links:
            all_links.append(href)

print(f"✅ Найдено {len(all_links)} уникальных ссылок")

with open("esmeraldas_links_scraped.json", "w", encoding="utf-8") as f:
    json.dump(all_links, f, ensure_ascii=False, indent=2)

browser.quit()
print("🚀 Ссылки сохранены в esmeraldas_links_scraped.json")
