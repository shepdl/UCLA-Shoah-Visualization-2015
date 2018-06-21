import common.db as db


cursor = db.get_cursor()
print "Resetting table ..."
cursor.execute("""DROP TABLE IF EXISTS secondLevelBaseProbabilities""")
segmentile_columns = ['L{}'.format(x) for x in range(1, 101)]
cursor.execute("""CREATE TABLE secondLevelBaseProbabilities (TermID INT, KeywordLabel VARCHAR(100), ShortFormID INT, {} FLOAT)""".format(' FLOAT, '.join(segmentile_columns)))
print "Table reset"

print "Loading data ..."
query = """
SELECT 
    totalKeywordsBySegment.ShortFormID, 
    totalKeywordsBySegment.segmentile, 
    SecondLevelParentID, 
    keywordCountsBySegment.keywordCount, 
    keywordCountsBySegment.keywordCount / totalKeywordsBySegment.totalKeywords AS probability

FROM (
    -- Total keywords by segment and ShortFormID
    SELECT t.ShortFormID, ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS totalKeywords
    FROM segmentKeywordsSecondParents2015filled AS sk
    JOIN (
    	SELECT sk.IntCode, MAX(SegmentNumber) AS total
        FROM segmentKeywordsSecondParents2015filled AS sk
	    GROUP BY sk.IntCode
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    JOIN testimonies2015_include AS t ON t.IntCode = sk.IntCode
    GROUP BY t.ShortFormID, segmentile
) AS totalKeywordsBySegment

JOIN (
	SELECT t.ShortFormID, ROUND(sk.SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS keywordCount, sk.SecondLevelParentID
    FROM segmentKeywordsSecondParents2015filled AS sk
    JOIN (
    	SELECT sk.IntCode, MAX(SegmentNumber) AS total
        FROM segmentKeywordsSecondParents2015filled AS sk
	    GROUP BY sk.IntCode
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    JOIN testimonies2015_include AS t ON t.IntCode = sk.IntCode
    GROUP BY t.ShortFormID, segmentile, sk.SecondLevelParentID
) AS keywordCountsBySegment ON totalKeywordsBySegment.ShortFormID = keywordCountsBySegment.ShortFormID AND totalKeywordsBySegment.segmentile = keywordCountsBySegment.segmentile

GROUP BY keywordCountsBySegment.ShortFormID, keywordCountsBySegment.segmentile, keywordCountsBySegment.SecondLevelParentID
ORDER BY keywordCountsBySegment.ShortFormID, keywordCountsBySegment.SecondLevelParentID, keywordCountsBySegment.segmentile
"""
cursor.execute(query)


print "Data loaded"

insert_cursor = db.get_cursor()

row = cursor.fetchone()
while True:
    if not row:
        break

    current_short_form_id = row['ShortFormID']
    current_segmentile = row['segmentile']
    current_parent_id = row['SecondLevelParentID']
    accumulating_parent_id = current_parent_id
    values = [current_parent_id, current_short_form_id,]
    segmentile_values = {_ : 0 for _ in range(0, 100)}

    while current_parent_id == accumulating_parent_id:
        segmentile_values[row['segmentile']] = row['probability']
        row = cursor.fetchone()
        if not row:
            break
        current_parent_id = row['SecondLevelParentID']
        
    values = values + [segmentile_values[x] for x in range(0, 100)]
    print 'Found all {} values for ParentID {} and will move on to {}'.format(len(values) - 2, accumulating_parent_id, current_parent_id)
    accumulating_parent_id = current_parent_id


    insert_cursor.execute("""INSERT INTO secondLevelBaseProbabilities (TermID, ShortFormID, {0}) VALUES ({1})""".format(
        ', '.join(segmentile_columns), 
        ', '.join(['%s' for _ in values])
    ), values)
    


db.get_connection().commit()
insert_cursor.close()
cursor.close()

print "Complete!"

