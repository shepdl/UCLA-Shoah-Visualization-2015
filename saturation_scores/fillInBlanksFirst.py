from common import db


# find testimonies with > 40% saturation
#
# find all testimonies

table_name = 'segmentKeywordsFirstParents2015filled'


print "Clearing table ..."
create_table_cursor = db.get_cursor()
create_table_cursor.execute('''DROP TABLE IF EXISTS {table_name}'''.format(**{'table_name' : table_name,}))
create_table_cursor.execute('''CREATE TABLE {table_name}
    (
        SegmentNumber INT,
        SegmentID INT,
        TermID INT,
        TermLabel VARCHAR(255),
        FirstLevelParentID INT,
        ParentLabel VARCHAR(255),
        IntCode INT
    )
    '''.format(**{'table_name' : table_name,})
)
print 'Table cleared'

get_testimony_segments = """
    SELECT SegmentNumber, SegmentID, TermID, TermLabel, FirstLevelParentID, ParentLabel, IntCode
    FROM segmentKeywordsFirstParents2015
    ORDER BY IntCode, SegmentNumber
"""

segments_cursor = db.get_cursor()
print "Executing load query ..."
segments_cursor.execute(get_testimony_segments)
print "Executed load query"

segment_1 = segments_cursor.fetchone()
current_testimony_id = segment_1['IntCode']
current_segment = segment_1['SegmentNumber']
current_segment_id = segment_1['SegmentID']
current_segment_keywords = [
    [
        segment_1['TermID'],
        segment_1['TermLabel'],
        segment_1['FirstLevelParentID'],
        segment_1['ParentLabel'],
    ]
]

insert_query = """INSERT INTO {table_name} 
    (SegmentNumber, SegmentID, TermID, TermLabel, FirstLevelParentID, ParentLabel, IntCode)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""".format(**{'table_name' : table_name,})
insert_cursor = db.get_cursor()
while True:
    segment_2 = segments_cursor.fetchone()
    if not segment_2:
        for term in current_segment_keywords:
            insert_cursor.execute(insert_query, (
                segment_number, current_segment_id,
                term[0], term[1], term[2], term[3],
                current_testimony_id,
            ))
        break
    if segment_2['IntCode'] == current_testimony_id:
        if segment_2['SegmentNumber'] == current_segment:
            current_segment_keywords.append([
                segment_2['TermID'],
                segment_2['TermLabel'],
                segment_2['FirstLevelParentID'],
                segment_2['ParentLabel'],
            ])
        else:
            for segment_number in range(current_segment, segment_2['SegmentNumber']):
                for term in current_segment_keywords:
                    insert_cursor.execute(insert_query, (
                        segment_number, current_segment_id,
                        term[0], term[1], term[2], term[3],
                        current_testimony_id,
                    ))
            current_segment_keywords = [
                [
                    segment_2['TermID'],
                    segment_2['TermLabel'],
                    segment_2['FirstLevelParentID'],
                    segment_2['ParentLabel'],
                ]
            ]
            current_segment = segment_2['SegmentNumber']
            current_segment_id = segment_2['SegmentID']

    else:
        # insert last one
        for term in current_segment_keywords:
            insert_cursor.execute(insert_query, (
                segment_number, current_segment_id,
                term[0], term[1], term[2], term[3],
                current_testimony_id,
            ))
        # set current_segment, current_testimony_kid
        current_segment_keywords = [
            [
                segment_2['TermID'],
                segment_2['TermLabel'],
                segment_2['FirstLevelParentID'],
                segment_2['ParentLabel'],
            ]
        ]
        current_segment = segment_2['SegmentNumber']
        current_testimony_id = segment_2['IntCode']
        current_segment_id = segment_2['SegmentID']

db.get_connection().commit()
insert_cursor.close()

print 'Complete'

