import requests
data = {'sender':   'Alice',
    'receiver': 'Bob',
    'message':  'We did it!'}
r = requests.post("http://192.168.0.97/led", json={'json_payload': data})
