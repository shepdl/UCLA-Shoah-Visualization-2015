# In this code:
#	First, the segmentKeywords table will be read and the inTime and the outTimes recorded. 
# 	Second, the Intime and OutTimes are processed, taken the difference of and comparened with the rest of the in and the otimes within the same testimony. 
#		If the same, the testimony is recorded, else, not recorded. 
from __future__ import division
import common.db as db
import json
import datetime
import re
from math import floor, ceil


# All queries: 
query = """
SELECT IntCode, SegmentNumber, `SegInTime` ,  `SegOutTime` 
FROM  `segmentKeywordsTable2015` 
GROUP BY IntCode, SegmentNumber
"""

create_query = """
CREATE TABLE IF NOT EXISTS evenSegmentTestimonies2015 (
IntCode VARCHAR(10)
)
"""

insert_query = """
INSERT INTO evenSegmentTestimonies2015 (IntCode) VALUES (%s)
"""
# Supporting Functions: 
def getDiff(aTime, bTime):
	# Assuming: Hours:Minues:Seconds:MicroSeconds ISO format. 
	pattern = "([0-9])+:([0-9])+:([0-9])+:([0-9])+"
	m = re.search(pattern, aTime)
	aTime = m.group(0)
	m = re.search(pattern, bTime)
	bTime = m.group(0)
	aTime = datetime.datetime.strptime(aTime, "%H:%M:%S:%f") 
	bTime = datetime.datetime.strptime(bTime, "%H:%M:%S:%f")
	return (bTime - aTime)

evenSegmentTestimonies = {}
unevenFlag = 0
prevIntCode = 0
cursor = db.get_cursor()
cursor.execute(query)
while True: 
	row = cursor.fetchone()
	if not row:
		if unevenFlag == 0: 
			evenSegmentTestimonies[prevIntCode] = prevIntCode
		break
	if row: 
		currIntCode = row["IntCode"]	
		if currIntCode != prevIntCode:
			print("---" + str(prevIntCode) + " --" + str(unevenFlag))
			if unevenFlag == 0:
				evenSegmentTestimonies[prevIntCode] = prevIntCode
			unevenFlag = 0
			diff = getDiff(row["SegInTime"], row["SegOutTime"])
			prevIntCode = currIntCode
			continue

		# Check diff: 
		currDiff = getDiff(row["SegInTime"], row["SegOutTime"])
		if currDiff != diff:
			 unevenFlag = 1
		prevIntCode = currIntCode
cursor.close()

# Creating the table: 
cursor = db.get_cursor()
cursor.execute(create_query)


# Insert into the created table:
cursor2 = db.get_cursor()
for tmony in evenSegmentTestimonies:
	cursor2.execute(insert_query, [str(evenSegmentTestimonies[tmony])])

conn = db.get_connection()
conn.commit()
cursor.close()
cursor2.close()

