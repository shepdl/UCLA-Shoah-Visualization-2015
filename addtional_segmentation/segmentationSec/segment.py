from __future__ import division
import common.db as db
import json
import csv
from math import floor, ceil



# This is for only ShortFormID = 2, Even Testimonies and Pruned with SaturationScore >= 0.20
# And now, further pruned with TotSegment >= 40. 
query1 = """
SELECT * 
FROM testimoniesSaturationPruned2015 
"""

cursor1 = db.get_cursor()
cursor1.execute(query1)
testimony_details_pruned = {}
i=0
while True:
        row=cursor1.fetchone()
        if not row:
                break
        else:
                testimony_details_pruned[row["IntCode"]]={
                        "IntCode" : row["IntCode"],
                        "IntervieweeName" : row["IntervieweeName"],
                        "TotTaggedSegments" : row["TotTaggedSegments"],
                        "TotSegments" : row["TotSegments"],
                        "SaturationPercent" : row["SaturationPercent"],
                        "NormativityScore" : 0
                }
        i=i+1
cursor1.close()
testimonies = testimony_details_pruned


query = """
SELECT * 
FROM segmentKeywordsSecondParents2015b
WHERE IntCode = %s
"""

insert = """
INSERT INTO filledSegmentKeywordsSecondParents2015b
(IntCode, SegmentNumber, SegmentID, SegmentPercentile, TermID, TermLabel, SecondLevelParentID, ParentLabel)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

insertCursor = db.get_cursor()
for tmony in testimonies:
        if True: 
                tot_len = testimonies[tmony]["TotSegments"]
                print "For Testimony: " + str(tmony)
                print "Tot Len: " + str(tot_len)
                segmentile = range(tot_len + 1)
		for i in range(0,100):
                        if i==0:
                                l1 = floor(tot_len * i * 0.01)
                        else:
                                l1 = floor(tot_len * i * 0.01) + 1
                        r1 = floor(tot_len * (i + 1) * 0.01)

                        if l1-1 == r1:
                                l1 = r1
			for ind in range(int(l1), int(r1+1)):
				segmentile[ind] = i + 1
				
		cursor = db.get_cursor()
		cursor.execute(query, [tmony])
		previous = 0
		while True: 
			row = cursor.fetchone()
			if not row: 
				break
			else:
				current = row["SegmentNumber"]
				if current != previous and previous != 0:
					if current != previous + 1: 
						# Insert all previous values until current SegmentNumber.
						previous = previous + 1
						while previous < current:
							SegmentPercentile = segmentile[previous]
							insertCursor.execute(insert, (IntCode, previous, SegmentID, SegmentPercentile, TermID, TermLabel, FirstLevelParentID, ParentLabel))
							previous += 1
					
					# Insert current.
				
				# Extract all details.  
				IntCode = row["IntCode"]
				SegmentNumber = row["SegmentNumber"]
				SegmentID = row["SegmentID"]
				SegmentPercentile = segmentile[SegmentNumber]
				TermID = row["TermID"]
				TermLabel = row["TermLabel"]
				FirstLevelParentID = row["SecondLevelParentID"]
				ParentLabel = row["ParentLabel"]
					
				# Insert current
				insertCursor.execute(insert, (IntCode, SegmentNumber, SegmentID, SegmentPercentile, TermID, TermLabel, FirstLevelParentID, ParentLabel))			
				previous = row["SegmentNumber"]		

		cursor.close()
insertCursor.close()



