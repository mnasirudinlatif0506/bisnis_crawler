# Bisnis.com Crawler & Scraper

## Deskripsi
Crawler & scraper untuk mengambil artikel dari [Bisnis.com](https://www.bisnis.com).
Mendukung dua mode:
1. **Backtrack Mode**: ambil artikel berdasarkan rentang tanggal.
2. **Standard Mode**: ambil artikel terbaru secara periodik.

## Instalasi
```bash
pip install -r requirements.txt
```

## Cara Jalankan

### Backtrack Mode
```bash
python backtrack_cli.py --start-date 2025-10-02 --end-date 2025-10-02 --output hasil_backtrack.json
```

### Standard Mode
```bash
python standard_cli.py --interval 300 --output hasil_standar.json
```

## Output
Format hasil JSON:
```json
[
  {
    "link": "...",
    "judul": "...",
    "isi_artikel": "...",
    "tanggal_terbit": "2025-10-02T08:30:00+07:00"
  }
]
```
