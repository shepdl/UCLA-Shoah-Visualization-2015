import common.db as db
import csv
import json
from __future__ import division
from math import floor, ceil

# Getting all the unique parents first. And then creating the parents table 
# First, processing only the first level parents.
query1 = """
SELECT TermID
FROM  `secondLevelParents2015` 
"""
cursor1 = db.get_cursor()
cursor1.execute(query1)
parentsTable = {}
while True:
	row=cursor1.fetchone()
	if not row:
		break
	else:
		print row["TermID"]
		i = 1
		parentsTable[row["TermID"]] = {}
		for i  in range(1,101):
			parentsTable[row["TermID"]][i] = 0
cursor1.close()

# All the parent values have now been initialized.
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

# The steps to proceed with nest for you would be!: 
# Step 1: For each testimony
# Step 2: And For each "1%" of it from [1 to 100]
# Step 3: small_Query again for the DICTINCT parent between l1 and r1. 
# Step 4: For each of those parents make +1 in the parentTable

testimonies = testimony_details_pruned
query1 = """
SELECT SecondLevelParentID
FROM copyFilledSegmentKeywordsSecondParents2015b
WHERE IntCode = %s
AND SegmentPercentile = %s
"""
count = 1
for tmony in testimonies:
        if True:
                tot_len = testimonies[tmony]["TotSegments"]
                for segmentile in range(1,101):
                        cursor1 = db.get_cursor()
                        cursor1.execute(query1,(str(tmony), str(segmentile)))
                        parentHits = []
                        while True:
                                row = cursor1.fetchone()
                                if not row:
                                        break
                                else:
                                        parentHits.append(row["SecondLevelParentID"])
                        uniqueHits = set(parentHits)
                        cursor1.close()

                        for parent in uniqueHits:
                                if parent:
                                        parentsTable[parent][segmentile] += 1
        count += 1

# Create parentsProbabilityTable.
tot_tmonies = len(testimonies)
parentsProbabilityTable = parentsTable
for parID in parentsProbabilityTable:
	for i in range(1,101):
		parentsProbabilityTable[parID][i] = parentsProbabilityTable[parID][i]/tot_tmonies


query1 = """
insert into secondLevelBaseProbabilities2015
values %r
"""
cursor1 = db.get_cursor()
print(len(parentsProbabilityTable))
parS = parentsProbabilityTable
for parId in parS:
	varlist = []
	varlist.append(str(parId))
	for i in range(1,101):
		varlist.append(str(parS[parId][i]))
	query2 = query1 % (tuple(varlist),)
	cursor1.execute(query2)
conn = db.get_connection()
conn.commit()
cursor1.close()




