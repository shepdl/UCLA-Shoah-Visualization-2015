import common.db as db

conn = db.get_connection()
cursor = db.get_cursor()

cursor.execute('''DROP TABLE IF EXISTS firstLevelBaseProbabilitiesUnrolled''');
cursor.execute('''CREATE TABLE firstLevelBaseProbabilitiesUnrolled (TermID INT, ShortFormID INT, Percentile INT, Probability FLOAT)''');
cursor.execute('''DROP TABLE IF EXISTS secondLevelBaseProbabilitiesUnrolled''');
cursor.execute('''CREATE TABLE secondLevelBaseProbabilitiesUnrolled (TermID INT, ShortFormID INT, Percentile INT, Probability FLOAT)''');

read_cursor = db.get_cursor()
write_cursor = db.get_cursor()

read_cursor.execute('''SELECT * FROM firstLevelBaseProbabilities ''')
while True:
    row = read_cursor.fetchone()
    if not row:
        break
    term_ID = row['TermID']
    short_form_ID = row['ShortFormID']
    for segmentile in range(1, 101):
        key = 'L' + str(segmentile)
        write_cursor.execute('''INSERT INTO firstLevelBaseProbabilitiesUnrolled (TermID, ShortFormID, Percentile, Probability) VALUES (%s, %s, %s, %s) ''', 
            [term_ID, short_form_ID, segmentile, row[key],]
        )

conn.commit()

read_cursor.execute('''SELECT * FROM secondLevelBaseProbabilities ''')
while True:
    row = read_cursor.fetchone()
    if not row:
        break
    term_ID = row['TermID']
    short_form_ID = row['ShortFormID']
    for segmentile in range(1, 101):
        key = 'L' + str(segmentile)
        write_cursor.execute('''INSERT INTO secondLevelBaseProbabilitiesUnrolled (TermID, ShortFormID, Percentile, Probability) VALUES (%s, %s, %s, %s) ''', 
            [term_ID, short_form_ID, segmentile, row[key],]
        )
    conn.commit()
write_cursor.close()
