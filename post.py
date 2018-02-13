import requests
data = {
    'red':   '255',
    'green': '255',
    'blue':  '0',
    'ledFunction': 'colorWipe',
    'section': 'all'}
r = requests.post("http://127.0.0.1/led", json={'json_payload': data})
