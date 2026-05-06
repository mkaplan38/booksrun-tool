from flask import Flask, jsonify, request, send_from_directory
import requests
import re
import os

app = Flask(__name__, static_folder='static')

OAUTH_TOKEN = 'v^1.1#i^1#I^3#r^0#f^0#p^1#t^H4sIAAAAAAAA/+VYbWwURRju9VMsYFQEJGKOK2LA3N7s3t3e3aZ3ydECPWh7pVdoQSrO7s62S/d2tzt7bY+gqUXQQmgFJWAkUk0M9QdCiEQIpAoGFAKKGH6ISuIXEGOiP0wwJBBnr0e5VgJIj9jE+3OZd955532eeT9mB3QWjpuzvmL9lQm2oty+TtCZa7PRxWBcYcEzE/NypxXkgAwFW1/nzM78rrzLpRjGFZ2rRVjXVIzsHXFFxVxKGHQkDJXTIJYxp8I4wpwpcLFwVSXHUIDTDc3UBE1x2CPlQQfD+Hg6ICLRzwgsDSCRqjds1mlBh4TcNC0JPC3xLAt9bjKPcQJFVGxC1STrAcM6gdcJ2DoQ4Nws52GpAKCXO+xLkYFlTSUqFHCEUu5yqbVGhq+3dxVijAyTGHGEIuH5sWg4Uj6vuq7UlWErlOYhZkIzgYePyjQR2ZdCJYFuvw1OaXOxhCAgjB2u0OAOw41y4RvO3IP7KarZgB8Clvd4Ax4AGSGQFSrna0Ycmrf3w5LIolNKqXJINWUzeSdGCRv8KiSY6VE1MREpt1t/ixNQkSUZGUHHvLnhZeGaGkcoFpcVhCsrnQvkNmRCo8lZU1vuBIjADTCS5ASMH0CfwKc3GrSWpnnETmWaKsoWadherZlzEfEajeSGyeCGKEXVqBGWTMujDD2aTnPoD3iXW4c6eIoJs1m1zhXFCRH21PDOJzC02jQNmU+YaMjCyIkURUEH1HVZdIycTMViOnw6cNDRbJo653K1t7dT7W5KM5pcDAC0q6GqMiY0ozhJxo64leuD+vKdFzjlFBQBkZVY5sykTnzpILFKHFCbHCGvl/YDkOZ9uFuhkdJ/CDIwu4ZnRLYyxO9mfSIvSTzjAX5GlLKRIaF0kLosPxAPk844NFqQqStQQE6BxFkijgxZ5NxeiXH7JeQU2YDk9ARI2PJekXXSEkIAIZ4XAv7/U6LcbajHkGAgMyuxnrU4591JTxNaHV7GeGLRBldddElFtKGiqmFRvd6MOvTWhRqsWyxWRaprlgXvNhtuCb5MkQkzdWT/bBBg5Xr2SKjQsInEUcGLCZqOajRFFpJj64DdhlgDDTMZQ4pCBKMCGdb1SHZqddbg/csycW+4s9ej/qP+dEtU2ArZsYXKWo+JAajLlNWBKEGLu6xc1yC5fljilSmv7bdUHKHkIjLSsAREkb4k8lBooQwERU1VkqPiTSY33zHFGsE5SIIsDl5ZqRQTFG4TCGKsJQgHmIpaN7g6rQWppB+ahqYoyFhKj7oexOMJE/IKGmuFIQsJIsMx1qxpn88PWMAAdlS4hFQrXjnWSppVyvO7bPC+l/NaBJX42MKuG5qYEKw76n345HANfwAJ5aR+dJftKOiyDeTabKAUPEWXgBmFeUvy88ZPw7KJKBlKFJabVPJdbyCqBSV1KBu5j+acPPdN9ZOHFvZ3/zylc91M15aciRnvL32NYOrQC8y4PLo44zkGPHFzpoB+aMoEhgVeEs0BN+thl4OSm7P59OT8SSf6d397TSlqWF/7Jj77x9GvSh7cdwlMGFKy2QpySLDkvHj8euHsDc/K5aHDvZVndvp+fHfOp0t2fImvbjLMlx/391O52wfED346VXxiOrV97ysrHltnOy4/3fla0Rclux7uPvx2165ZJ3+pP9369fytM97fc6lvS+XF/vP49aoD9T8c+7W8qWdzz57pnz8w2TMpeW3tQNl3f/7e6hO2b+4/+NeB/fvFR9Y2bkXBqgstm66/WvjZtbeOtOV3b/Oe39jU7+2ZuqdoRv5Lu3ZcXLN3Njy78YUdx3O/v9pzpfGT3oP4nW2zdn80MH7VhlXPS8qmhjZ45rRv0aGe+pbN+w4vHIg+9/HeFXDqOVi8gGtmXK213aeKhdqdRwoahd/Ol/rVNZd6jxVeeK9s9Ru9lz8cPMu/AQmDQksZEwAA'

BROWSE_URL = 'https://api.ebay.com/buy/browse/v1/item_summary/search'

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/fetch')
def fetch_books():
    offset = request.args.get('offset', 0, type=int)
    sort   = request.args.get('sort', 'newlyListed')
    cond   = request.args.get('cond', 'both')

    # Kondisyon filtresi
    cond_filter = ''
    if cond == 'new':
        cond_filter = ',conditionIds:{1000}'
    elif cond == 'vg':
        cond_filter = ',conditionIds:{3000}'
    elif cond == 'both':
        cond_filter = ',conditionIds:{1000|3000}'

    params = {
        'category_ids': '267',
        'filter': f'sellers{{booksrun}}{cond_filter}',
        'sort': sort,
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

            # ISBN çıkar
            m = re.search(r'\b(97[89]\d{10}|\d{9}[\dX])\b', title, re.I)
            isbn = m.group(1).upper() if m else ''
            if isbn and len(isbn) < 10:
                isbn = isbn.zfill(10)

            results.append({
                'title':     title,
                'isbn':      isbn,
                'price':     price,
                'condition': condition,
                'url':       url,
                'date':      date
            })

        return jsonify({
            'success': True,
            'items':   results,
            'total':   total,
            'offset':  offset
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
