import requests
data = {
    'red':   'Alice',
    'green': 'Bob',
    'blue':  'We did it!',
    'ledFunction': 'colorWipe',
    'section': 'all'}
r = requests.post("http://127.0.0.1/led", json={'json_payload': data})
