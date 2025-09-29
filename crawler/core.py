import requests
import re
import time
import json
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dateutil import parser as dateparser
from datetime import datetime, timezone, timedelta

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bisnis-crawler")

# header request
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

# timezone jakarta
JAKARTA_TZ = timezone(timedelta(hours=7))

# pola URL artikel: /read/YYYYMMDD/
ARTICLE_URL_RE = re.compile(r'https?://[^/]*bisnis\.com/read/(\d{8})/')

def get_soup(session, url, retries=3, backoff=1.0):
    """Mengambil halaman HTML dan kembalikan sebagai objek BeautifulSoup"""
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=15)
            r.raise_for_status()
            return BeautifulSoup(r.text, 'lxml')
        except Exception as e:
            logger.warning("Gagal GET %s (%s), percobaan %d/%d", url, e, attempt+1, retries)
            time.sleep(backoff * (2**attempt))
    logger.error("Tidak bisa akses %s setelah %d kali coba", url, retries)
    return None

def find_article_urls_from_soup(soup, base_url="https://bisnis.com"):
    """Cari semua link artikel dari halaman"""
    found = set()
    if not soup:
        return found
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href.startswith('//'):
            href = 'https:' + href
        if href.startswith('/'):
            href = urljoin(base_url, href)
        if '/read/' in href and 'bisnis.com' in urlparse(href).netloc:
            m = ARTICLE_URL_RE.search(href)
            if m:
                found.add(href.split('?')[0])
    return found

def iso_from_url_or_meta(soup, url):
    """Ambil tanggal terbit artikel dalam format ISO"""
    if soup:
        meta = soup.find('meta', property='article:published_time') \
            or soup.find('meta', attrs={'name':'publish_date'}) \
            or soup.find('meta', attrs={'name':'date'})
        if meta and meta.get('content'):
            try:
                dt = dateparser.parse(meta['content'])
                return dt.astimezone(JAKARTA_TZ).isoformat()
            except Exception:
                pass
        ttag = soup.find('time', datetime=True)
        if ttag:
            try:
                dt = dateparser.parse(ttag['datetime'])
                return dt.astimezone(JAKARTA_TZ).isoformat()
            except Exception:
                pass
    m = ARTICLE_URL_RE.search(url)
    if m:
        ymd = m.group(1)
        try:
            dt = datetime.strptime(ymd, "%Y%m%d").replace(tzinfo=JAKARTA_TZ)
            return dt.isoformat()
        except Exception:
            pass
    return None

def extract_title(soup, url):
    """Ambil judul artikel"""
    if not soup:
        return None
    og = soup.find('meta', property='og:title')
    if og and og.get('content'):
        return og['content'].strip()
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    return soup.title.string.strip() if soup.title else None

def extract_content(soup):
    """Ambil isi artikel (teks utama)"""
    if not soup:
        return ""
    candidates = []
    selectors = [
        {'name':'article'},
        {'name':'div', 'class': re.compile(r'(content|article|detail|story|body)', re.I)},
        {'name':'section', 'class': re.compile(r'(content|article|detail|story|body)', re.I)},
        {'name':'div', 'id': re.compile(r'(content|article|detail)', re.I)}
    ]
    for sel in selectors:
        if 'class' in sel or 'id' in sel:
            candidates.extend(soup.find_all(sel['name'], attrs={k:v for k,v in sel.items() if k!='name'}))
        else:
            candidates.extend(soup.find_all(sel['name']))
    best = ""
    for c in candidates:
        t = c.get_text(separator="\n", strip=True)
        if len(t) > len(best):
            best = t
    if not best:
        ps = soup.find_all('p')
        best = "\n\n".join([p.get_text(strip=True) for p in ps])
    return best.strip()

def scrape_article(session, url):
    """Scrape 1 artikel dan kembalikan dict"""
    soup = get_soup(session, url)
    if not soup:
        return None
    title = extract_title(soup, url) or ""
    content = extract_content(soup) or ""
    date_iso = iso_from_url_or_meta(soup, url) or ""
    return {
        "link": url,
        "judul": title,
        "isi_artikel": content,
        "tanggal_terbit": date_iso
    }

def save_json(path, items):
    """Simpan list artikel ke file JSON"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    logger.info("Tersimpan %d artikel ke %s", len(items), path)
