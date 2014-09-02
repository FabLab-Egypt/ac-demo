# -*- charset: utf8 -*-

import json

from urlparse import urlparse, urljoin
from flask import request, url_for


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

def readJSONFile(path):
    return json.loads(readFile(path))


def writeJSONFile(path, obj):
    writeFile(path, json.dumps(obj))

def writeFile(path, data):
    with open(path, 'w') as f:
        f.write(data)

def readFile(path):
    data = ""
    with open(path, 'r') as f:
        data = f.read()
    return data
