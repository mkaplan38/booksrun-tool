from flask import Flask, jsonify, request, send_from_directory
import requests
import re
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__, static_folder='static')

OAUTH_TOKEN = 'v^1.1#i^1#r^0#p^1#I^3#f^0#t^H4sIAAAAAAAA/+VYe2wURRjvXVuw6YOohPIKOdZCVHK7s3vP3dJLDgq29HEtd9S2iYHZ3dl26d7uug/aAyRNFZDUSNIYCQENxGgwJAQjfyBIMfyBCRCIGgMoMWoFJMZgioSoMTp7Pcq1EkB6xCbeP5f55ptvvt9vvsfsgN4pRc9uqdlyq9Q11b2nF/S6XS66GBRNKVxUlu+eXZgHshRce3oregv68n9cbMKkonMrkalrqok8PUlFNbm0sIqwDZXToCmbnAqTyOQsgYtHG+o5hgScbmiWJmgK4amtriIYKeTzsTQrQICkECthqXrbZkKrImgeMYAPQSkM/RLrD+F507RRrWpaULXwesAEvSDgBaEEYDnGz/kDZIgJthOeFmSYsqZiFRIQkbS7XHqtkeXrvV2FpokMCxshIrXR5fFYtLZ6WWNiMZVlK5LhIW5ByzbHjpZqIvK0QMVG997GTGtzcVsQkGkSVGRkh7FGuehtZx7C/QzVAUmCwRBi/WyQBeGcULlcM5LQurcfjkQWvVJalUOqJVup+zGK2eDXIsHKjBqxidpqj/PXbENFlmRkVBHLlkTbok1NRCSelBVk1td7n5PXIQsaHd6mldVegECQZxlJ8gImDGBI4DMbjVjL0Dxup6WaKsoOaaanUbOWIOw1Gs8NncUNVoqpMSMqWY5HWXo0Pcoh0+4c6sgp2lan6pwrSmIiPOnh/U9gdLVlGTJvW2jUwviJNEVVBNR1WSTGT6ZjMRM+PWYV0WlZOkdR3d3dZLeP1IwOigGAplob6uNCJ0pCAus6uT6iL99/gVdOQxEQXmnKnJXSsS89OFaxA2oHEQkE6DAAGd7HuhUZL/2HIAszNTYjcpUhosCwLONDtAADAYnPSbGJZIKUcvxAPEx5k9DoQpauQAF5BRxndhIZssj5AhLjC0vIKwZZyetncdjyATHopSWEAEI8L7Dh/1OiPGiox5FgICsnsZ6zOOd9KX8HWh9tY/zxWCuViK2qibXWNLTWPa93oh79xRUaTDSLDbWNTW1VD5oNdwW/VJExMwm8fy4IcHI9dyTUaKaFxAnBiwuajpo0RRZSk+uAfYbYBA0rFUeKggUTAhnV9drc1OqcwfuXZeLhcOeuR/1H/emuqEwnZCcXKme9iQ1AXSadDkQKWpJycl2D+PrhiFenvfbcVXGcEoVluGEJiMR9SeSh0EUaCIqaqqQmxJuMb76TijWMc4QEWRy5spJpJkhznYARm5qNOTDJmHODS2hdSMX90DI0RUFGCz3hepBM2hbkFTTZCkMOEkSGk6xZ06FQmPYHwuHAhHAJ6Va8erKVNKeUF/S54CMv5ysRVJKTC7tuaKItOHfUR/DJQY19AInkpX90n+sE6HMNul0usBgsoJ8C86fkryrIL5ltyhYiZSiRptyh4u96A5FdKKVD2XA/mXfqy4uN846u2Lfth/LezRXUQF5Z1vvLnhfAzNEXmKJ8ujjrOQbMvTNTSE8rL2WCIABCgGX8/kA7eOrObAE9o2D603P6j5a8+sV71+vXlzec21t2KRq/BEpHlVyuwjwcLHlvD1ceOLZI3W/eqB7Yt/Dd/vKtYEN8+8HLMz8ReHrRdyeP7v/DnrJmM9o4fP37l5/Yd2b1kSvKtMNHPnufmtU6v/LNb4YWtp0dtLo/b/hqRvHxN47sKNpeeinwc/e3Jw+Qb1UMb+px3+oYon5rHmbPl54AyZbXi+KxD3YUNl3YNef3xmbu4y3ux+UrQxu2DRyqnLWibvfZEvlcHVexobjuZvjrm6sSA6fm/rngnY/WBtdra+d3zRz89ZfErp/KDrXuHfx06PTlq7tfeuX8axtnleyWUaggWZk/1965aa94/NZjpy9c2Fp69cP+/nnT3cVFwhq7/fDFnb3H+qdyLCAGri278dcZ6nJJ97WDz4yc5d/JQqcPGRMAAA=='

