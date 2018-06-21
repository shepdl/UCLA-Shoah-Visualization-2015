
from __future__ import division
import common.db as db
import json
import csv
from math import floor, ceil

# Getting all the unique parents first. And then creating the parents table. 
# First, processing only the first level parents.
query1 = """
SELECT TermID
FROM  `firstLevelParents2015` 
"""

cursor1 = db.get_cursor()
cursor1.execute(query1)

parentsTable = {}
#fieldnames = []
while True:
	row=cursor1.fetchone()
	if not row:
		break
	else:
		i = 1
		parentsTable[row["TermID"]] = {}
		for i  in range(1,101):
			parentsTable[row["TermID"]][i] = 0
cursor1.close()


# print "\n ### \n"
# print(len(parentsTable))
# print "\n ### \n"

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

# The steps to proceed with next for you would be!: 
# Step 1: For each testimony
# Step 2: And For each "1%" of it from [1 to 100]  
# Step 3: small_Query again for the DICTINCT parent between l1 and r1. 
# Step 4: For each of those parents make +1 in the parentTable

testimonies = testimony_details_pruned

query1 = """
SELECT FirstLevelParentID
FROM filledSegmentKeywordsFirstParents2015
WHERE IntCode = %s
AND SegmentPercentile = %s
"""

count = 1 
for tmony in testimonies:
	if True:	 
		tot_len = testimonies[tmony]["TotSegments"]
		# print "#" + str(count) + ": For testimony: " + str(tmony)
		# print "The total length of the testimony is : " + str(tot_len)	
		for segmentile in range(1,101):
			
			cursor1 = db.get_cursor()
			cursor1.execute(query1,(str(tmony), str(segmentile)))
			parentHits = []
			while True:
				row = cursor1.fetchone()
				if not row:
					break
				else:
					parentHits.append(row["FirstLevelParentID"])	
			uniqueHits = set(parentHits)
			cursor1.close()

			for parent in uniqueHits:
				if parent: 
					parentsTable[parent][segmentile] += 1	
	count += 1

# Now that the COUNT parentsTable has been created: 
# Create parentsProbabilityTable. Wriet to file. 

tot_tmonies = len(testimonies)
parentsProbabilityTable = parentsTable

keywordCounts = []

for i in range(1,101):
    thisSegmentSum = 0
    for parID in parentsProbabilityTable:
        thisSegmentSum += parentsProbabilityTable[parID][i]

    keywordCounts.append(thisSegmentSum)
        

for parID in parentsProbabilityTable:
    for i in range(1,101):
        parentsProbabilityTable[parID][i] = parentsProbabilityTable[parID][i] / keywordCounts[i - 1]

for i in range(1, 101):
    total_this_moment = 0.0
    for parID in parentsProbabilityTable:
        total_this_moment += parentsProbabilityTable[parID][i]
    if total_this_moment != 1.0:
        # print "Total at {} only adds up to {}".format(i, total_this_moment)
        pass


query1 = """
insert into firstLevelBaseProbabilities2015 
values ({})
"""
cursor1 = db.get_cursor()
# cursor.execute('CREATE TABLE IF NOT EXISTS firstLevelBaseProbabilities ()')
cursor1.execute('DROP TABLE IF EXISTS firstLevelBaseProbabilities2015')
cursor1.execute('CREATE TABLE firstLevelBaseProbabilities2015 (TermID INT, TermLabel VARCHAR(255), {} FLOAT)'.format(' FLOAT, '.join([
    'L{}'.format(x) for x in range(1, 101)
])
))
# cursor1.execute('TRUNCATE TABLE firstLevelBaseProbabilities201')
parS = parentsProbabilityTable
for parID, segments in parentsProbabilityTable.items():
    ordered_segments = [segments[x] for x in sorted(segments)]
    print query1.format(', '.join([str(x) for x in [parID, '',] + [x for x in ordered_segments]]))
    cursor1.execute(query1.format(', '.join([str(x) for x in [parID, "''",] + [x for x in ordered_segments]])))

# for i in range(1,101):
# 	varlist = []
# 	varlist.append(str(i))
# 	for parId in parS:
# 		varlist.append(str(parS[parId][i]))
# 	query2 = query1 % (tuple(varlist),)
# 	cursor1.execute(query2)

conn = db.get_connection()
conn.commit()
cursor1.close()




