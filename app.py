from flask import Flask, jsonify, request, send_from_directory
import requests
import re
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__, static_folder='static')

OAUTH_TOKEN = 'v^1.1#i^1#r^0#p^1#I^3#f^0#t^H4sIAAAAAAAA/+VYe2wURRjv9QHyaA3BUCDSXJeHEXJ7s7f36tK7eG2BHlx7pXfUtpHA3O5su3Rvd9mZoz2i4WgC8hACqIkhEMAiIDERowkxEJDqHyJR/4EgiQZDADUxvv5RIjHOXku5VgJIj9jE++ey33zzzff7zfeYGZAZN2H+5vrNv5faxhcezIBMoc3GTQITxpUsKCsqnFlSAHIUbAczczLFvUXfV2OYVA2hGWFD1zCy9yRVDQtZYYBJmZqgQ6xgQYNJhAUiCrFQQ0RwsUAwTJ3ooq4y9nBdgPF4OJdH9vhEj8vt9/NVVKrdsRnXAwzvhX4Zyj7gATLw+3g6jnEKhTVMoEYCjAu4vA7gcQB/nOME4BN4wPJebztjb0EmVnSNqrCACWbdFbJzzRxf7+8qxBiZhBphguHQ4lg0FK5b1BivdubYCg7yECOQpPDwr1pdQvYWqKbQ/ZfBWW0hlhJFhDHjDA6sMNyoELrjzCO4n6XaD/yUaI/M+3nZJ1Ul8kLlYt1MQnJ/PyyJIjnkrKqANKKQ9IMYpWwk1iCRDH41UhPhOrv1tzwFVUVWkBlgFtWE2kJNTUwwllRUhCMRxxJlHSLQ7HA0Ndc5AALeRJVLlh3A5QfQJyYGFxqwNkjziJVqdU1SLNKwvVEnNYh6jYZzAwRPDjdUKapFzZBMLI9y9fghDrl2a1MHdjFFOjVrX1GSEmHPfj54B4ZmE2IqiRRBQxZGDmQpCjDQMBSJGTmYjcXB8OnBAaaTEENwOru7u9luntXNDqcLAM7Z2hCJiZ0oCRmqa+X6gL7y4AkOJQtFRHQmVgSSNqgvPTRWqQNaBxOk2e4HYJD34W4FR0r/IcjB7ByeEfnKEK+bh7LMcxwQ3a6EnJdiExwMUqflB0rAtCMJzS5EDBWKyCHSOEslkalIAu+RXbxfRg7JWyU73FU0bBMeyevgZIQAQomEWOX/PyXKw4Z6DIkmInmJ9bzFeYJPuzvQ+lCbyx2Ltjrj0RX10db6htZlzxudqMdYu1SH8eVSQ7ixqS3wsNlwT/C1qkKZidP180GAlev5I6FexwRJo4IXE3UDNemqIqbH1gbzptQETZKOIVWlglGBDBlGOD+1Om/w/mWZeDTc+etR/1F/uicqbIXs2EJlzcfUADQU1upArKgnnVau65AePyzxqqzX9nsqjlByUhltWCJiaV+SElDsYk0EJV1T06PiTaEn3zHFGsU5QIIiDRxZ2SwTLF4nUsRYT1EOMBu1TnBxvQtptB8SU1dVZLZwo64HyWSKwISKxlphyEOCKHCMNWvO5/PTk5fbMzpcYrYVrxprJc0q5cW9NvjYy3kzgmpybGE3TF1KidYZ9TFcOZzDH0CCBdkf12vrB722M4U2G6gGc7nZoHJc0YrioskzsUIQq0CZxUqHRu/1JmK7UNqAilk4teCzS1caK04tPbb1enlm0xznnoKynPeXgyvB9KEXmAlF3KSc5xjw9N2REu7J8lKXF3iAn15hfDxoB7PvjhZz04qf6k9vfHFp5YfnP3iZVB6Zai85y4S3g9IhJZutpIAGS0G6mm+7mPrt1HKud0ZjX/d2z+4T59de33CmsLn9/d07lcPqgs9PzplX9k7kp7bVVzZeqRA+CqRXv/W2e5oUvrFrmloU0uat2Xqzs+bor7cSZktVOUmttO/6c2r1rEOHdjrf/ONHR/l36+afLOt/Sbj2yzfXtm/b27Dr1slvybFtGbUhtGxfNX7uS3Z/+StLvu57d29rYEv/ex/3/1WzcrK8pvtm0YUf5h6e13f7hleKLNywI7Lq9kb/1SlfTF//iXHu7OkfTjt+2+/Ov/C+LrNFZmLkRmrI9sOH3ih7o3zW/apFT/jTaVTjhw9MbCXfwOZ0cDfGRMAAA=='

