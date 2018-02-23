import json
import urllib2
data = {
    'red':   '41',
    'green': '11',
    'blue':  '117',
    'ledFunction': 'happyFace',
    'section': 'all'}
req = urllib2.Request('http://localhost/led')
req.add_header('Content-Type', 'application/json')
response = urllib2.urlopen(req, json.dumps(data))
