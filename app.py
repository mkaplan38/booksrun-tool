from flask import Flask, jsonify, request, send_from_directory
import requests
import re
import os
import time
from datetime import datetime, timezone, timedelta

app = Flask(__name__, static_folder='static')

# Ortam değişkenlerinden al
CLIENT_ID     = os.environ.get('EBAY_CLIENT_ID', 'SmilesLL-Givetarg-PRD-0e06b92ff-0280a7cb')
CLIENT_SECRET = os.environ.get('EBAY_CLIENT_SECRET', 'PRD-e06b92ff01b6-ef2d-4518-8381-76d6')

BROWSE_URL = 'https://api.ebay.com/buy/browse/v1/item_summary/search'
TOKEN_URL  = 'https://api.ebay.com/identity/v1/oauth2/token'

# Token cache
_token_cache = {'token': None, 'expires_at': 0}

def get_token():
    """Token yoksa veya süresi dolduysa otomatik yenile."""
    now = time.time()
    if _token_cache['token'] and now < _token_cache['expires_at'] - 60:
        return _token_cache['token']

    resp = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'grant_type': 'client_credentials', 'scope': 'https://api.ebay.com/oauth/api_scope'},
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=10
    )
    data = resp.json()
    if 'access_token' not in data:
        raise Exception(f"Token alınamadı: {data.get('error_description', str(data))}")

    _token_cache['token']      = data['access_token']
    _token_cache['expires_at'] = now + int(data.get('expires_in', 7200))
    return _token_cache['token']

def get_headers():
    return {
        'Authorization': f'Bearer {get_token()}',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        'Content-Type': 'application/json'
    }

def extract_isbn(text):
    m = re.search(r'\b(97[89]\d{10}|\d{9}[\dX])\b', text, re.I)
    if m:
        isbn = m.group(1).upper()
        return isbn.zfill(10) if len(isbn) < 10 else isbn
    return ''

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/fetch')
def fetch_books():
    offset    = request.args.get('offset', 0, type=int)
    seller    = request.args.get('seller', 'booksrun')
    cond      = request.args.get('cond', 'both')
    price_min = request.args.get('price_min', '').strip()
    price_max = request.args.get('price_max', '').strip()
    hours     = request.args.get('hours', '').strip()

    cond_map = {
        'new':     ['1000'],
        'vg':      ['2750'],
        'likenew': ['1750'],
        'both':    ['1000', '2750'],
        'all':     ['1000', '1750', '2750'],
    }
    cond_ids = cond_map.get(cond, [])

    filter_parts = [f'sellers{{{seller}}}']
    if cond_ids:
        filter_parts.append('conditionIds:{' + '|'.join(cond_ids) + '}')
    if hours and hours != '0':
        dt = datetime.now(timezone.utc) - timedelta(hours=int(hours))
        filter_parts.append(f'itemStartDate:[{dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")}]')

    # Fiyat filtresi ayrı parametre olarak gönderilmeli
    params = {
        'category_ids': '267',
        'filter':       ','.join(filter_parts),
        'sort':         'newlyListed',
        'limit':        200,
        'offset':       offset,
        'fieldgroups':  'STANDARD'
    }

    if price_min or price_max:
        lo = price_min if price_min else '0'
        hi = price_max if price_max else '99999'
        params['filter'] += f',price:[{lo}..{hi}],priceCurrency:USD'

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

            isbn = extract_isbn(title)
            if not isbn:
                for asp in item.get('localizedAspects', []):
                    if 'isbn' in asp.get('name', '').lower():
                        isbn = extract_isbn(asp.get('value', ''))
                        break

            # Server-side fiyat kontrolü
            if price_min and price < float(price_min): continue
            if price_max and price > float(price_max): continue

            results.append({
                'title': title, 'isbn': isbn, 'price': price,
                'condition': condition, 'url': url,
                'date': date, 'item_id': item_id
            })

        return jsonify({'success': True, 'items': results, 'total': total, 'offset': offset})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/item_isbn')
def item_isbn():
    item_id = request.args.get('item_id', '')
    if not item_id:
        return jsonify({'isbn': ''})
    try:
        resp = requests.get(
            f'https://api.ebay.com/buy/browse/v1/item/{item_id}',
            headers=get_headers(), timeout=10
        )
        data = resp.json()
        for asp in data.get('localizedAspects', []):
            if 'isbn' in asp.get('name', '').lower():
                return jsonify({'isbn': extract_isbn(asp.get('value', ''))})
        return jsonify({'isbn': extract_isbn(data.get('description', ''))})
    except:
        return jsonify({'isbn': ''})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
