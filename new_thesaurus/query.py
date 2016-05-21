
# This code is to generate a new thesaurus (TWO PASS Code): 
# 	- Match the thesaurus keywords and the segment keywords by the keyword text.
# 	- and reassign keyword ids!

import common.db as db 
import re

query = """
SELECT *
FROM thesaurus2015
"""

# Pass One: To get new unique IDs to each of teh terms matched by text. 
cursor = db.get_cursor()
cursor.execute(query)
newThesaurus = {}
backMap = {}
wordCount = 1
while True: 
	row = cursor.fetchone()
	if not row: 
		break
	if row:
		splice = row["TermLabel"].strip() 
		if splice not in newThesaurus: 
			newThesaurus[splice] = {
				"TermLabel": row["TermLabel"].strip(),
				"ThesaurusID": row["ThesaurusID"],
				"ThesaurusType": row["ThesaurusType"],
				"KeywordCount": row["KeywordCount"],
				"TypeID": row["TypeID"],
				"IsParent": row["IsParent"],
				"KWDefinition": row["KWDefinition"], 
				"NewID": wordCount,
				"OldID": row["TermID"], # For just in case. 				
				"ParentLabel": row["ParentTermLabel"].strip(),
				"ParentID": row["ParentTermID"],
				"NewParentID": ""
			}
			 
			wordCount += 1	
cursor.close()
print("New thesaurus created.")

# Pass Two: to set unique IDs to parents of each term by back checking 
# Issue faced: Parse out "(CONTAINER ONLY)"  in ParentLabel to find actual parent. (Often First Level Parent).
# 		If not found even then, drop thesaurus entry. No keyword with "%(CONTAINER ONLY)%" found in any of the testimony segments.
# 		"This is a structural element in the hierarchy, not..." (defn of ^)
newThesaurusIntm = newThesaurus.copy()

for r in newThesaurus:
	if re.sub("\(CONTAINER ONLY\)", "", newThesaurus[r]["ParentLabel"]).strip() not in newThesaurusIntm:
		print(re.sub("\(CONTAINER ONLY\)", "", newThesaurus[r]["ParentLabel"]))
	else:
		#print(newThesaurusIntm[re.sub("\(CONTAINER ONLY\)", "", newThesaurus[r]["ParentLabel"])]["NewID"])
		newThesaurus[r]["NewParentID"] = newThesaurusIntm[re.sub("\(CONTAINER ONLY\)", "", newThesaurus[r]["ParentLabel"]).strip()]["NewID"]	
# Insert the new thesaurus to table: 
insert_query = """
INSERT into thesaurusNew2015 (TermID, TermLabel, ParentTermID, ParentTermLabel, OldTermID, ThesaurusID, ThesaurusType, KeywordCount, TypeID, IsParent, KWDefinition) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
"""
print("Insertion started.")
cursor = db.get_cursor()
for record in newThesaurus:
	r = newThesaurus[record]
	cursor.execute(insert_query, (r["NewID"], r["TermLabel"], r["NewParentID"], r["ParentLabel"], r["OldID"], r["ThesaurusID"], r["ThesaurusType"], r["KeywordCount"], r["TypeID"], r["IsParent"], r["KWDefinition"]))

conn = db.get_connection()
conn.commit()
cursor.close()
"""

# Insert the new segment keywords to table: 
query = """
SELECT IntCode, Keyword, KeywordID, SegmentID, SegmentNumber 
FROM segmentKeywordsTable2015
"""

insert_query = """
INSERT INTO segmentKeywordsNew2015 (IntCode, SegmentID, SegmentNumber, KeywordIDNew, Keyword) 
VALUES(%s, %s, %s, %s, %s)
"""


print("Started thesaurus traversal.")
cursor2 = db.get_cursor()
insert_cursor = db.get_cursor()
cursor2.execute(query)
count = 0
print("Query exected.") 
while True:
	row = cursor2.fetchone()
	if not row: 
		break
	if row:
		IntCode = row["IntCode"]
		SegmentID = row["SegmentID"]
		SegmentNumber = row["SegmentNumber"]
		KeywordID = row["KeywordID"]
		Keyword = row["Keyword"]
		if re.sub("\(PIQ\)", "", row["Keyword"]).strip() not in newThesaurus:
			NewID = -1 # Skip keywords NOT in thesaurus. i.e. the "stray" keywords. (Code expanded out for explanation.) 
		else: 
			NewID = newThesaurus[re.sub("\(PIQ\)", "", row["Keyword"]).strip()]["NewID"]
			# Insert to the new segment keywords table: If NewID -1, do not insert. 
			insert_cursor.execute(insert_query, (IntCode, SegmentID, SegmentNumber, NewID, Keyword))		
			
	if (count % 5 == 0):
		print count
	count += 1
conn = db.get_connection()
conn.commit()
cursor2.close()
insert_cursor.close()



