import common.db as db
import json


query = """INSERT INTO testimoniesSaturationPruned2015 (IntCode, TotSegments) VALUES (%s, %s) """

connection = db.get_connection()
cursor = connection.cursor()


testimony_data = json.load(open('testimony_details_20.json'))


for element in testimony_data.values():
    for int_code, testimony in element.items():
        cursor.execute(query, (int_code, testimony['TotSegments'],))

connection.commit()
cursor.close()

