# BooksRun eBay Fetcher

BooksRun eBay mağazasından en son eklenen kitapları çeken web uygulaması.

## Özellikler
- New / Very Good / İkisi Birden kondisyon filtresi
- 500 / 1.000 / 2.000 / 5.000 / 10.000 kitap seçeneği
- En yeni eklenen sırasıyla çeker
- ISBN, fiyat, tarih gösterir
- Excel (.xlsx) indirme
- ISBN listesi kopyalama

## Render.com'a Yükleme

1. github.com'da yeni bir repository oluşturun: "booksrun-tool"
2. Bu dosyaları yükleyin
3. render.com'a gidin → "New Web Service"
4. GitHub repository'sini bağlayın
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn app:app`
7. "Deploy" tıklayın
