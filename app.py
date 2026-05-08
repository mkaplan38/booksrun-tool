from flask import Flask, jsonify, request, send_from_directory
import requests
import re
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__, static_folder='static')

OAUTH_TOKEN = 'v^1.1#i^1#p^1#f^0#I^3#r^0#t^H4sIAAAAAAAA/+VYbWwURRi+6xc0tGikWgFDz6VGQW5vbu9u97pyZ64f2Cv9OHpHKVRCZnfn2rV7u8vuHL3zBykNkPgRgyamJARaIgYlQRNN1ARCCSEYIMRURFJIDGJ/+ENCSDBE5Yez16NcKwGkR2zi7Y/LvvPOO+/zzPsxO6C/pHT5zsadt8rtcwqG+0F/gd3ungdKS4pfnl9YsKjYBnIU7MP91f1FA4W/rjRhQtH5dmTqmmoiRyqhqCafEQaopKHyGjRlk1dhApk8FvloqKWZZ2jA64aGNVFTKEe4PkDFBVHwiZIgsW6uhvMAIlXv2IxpAQqKjA8g4OdY6Pdzgo+Mm2YShVUTQxUHKAYwrBP4nMAfA34eMLyHpTkvt4FydCDDlDWVqNCACmbc5TNzjRxf7+8qNE1kYGKECoZDq6JtoXB9Q2tspSvHVjDLQxRDnDSnvtVpEnJ0QCWJ7r+MmdHmo0lRRKZJuYITK0w1yofuOPMI7meoZmBNXPBKbh8DPSxk2LxQuUozEhDf3w9LIkvOeEaVRyqWcfpBjBI2hDeQiLNvrcREuN5h/a1JQkWOy8gIUA21ofWhSIQKRhOygszmZudr8haEodHtjLTXO0ncsEINE487AeMHkBOF7EIT1rI0T1upTlMl2SLNdLRquBYRr9FUbjjel8MNUWpT24xQHFse5ei5wR0OPf4N1qZO7GIS96jWvqIEIcKReX3wDkzOxtiQhSRGkxamD2QoImmj67JETR/MxGI2fFJmgOrBWOddrr6+PrrPQ2tGt4sBwO3qbGmOij0oASmia+X6hL784AlOOQNFRGSmKfM4rRNfUiRWiQNqNxX0+dx+ALK8T3UrOF36D0EOZtfUjMhXhtR4RYnzij6WQ1aeiPnIkGA2SF2WH0iAaWcCGr0I6woUkVMkcZZMIEOWeI8vznj8ceSU2Jq401tDwlbwSazTHUcIICQIYo3//5QoDxvqUSQaCOcl1vMW54In7e1Gb4bWM95oW6cr1ra2sa2zsaVz9Tq9B6X0zU0ajK2RWsKtkfWBh82Ge4KvU2TCTIysnw8CrFzPHwmNmomRNCN4UVHTUURTZDE9uzbYY0gRaOB0FCkKEcwIZEjXw/mp1XmD9y/LxKPhzl+P+o/60z1RmVbIzi5U1nyTGIC6TFsdiBa1hMvKdQ2S44cl3pTx2nFPxWlKLiIjDUtENOlLkgDFXtpAUNJUJT0j3mRy8p1VrBGcEyTI0sSRlc4wQZtbRILY1JKEA5Nus05wMa0XqaQfYkNTFGR0uGdcDxKJJIaCgmZbYchDgshwljVrN8f5GYbz+NgZ4RIzrXjTbCtpVikvGrDDx17O2xFUErMLu25oUlK0zqiP4ZPDNfUCJGjL/NwD9hNgwH6swG4HK8EL7qXg+ZLCtUWFZYtMGSNahnHalLtV8l1vILoXpXUoGwULbGcujLUuOdL0yVvjlf07ql0f2Obn3L8MbwTPTt7AlBa65+Vcx4Dn7o4Uu5+oLGdY4AN+8jAedgNYene0yP1MUcXglaH42SvOiwvGV1QfODrW8dPIyTQon1Sy24ttJFhsw1tKRyNLd1xdsenkbVG50lhW3Xlm7tWqrXNbK40fEdo9aN91qn7h8r3HD1dFP3yl7MXRa+d/GfKkLkjfXXp9zjVVer9BWfLFQv9TX+7cXNc7xrz7zun2E3t+2O79/VjFYkEYqrTvW3bz8rb6rX9+OsSeTW47+Me55pYULl+3x3vgxl9zF3eXHR7Zf35j1W9fNV8IfNY1Hv9mZPvbLx188uk1NNs0WK1+/t78vdTiMWZfoJf/PvxqxYg01HiZ/lapW32x9/RgYaSkdtftStv+612nS7sOdV2/UdA0evPooarDqdHjH9MNW7nShV9zYskTp9D40Y/OxXb7j1UU3dpde2TkUt2yjeDymZ+7Jvbyb4WzcIcZEwAA'

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
