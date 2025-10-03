import argparse
import time
from datetime import datetime
from crawler.core import get_soup, find_article_urls_from_soup, scrape_article, save_json
from backtrack_cli import parse_bisnis_date   # pakai helper dari backtrack_cli

def standard_crawl(interval, output_file):
    base_url = "https://www.bisnis.com"
    seen = set()
    articles = []

    print(f"Memulai standard crawl dari {base_url}")
    print(f"Interval scraping: {interval} detik")
    print("="*40)

    while True:
        try:
            soup = get_soup(base_url)
            urls = find_article_urls_from_soup(soup)

            for url in urls:
                if url not in seen:
                    try:
                        article = scrape_article(url)

                        # Parsing tanggal → coba ISO, kalau gagal pakai parser Indo
                        pub_date = None
                        t = article["tanggal_terbit"]

                        try:
                            pub_date = datetime.fromisoformat(t.replace("Z", "+00:00"))
                        except Exception:
                            pub_date = parse_bisnis_date(t)

                        if pub_date:
                            article["tanggal_terbit"] = pub_date.isoformat()

                        articles.append(article)
                        seen.add(url)
                        print(f"Artikel baru: {article['judul']} ({article['tanggal_terbit']})")

                    except Exception as e:
                        print(f"Gagal scrape {url}: {e}")
                        continue

            save_json(articles, output_file)
            print(f"Disimpan {len(articles)} artikel ke {output_file}")
            print("="*40)
            time.sleep(interval)

        except KeyboardInterrupt:
            print("Crawler dihentikan manual.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=300, help="Interval detik antar scraping")
    parser.add_argument("--output", default="standard.json")
    args = parser.parse_args()

    standard_crawl(args.interval, args.output)
