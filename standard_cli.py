import argparse
import time
from crawler.core import get_soup, find_article_urls_from_soup, scrape_article, save_json

def standard_crawl(interval, output_file):
    base_url = "https://www.bisnis.com"
    seen = set()
    articles = []
    while True:
        try:
            soup = get_soup(base_url)
            urls = find_article_urls_from_soup(soup)
            for url in urls:
                if url not in seen:
                    try:
                        article = scrape_article(url)
                        articles.append(article)
                        seen.add(url)
                        print(f"Artikel baru: {article['judul']}")
                    except Exception as e:
                        print(f"Gagal scrape {url}: {e}")
                        continue
            save_json(articles, output_file)
            print(f"Disimpan {len(articles)} artikel ke {output_file}")
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
