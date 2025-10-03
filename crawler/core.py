import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/140.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def find_article_urls_from_soup(soup):
    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("https://") and "read" in href:
            urls.append(href)
    return list(set(urls))

def scrape_article(url):
    soup = get_soup(url)

    # Judul
    title = soup.find("h1")
    title = title.get_text(strip=True) if title else None

    # Isi artikel
    paragraphs = soup.find_all("p")
    content = " ".join(p.get_text(strip=True) for p in paragraphs)

    # Cari tanggal terbit
    published_at = None

    # 1. Dari meta og:article:published_time
    meta_time = soup.find("meta", {"property": "article:published_time"})
    if meta_time and meta_time.has_attr("content"):
        published_at = meta_time["content"]

    # 2. Dari <time datetime="">
    if not published_at:
        published = soup.find("time")
        if published and published.has_attr("datetime"):
            published_at = published["datetime"]

    # 3. Dari teks tanggal
    if not published_at:
        date_el = soup.find("div", class_="date") or soup.find("span", class_="date")
        if date_el:
            published_at = date_el.get_text(strip=True)

    # 4. Fallback → UTC now
    if not published_at:
        published_at = datetime.utcnow().isoformat() + "+00:00"

    return {
        "link": url,
        "judul": title,
        "isi_artikel": content,
        "tanggal_terbit": published_at
    }

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
