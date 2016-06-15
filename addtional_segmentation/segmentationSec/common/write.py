import simplejson as js
import sys
import datetime

def json(data, filename):
    data["FW-meta"] = {
        "created_using" : sys.argv[1]
        "arguments" : sys.argv[1:]
        "created_at": datetime.datetime.now()
    }
    json.write(data, open(filename, "w"))
