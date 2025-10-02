import argparse
import os
import re
import time
import requests
from datetime import datetime
from crawler.core import get_soup, find_article_urls_from_soup, scrape_article, save_json

# website
SEED_URLS = ["https://bisnis.com"]

def backtrack_crawl(start_date, end_date, output_file, max_pages=2, delay=1.0):
    """Crawl artikel dari bisnis.com berdasarkan rentang tanggal"""
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"})

    # ubah input string tanggal jadi objek date
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    article_links = set()

    # loop halaman utama (dan pagination jika ada)
    for seed in SEED_URLS:
        print("Mulai scan dari:", seed)
        for page in range(1, max_pages + 1):
            page_url = seed if page == 1 else f"{seed}/page/{page}"
            soup = get_soup(session, page_url)
            time.sleep(delay)

            if not soup:
                continue

            links = find_article_urls_from_soup(soup, base_url=seed)
            for link in links:
                match = re.search(r"/read/(\d{8})/", link)
                if match:
                    tgl = datetime.strptime(match.group(1), "%Y%m%d").date()
                    if start <= tgl <= end:
                        article_links.add(link)

            print(f"  Halaman {page} -> total kandidat sementara: {len(article_links)}")

    print("Total artikel sesuai tanggal:", len(article_links))

    # scraping isi artikel
    hasil = []
    for idx, link in enumerate(sorted(article_links), 1):
        print(f"Scraping {idx}/{len(article_links)}: {link}")
        data = scrape_article(session, link)
        if data:
            hasil.append(data)
        time.sleep(delay)

    # simpan ke JSON
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    save_json(output_file, hasil)
    print("Selesai! Hasil disimpan di:", output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="format: YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="format: YYYY-MM-DD")
    parser.add_argument("--output", default="example_outputs/backtrack.json")
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--rate", type=float, default=1.0)
    args = parser.parse_args()

    backtrack_crawl(
        args.start,
        args.end,
        args.output,
        max_pages=args.max_pages,
        delay=args.rate
    )
