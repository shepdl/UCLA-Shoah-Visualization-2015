import codecs
import collections

import mysql.connector


connection = mysql.connector.connect(user='root', database='vhf_report_nov_2018')


cursor = connection.cursor(dictionary=True)
cursor.execute('SELECT term_id, first_level_parent_id FROM term_first_level_parents')

term_parents = collections.defaultdict(list)
for row in cursor:
    term_parents[row['term_id']].append(row['first_level_parent_id'])




# Find testimony lengths
testimony_lengths = {}
cursor = connection.cursor(dictionary=True)
cursor.execute('SELECT TestimonyID, Length FROM rpt_testimony WHERE ShortFormIDs = %s', ('<2>',))

for row in cursor.fetchall():
    testimony_lengths[row['TestimonyID']] = (row['Length'] // (60000)) + 1 # believe testimony lenght is in ms

cursor.close()

# Find keywords at each percentile to make segmentile
percentile_counts = {
    testimony_id: [ {} for _ in range(100)] # one keyword count dictionary per testimony
    for testimony_id in testimony_lengths
}

cursor = connection.cursor(dictionary=True)
cursor.execute('''
SELECT sk.TestimonyID, s.SegmentNumber, KeywordID 
        -- , thes.ThesaurusType, -- thes.Label,
        -- thes.ParentTermID
FROM rpt_SegmentKeyword AS sk 
    JOIN rpt_Testimony AS t ON t.TestimonyID = sk.TestimonyID
    JOIN rpt_segment AS s ON sk.SegmentID = s.SegmentID
    -- JOIN rpt_thesaurus3 AS thes ON sk.KeywordID = thes.TermID
WHERE t.ShortFormIDs = %s AND sk.SegmentID >= 225469
    -- AND thes.ThesaurusType IN (1, 3)
''', ('<2>',)
)
rows = 0
for row in cursor:
    rows += 1
    segmentile = round((row['SegmentNumber'] / testimony_lengths[row['TestimonyID']]) * 100)

    if segmentile > 99:
        segmentile = 99
    if row['KeywordID'] not in term_parents:
        parent_terms = [row['KeywordID']]
    else:
        parent_terms = term_parents[row['KeywordID']]
    for parent_term in parent_terms:
        percentile_counts[row['TestimonyID']][segmentile].setdefault(parent_term, 0)
        percentile_counts[row['TestimonyID']][segmentile][parent_term] += 1

segment_keyword_aggregate = {x: {} for x in range(0, 100)}
summary = {x: {} for x in range(0, 100)}
cursor.close()
for segment_no in range(0, 100):
    keyword_instances = 0
    for testimony_id in percentile_counts:
        for term_id, count in percentile_counts[testimony_id][segment_no].items():
            segment_keyword_aggregate[segment_no].setdefault(term_id, 0)
            segment_keyword_aggregate[segment_no][term_id] += count
            keyword_instances += count

summary[segment_no] = { 'total': keyword_instances, }

cursor = connection.cursor()
segment_no = 50
for term_id, value in segment_keyword_aggregate[segment_no].items():
    print(segment_no, term_id, value)

cursor.close()
connection.commit()
    
out_file.close()

connection.close()
            

    # For each segmentile, count mentions of all keywords over total. Divide these. That gives the percentage of testimonies that mention that keyword at that percentile.