BROWSE_URL  = 'https://api.ebay.com/buy/browse/v1/item_summary/search'
ITEM_URL    = 'https://api.ebay.com/buy/browse/v1/item/'

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def extract_isbn(text):
    """ISBN-13 veya ISBN-10 çıkar, yoksa boş döndür."""
    m = re.search(r'\b(97[89][\d]{10}|\d{9}[\dX])\b', text, re.I)
    if m:
        isbn = m.group(1).upper()
        return isbn.zfill(10) if len(isbn) < 10 else isbn
    return ''

def get_headers():
    return {
        'Authorization': f'Bearer {OAUTH_TOKEN}',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        'Content-Type': 'application/json'
    }

@app.route('/api/fetch')
def fetch_books():
    offset    = request.args.get('offset', 0, type=int)
    seller    = request.args.get('seller', 'booksrun')
    cond      = request.args.get('cond', 'both')
    price_min = request.args.get('price_min', '').strip()
    price_max = request.args.get('price_max', '').strip()
    hours     = request.args.get('hours', '', type=str).strip()

    # Kondisyon ID'leri: 1000=New, 1750=Like New, 2750=Very Good, 3000=Good
    cond_map = {
        'new':     ['1000'],
        'vg':      ['2750'],
        'likenew': ['1750'],
        'both':    ['1000', '2750'],
        'all':     ['1000', '1750', '2750'],
    }
    cond_ids = cond_map.get(cond, [])

    # Filter string — fiyat eBay formatı: price:[min..max],priceCurrency:USD
    filter_parts = [f'sellers{{{seller}}}']
    if cond_ids:
        filter_parts.append('conditionIds:{' + '|'.join(cond_ids) + '}')
    if price_min or price_max:
        lo = price_min if price_min else '0'
        hi = price_max if price_max else '99999'
        filter_parts.append(f'price:[{lo}..{hi}]')
        filter_parts.append('priceCurrency:USD')
    if hours and hours != '0':
        dt = datetime.now(timezone.utc) - timedelta(hours=int(hours))
        filter_parts.append(f'itemStartDate:[{dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")}]')

    params = {
        'category_ids': '267',
        'filter':       ','.join(filter_parts),
        'sort':         'newlyListed',
        'limit':        200,
        'offset':       offset,
        'fieldgroups':  'STANDARD'
    }

    try:
        resp = requests.get(BROWSE_URL, params=params, headers=get_headers(), timeout=15)
        data = resp.json()

        if 'errors' in data:
            msg = data['errors'][0].get('message', 'eBay API hatası')
            return jsonify({'success': False, 'error': msg}), 400

        items_raw = data.get('itemSummaries', [])
        total     = data.get('total', 0)

        results = []
        for item in items_raw:
            title     = item.get('title', '')
            price     = float(item.get('price', {}).get('value', 0))
            condition = item.get('condition', '')
            url       = item.get('itemWebUrl', '')
            date      = (item.get('itemCreationDate') or '')[:10]
            item_id   = item.get('itemId', '')

            # ISBN: önce başlıktan dene
            isbn = extract_isbn(title)

            # Başlıkta yoksa additionalImages veya localizedAspects'ten dene
            if not isbn:
                for asp in item.get('localizedAspects', []):
                    if 'isbn' in asp.get('name', '').lower():
                        isbn = extract_isbn(asp.get('value', ''))
                        break

            # Fiyat filtresi — API bazen dışarıdan gelenleri geçirebilir, server-side kontrol
            if price_min and price < float(price_min):
                continue
            if price_max and price > float(price_max):
                continue

            results.append({
                'title':     title,
                'isbn':      isbn,
                'price':     price,
                'condition': condition,
                'url':       url,
                'date':      date,
                'item_id':   item_id
            })

        return jsonify({'success': True, 'items': results, 'total': total, 'offset': offset})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/item_isbn')
def item_isbn():
    """Tek bir item'ın detaylarından ISBN çeker (arka planda)."""
    item_id = request.args.get('item_id', '')
    if not item_id:
        return jsonify({'isbn': ''})
    try:
        resp = requests.get(
            f'{ITEM_URL}{item_id}',
            headers=get_headers(),
            timeout=10
        )
        data = resp.json()
        # localizedAspects içinde ISBN ara
        for asp in data.get('localizedAspects', []):
            if 'isbn' in asp.get('name', '').lower():
                return jsonify({'isbn': extract_isbn(asp.get('value', ''))})
        # description içinde ara
        desc = data.get('description', '')
        isbn = extract_isbn(desc)
        return jsonify({'isbn': isbn})
    except:
        return jsonify({'isbn': ''})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
