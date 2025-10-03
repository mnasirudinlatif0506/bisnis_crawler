import argparse
from datetime import datetime, timezone, timedelta
from crawler.core import get_soup, find_article_urls_from_soup, scrape_article, save_json

# Helper parsing tanggal Indonesia → datetime
def parse_bisnis_date(raw_date: str):
    bulan_map = {
        "Januari": "January", "Februari": "February", "Maret": "March",
        "April": "April", "Mei": "May", "Juni": "June",
        "Juli": "July", "Agustus": "August", "September": "September",
        "Oktober": "October", "November": "November", "Desember": "December"
    }

    for indo, eng in bulan_map.items():
        raw_date = raw_date.replace(indo, eng)

    raw_date = raw_date.replace("WIB", "").strip()

    try:
        dt = datetime.strptime(raw_date, "%d %B %Y, %H:%M")
        wib = timezone(timedelta(hours=7))
        dt = dt.replace(tzinfo=wib)
        return dt
    except Exception:
        return None

def backtrack_crawl(start_date, end_date, output_file):
    base_url = "https://www.bisnis.com"
    soup = get_soup(base_url)
    urls = find_article_urls_from_soup(soup)
    articles = []

    print(f"Memulai scraping dari {base_url}")
    print(f"Filter tanggal: {start_date} s.d {end_date}")
    print("="*40)

    for url in urls:
        try:
            article = scrape_article(url)

            # Parsing tanggal
            pub_date = None
            t = article["tanggal_terbit"]

            try:
                # ISO format
                pub_date = datetime.fromisoformat(t.replace("Z", "+00:00"))
            except Exception:
                # Format Indonesia
                pub_date = parse_bisnis_date(t)

            if not pub_date:
                print(f"Gagal parsing tanggal untuk artikel: {url}")
                continue

            # Filter sesuai range
            if start_date <= pub_date.date() <= end_date:
                articles.append(article)
                print(f"Artikel ditambahkan: {article['judul']} ({pub_date.date()})")
            else:
                print(f"Lewatkan artikel (tanggal {pub_date.date()})")
        except Exception as e:
            print(f"Skip {url} karena error: {e}")
            continue

    save_json(articles, output_file)

    print("="*40)
    print(f"Total artikel diperiksa : {len(urls)}")
    print(f"Artikel sesuai filter   : {len(articles)}")
    print(f"Disimpan ke             : {output_file}")
    print("="*40)
    print("Backtrack selesai.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--output", default="backtrack.json")
    args = parser.parse_args()

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()

    backtrack_crawl(start_date, end_date, args.output)
