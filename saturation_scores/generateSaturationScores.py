# This code: 
# First, the all of the testimonies and their details are collectedi from the EVEN segments testimonies table. 
# Second, the saturation scores and the unique_tags are gotten from the segnment-keywords table. 
# Third, 
from __future__ import division
import common.db as db
import json

query = """
SELECT * from evenSegmentTestimonies2015
"""
cursor = db.get_cursor()
cursor.execute(query)
evenTestimoniesList = []
while True: 
	row = cursor.fetchone()
	if not row:
		break
	if row: 
		evenTestimoniesList.append(row["IntCode"])
cursor.close()
refinedEvenTestimoniesList = ', '.join(a for a in evenTestimoniesList)

query = """
SELECT ES.IntCode AS IntCode, MAX( ES.SegmentNumber ) AS TotSegments, CS.ShortFormID AS ShortFormID
FROM segmentKeywordsTable2015 AS ES, testimonies2015 AS CS
WHERE ES.IntCode = CS.IntCode
AND CS.ShortFormID = 2
AND ES.IntCode in ({0})
GROUP BY ES.IntCode
"""
cursor = db.get_cursor()
query = query.format(refinedEvenTestimoniesList)
cursor.execute(query)
testimony_details={}
i=1
while True:
	row=cursor.fetchone()
	if not row:
		break
	if row:
		testimony_details[row["IntCode"]]={
			"IntervieweeName" : [], 
			"IntCode" : [], #
			"TotTaggedSegments" : [],
			"TotSegments" : [], #
			"SaturationPercent":[],
		}
		testimony_details[row["IntCode"]]["IntCode"].append(row["IntCode"])
		testimony_details[row["IntCode"]]["TotSegments"].append(row["TotSegments"])
		i=i+1			
cursor.close()

# Assumptions:
# None of the sgements are filled in. And the total number of segments with the tags are directly accounted for. 
query="""
SELECT ES.IntCode AS IntCode, COUNT( DISTINCT  ES.SegmentNumber ) AS TotTaggedSegments,  CS.IntervieweeName AS IntervieweeName
FROM  `segmentKeywordsTable2015` AS ES, `testimonies2015` AS CS
WHERE ES.IntCode = CS.IntCode
AND ES.IntCode in ({0})
GROUP BY  ES.IntCode 
"""
query = query.format(refinedEvenTestimoniesList)
insert_query = """
INSERT INTO testimoniesSaturation2015 (Intcode, IntervieweeName, TotTaggedSegments, TotSegments, SaturationPercent)
VALUES (%s, %s, %s, %s, %s)
"""

cursor = db.get_cursor()
cursor2 = db.get_cursor()
cursor.execute(query)
j=1
countArray = []
for index in range (0,101):
	countArray.append(0)
testimony_details_20 = {}
while True:
	row = cursor.fetchone()
	if not row:
		break
	if row["IntCode"] in testimony_details:
		# Completing the testimony_details: 
		testimony_details[row["IntCode"]]["TotTaggedSegments"].append(row["TotTaggedSegments"])
		testimony_details[row["IntCode"]]["IntervieweeName"].append(row["IntervieweeName"])
		# Derived data:
		saturation_percent=float(row["TotTaggedSegments"])/float(testimony_details[row["IntCode"]]["TotSegments"][0])
		testimony_details[row["IntCode"]]["SaturationPercent"].append(saturation_percent)
		# Writing to database:
		cursor2.execute(insert_query, (testimony_details[row["IntCode"]]["IntCode"][0],
						testimony_details[row["IntCode"]]["IntervieweeName"][0],
						testimony_details[row["IntCode"]]["TotTaggedSegments"][0],
						testimony_details[row["IntCode"]]["TotSegments"][0],
						float(testimony_details[row["IntCode"]]["SaturationPercent"][0])));		
		countArray[int(saturation_percent*100)]+=1
		if countArray[int(saturation_percent*100)]<=20:	
			if str(int(saturation_percent*100)) not in testimony_details_20:
				testimony_details_20[str(int(saturation_percent*100))]={}
			testimony_details_20[str(int(saturation_percent*100))][row["IntCode"]] = {
					"Intcode": row["IntCode"],
					"IntervieweeName": row["IntervieweeName"],
					"TotTaggedSegments": row["TotTaggedSegments"],
					"TotSegments": testimony_details[row["IntCode"]]["TotSegments"][0],
					"SaturationPercent": saturation_percent
			}
		j=j+1	

conn = db.get_connection()
conn.commit()
cursor2.close()
cursor.close()

jsondata = json.dumps(testimony_details) 
fd = open('demo_dumps.json', 'w')
fd.write(jsondata)
fd.close()

# Write testimonies_details_20 set to file;
jsondata = json.dumps(testimony_details_20)
fd = open("testimony_details_20.json", "w")
fd.write(jsondata)
fd.close()





