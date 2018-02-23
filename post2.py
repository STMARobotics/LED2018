import json
import urllib2
data = {
    'red':   '100',
    'green': '5',
    'blue':  '5',
    'ledFunction': 'happyFace',
    'section': 'all'}
req = urllib2.Request('http://localhost/led')
req.add_header('Content-Type', 'application/json')
response = urllib2.urlopen(req, json.dumps(data))
