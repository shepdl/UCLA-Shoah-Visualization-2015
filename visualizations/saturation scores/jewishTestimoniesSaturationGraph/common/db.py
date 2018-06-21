import MySQLdb
import config

HOST = "localhost"
USER = "root"
PASSWORD = ""
DB = "shoah_2015"
CHARSET = "utf8"
UNICODE = True

connection = MySQLdb.connect(host=HOST,user=USER,passwd=PASSWORD,
        db=DB, use_unicode=UNICODE,charset=CHARSET)

def get_cursor():
    return connection.cursor(MySQLdb.cursors.DictCursor)
def get_connection():
    return connection

class query(object):
    def __init__(self, query, params=None):
        self.query = query
        self.cursor = get_cursor()
        self.cursor.execute(self.query, params)

    def results(self, field = None):
        if not self.results:
            self.results = []
            while True:
                if not field:
                    self.results.append(self.cursor.fetchone())
                else:
                    self.results.append(self.cursor.fetchone()[field])

    def tree_on(self, *key_fields):
        output = {}
        while True:
            row = cursor.fetchone()
            if not row:
                break
            o = output
            for k in key_fields:
                if row[k] not in o:
                    o[row[k]] = {}
                o = o[row[k]]
            # output[row[key_field]] = row
        self.cursor.close()
        return output

        
