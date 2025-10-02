import argparse
import os
import json
import time
import requests
from crawler.core import get_soup, find_article_urls_from_soup, scrape_article, save_json

# website
SEED_URLS = ["https://bisnis.com"]

def load_existing(file_path):
    """Cek kalau file output sudah ada, langsung load isinya"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def standard_crawl(output_file, interval=600, max_pages=1, delay=1.0, run_once=False):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"})

    # artikel yang sudah pernah diambil
    articles = load_existing(output_file)
    seen = {a["link"] for a in articles}
    print("Mulai standard mode. Artikel lama sudah ada:", len(seen))

    while True:
        found_links = set()
        for seed in SEED_URLS:
            for page in range(1, max_pages + 1):
                url = seed if page == 1 else f"{seed}/page/{page}"
                soup = get_soup(session, url)
                time.sleep(delay)
                if not soup:
                    continue
                links = find_article_urls_from_soup(soup, base_url=seed)
                found_links.update(links)

        # cari link baru yang belum pernah di-scrape
        new_links = [u for u in sorted(found_links) if u not in seen]
        print(f"Total link ketemu: {len(found_links)} | Baru: {len(new_links)}")

        # scrape artikel baru
        for idx, link in enumerate(new_links, 1):
            print(f"Scraping baru {idx}/{len(new_links)}: {link}")
            art = scrape_article(session, link)
            if art:
                articles.append(art)
                seen.add(link)
            time.sleep(delay)

        # simpan hasil terbaru
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        save_json(output_file, articles)

        if run_once:
            print("Standard mode sekali jalan selesai.")
            break

        print(f"Load {interval} detik sebelum cek lagi...\n")
        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="example_outputs/standard.json")
    parser.add_argument("--interval", type=int, default=600)
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--rate", type=float, default=1.0)
    parser.add_argument("--run-once", action="store_true")
    args = parser.parse_args()

    standard_crawl(
        args.output,
        interval=args.interval,
        max_pages=args.max_pages,
        delay=args.rate,
        run_once=args.run_once
    )