BROWSE_URL = 'https://api.ebay.com/buy/browse/v1/item_summary/search'

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def extract_isbn(title):
    m = re.search(r'\b(97[89]\d{10}|\d{9}[\dX])\b', title, re.I)
    if m:
        isbn = m.group(1).upper()
        if len(isbn) < 10:
            isbn = isbn.zfill(10)
        return isbn
    return ''

def build_filter(seller, cond_ids, price_min, price_max, hours):
    parts = [f'sellers{{{seller}}}']
    if cond_ids:
        parts.append(f'conditionIds{{{"|".join(cond_ids)}}}')
    if price_min or price_max:
        lo = price_min if price_min else '0'
        hi = price_max if price_max else '99999'
        parts.append(f'price:[{lo}..{hi}]')
    if hours:
        dt = datetime.now(timezone.utc) - timedelta(hours=int(hours))
        parts.append(f'itemStartDate:[{dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")}]')
    return ','.join(parts)

@app.route('/api/fetch')
def fetch_books():
    offset    = request.args.get('offset', 0, type=int)
    seller    = request.args.get('seller', 'booksrun')
    cond      = request.args.get('cond', 'both')
    price_min = request.args.get('price_min', '')
    price_max = request.args.get('price_max', '')
    hours     = request.args.get('hours', '')  # 24 veya 48

    # Kondisyon ID'leri
    # eBay: 1000=New, 1750=Like New, 2750=Very Good, 3000=Good
    cond_map = {
        'new':       ['1000'],
        'vg':        ['2750'],
        'likenew':   ['1750'],
        'both':      ['1000', '2750'],
        'all':       ['1000', '1750', '2750'],
    }
    cond_ids = cond_map.get(cond, [])

    filter_str = build_filter(seller, cond_ids, price_min, price_max, hours)

    params = {
        'category_ids': '267',
        'filter': filter_str,
        'sort': 'newlyListed',
        'limit': 200,
        'offset': offset,
        'fieldgroups': 'STANDARD'
    }

    headers = {
        'Authorization': f'Bearer {OAUTH_TOKEN}',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        'Content-Type': 'application/json'
    }

    try:
        resp = requests.get(BROWSE_URL, params=params, headers=headers, timeout=15)
        data = resp.json()

        if 'errors' in data:
            return jsonify({'success': False, 'error': data['errors'][0].get('message', 'eBay API hatası')}), 400

        items_raw = data.get('itemSummaries', [])
        total     = data.get('total', 0)

        results = []
        for item in items_raw:
            title     = item.get('title', '')
            price     = float(item.get('price', {}).get('value', 0))
            condition = item.get('condition', '')
            url       = item.get('itemWebUrl', '')
            date      = item.get('itemCreationDate', '')[:10] if item.get('itemCreationDate') else ''
            isbn      = extract_isbn(title)

            results.append({
                'title':     title,
                'isbn':      isbn,
                'price':     price,
                'condition': condition,
                'url':       url,
                'date':      date
            })

        return jsonify({'success': True, 'items': results, 'total': total, 'offset': offset})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
