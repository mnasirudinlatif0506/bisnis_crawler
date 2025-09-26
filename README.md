# Bisnis.com Crawler & Scraper

## Deskripsi
Crawler dan scraper artikel dari [bisnis.com].  
Dua mode:
- **Backtrack**: ambil artikel dalam rentang tanggal tertentu.
- **Standard**: ambil artikel terbaru secara berkala.

## Cara Jalankan
1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Mode Backtrack
```bash
python -m crawler.backtrack_cli --start 2025-09-25 --end 2025-09-25 --output example_outputs/backtrack.json --max-pages 1 --rate 1
```

3. Mode Standard
```bash
python -m crawler.standard_cli --run-once --max-pages 1 --rate 1 --output example_outputs/standard_sample.json
```

## Arsitektur
- `crawler/core.py`: fungsi dasar scraping & ekstraksi artikel.
- `crawler/backtrack_cli.py`: entrypoint mode backtrack.
- `crawler/standard_cli.py`: entrypoint mode standard.
- `example_outputs/`: tempat output JSON.

## Catatan
Hargai robots.txt dan TOS situs. Gunakan rate-limit saat crawling.
