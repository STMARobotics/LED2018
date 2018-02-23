import json
import urllib2
data = {
    'red':   '5',
    'green': '5',
    'blue':  '100',
    'ledFunction': 'colorWipe',
    'section': 'all'}
req = urllib2.Request('http://localhost/led')
req.add_header('Content-Type', 'application/json')
response = urllib2.urlopen(req, json.dumps(data))
