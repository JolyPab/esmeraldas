from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import json
import time

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--headless")

def parse_page(url):
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    result = None
    try:
        browser.get(url)
        time.sleep(4)

        title = browser.title.strip()

        # Пробуем взять основной контент с <main> или <div class="content">
        try:
            main = browser.find_element(By.TAG_NAME, "main")
            content = main.text.strip()
        except:
            try:
                main = browser.find_element(By.CLASS_NAME, "content")
                content = main.text.strip()
            except:
                content = ""

        result = {
            "url": url,
            "title": title,
            "content": content
        }

    except Exception as e:
        print(f"❌ Ошибка на {url}: {e}")
    finally:
        browser.quit()
        return result

def main():
    with open("esmeraldas_links_scraped.json", "r", encoding="utf-8") as f:
        links = json.load(f)

    parsed = []
    max_workers = 12  # можно увеличить, если у тебя много RAM

    print(f"🚀 Начинаем парсинг {len(links)} страниц с {max_workers} потоками...\n")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(parse_page, url): url for url in links}

        for i, future in enumerate(tqdm(as_completed(futures), total=len(futures))):
            result = future.result()
            if result and result["content"]:
                parsed.append(result)

            if i % 10 == 0 and parsed:
                with open("esmeraldas_parsed.json", "w", encoding="utf-8") as f:
                    json.dump(parsed, f, ensure_ascii=False, indent=2)

    with open("esmeraldas_parsed.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Готово! Спарсено: {len(parsed)} страниц.")

if __name__ == "__main__":
    main()
