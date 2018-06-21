import common.db as db

conn = db.get_connection()
cursor = db.get_cursor()

print 'Clearing database ...'
cursor.execute('''DROP TABLE IF EXISTS uniqueness_scores_first_level ''')
cursor.execute('''DROP TABLE IF EXISTS uniqueness_scores_second_level ''')
cursor.execute('''CREATE TABLE uniqueness_scores_first_level  (IntCode INT, Score FLOAT)''')
cursor.execute('''CREATE TABLE uniqueness_scores_second_level  (IntCode INT, Score FLOAT)''')

max_segments = {}
print 'Finding maximum segments ...'
cursor.execute('''SELECT skf.IntCode, MAX(skf.SegmentNumber) AS max_seg FROM segmentKeywordsFirstParents2015Filled skf 
        JOIN testimonies2015_include AS ti ON ti.IntCode = skf.IntCode
        GROUP BY IntCode
''')
while True:
    row = cursor.fetchone()
    if not row:
        break
    max_segments[row['IntCode']] = row['max_seg']


print 'Running first level normativities ...'
cursor.execute('''SELECT * FROM firstLevelBaseProbabilities ''')
first_level_base_probabilities = {}
while True:
    row = cursor.fetchone()
    if not row:
        break
    first_level_base_probabilities.setdefault(row['ShortFormID'], {})
    first_level_base_probabilities[row['ShortFormID']].setdefault(row['TermID'], {})
    for segmentile in range(1, 101):
        segmentile_key = 'L' + str(segmentile)
        first_level_base_probabilities[row['ShortFormID']][row['TermID']][segmentile] = row[segmentile_key]
    
cursor.execute('''SELECT f.IntCode, t.ShortFormID, SegmentNumber, FirstLevelParentID FROM segmentKeywordsFirstParents2015filled AS f JOIN testimonies2015_include AS t ON t.IntCode = f.IntCode ORDER BY IntCode, SegmentNumber''')
write_cursor = db.get_cursor()
current_testimony = None
current_testimony_score = 0.0
segments_per_testimony = 0
while True:
    row = cursor.fetchone()
    # if not row:
    #     write_cursor.execute('''INSERT INTO uniqueness_scores_first_level (IntCode, Score) VALUES (%s, %s)''', [current_testimony, current_testimony_score,])
    #     break
    try:
        if row['IntCode'] != current_testimony and current_testimony is not None:
            # print 'Writing {} (Score: {})'.format(current_testimony, current_testimony_score)
            if current_testimony_score == 0.0:
                print '{} {} {}'.format(row['IntCode'], segments_per_testimony, current_testimony_score)
            write_cursor.execute('''INSERT INTO uniqueness_scores_first_level (IntCode, Score) VALUES (%s, %s)''', [current_testimony, current_testimony_score,])
            current_testimony = row['IntCode']
            current_testimony_score = 0.0
            segments_per_testimony = 0
        if current_testimony is None:
            current_testimony = row['IntCode']

    except TypeError as ex:
        write_cursor.execute('''INSERT INTO uniqueness_scores_first_level (IntCode, Score) VALUES (%s, %s)''', [current_testimony, current_testimony_score,])
        break

    segments_per_testimony += 1

    segment_number = int(max(round((float(row['SegmentNumber']) / float(max_segments[row['IntCode']]) * 100)), 1))
    keyword_segment_probability = first_level_base_probabilities[row['ShortFormID']][ row['FirstLevelParentID'] ][
            segment_number
        ]
    if keyword_segment_probability == 0.0 and segment_number < 100:
        keyword_segment_probability = first_level_base_probabilities[row['ShortFormID']][ row['FirstLevelParentID'] ][
                segment_number + 1
        ]
        if keyword_segment_probability == 0.0:
            keyword_segment_probability = first_level_base_probabilities[row['ShortFormID']][ row['FirstLevelParentID'] ][
                    segment_number - 1
            ]
    if keyword_segment_probability == 0.0:
        print '{} (ShortForm: {}) segment # {}/{} (={})'.format(row['IntCode'], row['ShortFormID'], row['SegmentNumber'], max_segments[row['IntCode']], segment_number)
        continue
    current_testimony_score += 1.0 / keyword_segment_probability
    # current_testimony_readings[
    #     row['SegmentNumber'] / max_segments[current_testimony]
    # ] = 1.0 / first_level_base_probabilities[
    #         row['ShortFormID']][row['FirstLevelParentID']
    #     ]

conn.commit()


print 'Running second level normativities ...'
cursor.execute('''SELECT * FROM secondLevelBaseProbabilities ''')
second_level_base_probabilities = {}
while True:
    row = cursor.fetchone()
    if not row:
        break
    second_level_base_probabilities.setdefault(row['ShortFormID'], {})
    second_level_base_probabilities[row['ShortFormID']].setdefault(row['TermID'], {})
    for segmentile in range(1, 101):
        segmentile_key = 'L' + str(segmentile)
        second_level_base_probabilities[row['ShortFormID']][row['TermID']][segmentile] = row[segmentile_key]
    
cursor.execute('''SELECT f.IntCode, t.ShortFormID, SegmentNumber, SecondLevelParentID FROM segmentKeywordsSecondParents2015Filled AS f JOIN testimonies2015_include AS t ON t.IntCode = f.IntCode ORDER BY IntCode, SegmentNumber''')
write_cursor = db.get_cursor()
current_testimony = None
current_testimony_score = 0.0
while True:
    row = cursor.fetchone()
    if not row:
        write_cursor.execute('''INSERT INTO uniqueness_scores_second_level (IntCode, Score) VALUES (%s, %s)''', [current_testimony, current_testimony_score,])
        break
    if row['IntCode'] != current_testimony and current_testimony is not None:
        write_cursor.execute('''INSERT INTO uniqueness_scores_second_level (IntCode, Score) VALUES (%s, %s)''', [current_testimony, current_testimony_score,])
        current_testimony = row['IntCode']
        current_testimony_score = 0.0
    if current_testimony is None:
        current_testimony = row['IntCode']

    keyword_segment_probability = second_level_base_probabilities[row['ShortFormID']][ 
            row['SecondLevelParentID'] ][ max(round((float(row['SegmentNumber']) / float(max_segments[row['IntCode']])) * 100), 1)
        ]
    if keyword_segment_probability == 0.0:
        continue
    current_testimony_score += 1.0 / keyword_segment_probability
    # current_testimony_readings[
    #     row['SegmentNumber'] / max_segments[current_testimony]
    # ] = 1.0 / second_level_base_probabilities[
    #         row['ShortFormID']][row['secondLevelParentID']
    #     ]

conn.commit()
