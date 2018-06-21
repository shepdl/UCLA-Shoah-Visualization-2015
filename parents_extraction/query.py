# In this code: 
# 	First, we will have to extract all the first level parents. 
# 	Second, based on that, we ill have to extract the second level parents too. 
#	Third, using teh first and the second level parents, trace backwards to the first and the second 
#			levels to collect the parents 'Hit' in two lists (first list and second list)
#			for each of the segment-keywords. 

from __future__ import division
import common.db as db
import json
import xmltodict
from math import floor, ceil

# Extracting the First Level Parents: 
# Important Note!: primary node has label 32582 NOT -1 in thesaurusNew2015

query = """
SELECT DISTINCT  `TermID` ,  `TermLabel` 
FROM  `thesaurusNew2015` 
WHERE  `ParentTermID` = 32582
"""

cursor = db.get_cursor()
cursor.execute(query)
primary_parents = {}
primary_parents_list = []
while True:
        row = cursor.fetchone()
        if not row:
                break
        if row:
                primary_parents[row["TermID"]] = row["TermLabel"]
                primary_parents_list.append(str(row["TermID"]))
cursor.close()
print(len(primary_parents))

          
         
# Extracting the second level parents: 
cursor = db.get_cursor()
refinedPrimaryParentsList = ', '.join(str(a) for a in primary_parents_list)
query = "SELECT DISTINCT  `TermID` ,  `TermLabel` FROM  `thesaurusNew2015` WHERE  `ParentTermID` in ({0})".format(refinedPrimaryParentsList) 
cursor.execute(query)
secondary_parents = {}
secondary_parents_list = []
while True: 
	row = cursor.fetchone()
	if not row: 
		break 
	if row: 	
		secondary_parents[row["TermID"]] = row["TermLabel"]
		secondary_parents_list.append(str(row["TermID"]))
print(len(secondary_parents))
cursor.close() 
    
refinedSecondaryParentsList = ', '.join(str(a) for a in secondary_parents_list)



# Write the First and the Second Level Parents to Table: 
# Just for viewing. 
insert_query = """
INSERT INTO firstLevelParents2015 (TermID, TermLabel) values (%s, %s)
"""
cursor = db.get_cursor()
cursor.execute('TRUNCATE TABLE firstLevelParents2015')
for TermID in primary_parents:
	cursor.execute(insert_query, (TermID, primary_parents[TermID]))
conn = db.get_connection()
conn.commit()
cursor.close()

print "First level parents inserted"


insert_query = """
INSERT INTO secondLevelParents2015 (TermID, TermLabel) values (%s, %s)
"""
cursor = conn.cursor()
cursor.execute('TRUNCATE TABLE secondLevelParents2015')
for TermID in secondary_parents:
        cursor.execute(insert_query, (TermID, secondary_parents[TermID]))
conn.commit()
cursor.close()

print "Second level parents inserted"


# Now, climbing the tree to look for the first and second level parents. 
# And append to list of firstLevelHits  and secondLevelHits of every segment keywords. 

# Get all IntCodes. 
query = "SELECT IntCode, IntervieweeName FROM testimonies2015" 
cursor = db.get_cursor();
cursor.execute(query)
testimonies = {}
while True: 
	row = cursor.fetchone()
	if not row:
		break
	if row: 
		testimonies[row["IntCode"]]  = row["IntervieweeName"]

db.get_connection().commit()
cursor.close()

print "Loaded interviewee names"


# Process Testimonies one at a time. 
def findParents(TermID, parentHits, secondaryHits, checked):
	if TermID not in checked:
		checked.append(TermID)
		if str(TermID) in primary_parents_list:
			if str(TermID) not in parentHits:
				parentHits.append(TermID)
		else:	
			query = "SELECT DISTINCT `ParentTermID`, `ParentTermLabel` FROM `thesaurusNew2015` WHERE TermID = %s"
			cursor = db.get_cursor()	
			cursor.execute(query, [TermID])
			set  = {}
			while True: 
				row = cursor.fetchone()
				if not row:
					break
				if row:
					set[str(row["ParentTermID"])] = row["ParentTermLabel"]
                        db.get_connection().commit()
			cursor.close()

			for ParentTermID in set:
				if str(ParentTermID) in primary_parents_list:
					if str(ParentTermID) not in parentHits:
						parentHits.append(ParentTermID)
					if str(TermID) not in secondaryHits:
						secondaryHits.append(TermID)
				else:
					parentHits, secondaryHits = findParents(ParentTermID, parentHits, secondaryHits, checked)
	return parentHits, secondaryHits
			


select_query = """
				SELECT SegmentNumber, SegmentID, KeywordID AS TermID, Keyword AS TermLabel
				FROM  `segmentKeywordsNew2015` 
				WHERE `IntCode` = %s
				ORDER BY `SegmentID`
			"""


count = 1

print "Writing information about testimonies and segments ..."
cursor = db.get_cursor()
cursor.execute('TRUNCATE TABLE segmentKeywordsFirstParents2015')
cursor.execute('TRUNCATE TABLE segmentKeywordsSecondParents2015b')
for tmony in testimonies: 
	if(True): 
		cursor = db.get_cursor()
		cursor.execute(select_query, [str(tmony)])
	
		while True: 
			row = cursor.fetchone()
			if not row: 
				break
			if row:
				SegmentNumber = row["SegmentNumber"]
				SegmentID = row["SegmentID"] 
				TermID = row["TermID"]
				TermLabel = row["TermLabel"]

				# Processing for one keyword:
				insert_queryFirst = """
								INSERT INTO segmentKeywordsFirstParents2015 
								(IntCode, SegmentNumber, SegmentID, TermID, TermLabel, FirstLevelParentID, ParentLabel) 
								VALUES (%s, %s, %s, %s, %s, %s, %s)
								"""
				insert_querySecond = """
                                    INSERT INTO segmentKeywordsSecondParents2015b 
                                    (IntCode, SegmentNumber, SegmentID, TermID, TermLabel, SecondLevelParentID, ParentLabel) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """
				select_query2 = """
                                        SELECT TermLabel FROM thesaurusNew2015 WHERE TermID = %s
                                """
				firstLevelHits, secondLevelHits = findParents(TermID, [], [], [])	
				for parent in firstLevelHits:
					cursor2 = db.get_cursor()
					cursor2.execute(select_query2, [parent])
					row = cursor2.fetchone()
					ParentLabel = "None"
					if row:
						ParentLabel = row["TermLabel"]
                                        db.get_connection().commit()
					cursor2.close()
					cursor3 = db.get_cursor()
					cursor3.execute(insert_queryFirst, (tmony, SegmentNumber, SegmentID, TermID, TermLabel, parent, ParentLabel))
                                        db.get_connection().commit()
					cursor3.close()
				for parent in secondLevelHits:
                                    cursor2 = db.get_cursor()
                                    cursor2.execute(select_query2, [parent])
                                    row = cursor2.fetchone()
                                    ParentLabel = "None"
                                    if row:
                                        ParentLabel = row["TermLabel"]
                                    db.get_connection().commit()
                                    cursor2.close()
                                    cursor3 = db.get_cursor()
                                    cursor3.execute(insert_querySecond, (tmony, SegmentNumber, SegmentID, TermID, TermLabel, parent, ParentLabel))
                                    db.get_connection().commit()
                                    cursor3.close()
                db.get_connection().commit()
		cursor.close()
	count = count + 1
        if count > 0 and count % 1000 == 0:
            print "{} testimonies completed".format(count)


