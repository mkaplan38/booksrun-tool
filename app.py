from flask import Flask, jsonify, request, send_from_directory
import requests
import json
import os

app = Flask(__name__, static_folder='static')

APP_ID = 'SmilesLL-Givetarg-PRD-0e06b92ff-0280a7cb'
EBAY_URL = 'https://svcs.ebay.com/services/search/FindingService/v1'

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/fetch')
def fetch_books():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'StartTimeNewest')
    cond = request.args.get('cond', 'both')  # new, vg, both

    params = {
        'OPERATION-NAME': 'findItemsAdvanced',
        'SERVICE-VERSION': '1.0.0',
        'SECURITY-APPNAME': APP_ID,
        'RESPONSE-DATA-FORMAT': 'JSON',
        'categoryId': '267',
        'sortOrder': sort,
        'itemFilter(0).name': 'Seller',
        'itemFilter(0).value': 'booksrun',
        'paginationInput.pageNumber': page,
        'paginationInput.entriesPerPage': 100,
    }

    try:
        resp = requests.get(EBAY_URL, params=params, timeout=15)
        data = resp.json()
        root = data.get('findItemsAdvancedResponse', [{}])[0]
        items = root.get('searchResult', [{}])[0].get('item', [])

        results = []
        for item in items:
            title = item.get('title', [''])[0]
            price = item.get('sellingStatus', [{}])[0] \
                        .get('currentPrice', [{}])[0] \
                        .get('__value__', '0')
            condition = item.get('condition', [{}])[0] \
                           .get('conditionDisplayName', [''])[0]
            url = item.get('viewItemURL', [''])[0]
            date = item.get('listingInfo', [{}])[0] \
                       .get('startTime', [''])[0]

            # Kondisyon filtresi
            c = condition.lower()
            if cond == 'new' and not ('new' in c and 'very' not in c):
                continue
            if cond == 'vg' and 'very good' not in c:
                continue
            if cond == 'both' and ('new' not in c and 'very good' not in c):
                continue

            # ISBN çıkar
            import re
            isbn_match = re.search(r'\b(97[89]\d{10}|\d{9}[\dX])\b', title, re.I)
            isbn = isbn_match.group(1).upper() if isbn_match else ''
            if isbn and len(isbn) < 10:
                isbn = isbn.zfill(10)

            results.append({
                'title': title,
                'isbn': isbn,
                'price': float(price),
                'condition': condition,
                'url': url,
                'date': date[:10] if date else ''
            })

        total_pages = int(
            root.get('paginationOutput', [{}])[0]
                .get('totalPages', ['1'])[0]
        )

        return jsonify({
            'success': True,
            'items': results,
            'total_pages': total_pages,
            'page': page
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
