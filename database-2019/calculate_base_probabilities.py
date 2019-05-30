import codecs
import collections

import mysql.connector


connection = mysql.connector.connect(user='root', database='vhf_report_nov_2018')

# Build tree of topics
cursor = connection.cursor(dictionary=True)
cursor.execute('SELECT DISTINCT TermID, ParentTermID FROM rpt_thesaurus3 WHERE ThesaurusType = 1 and ParentType = 1')
# Find all parents through DFS
children = collections.defaultdict(list)
for row in cursor:
    children[row['ParentTermID']].append(row['TermID'])
    # children[row['TermID']].append(row['ParentTermID'])


term_parents = collections.defaultdict(set)

for t in children[-1]:
    stack = children[t]
    while stack:
        c = stack.pop()
        # term_parents[c] = t
        term_parents[c].add(t)
        for n in children[c]:
            if n not in term_parents:
                stack.append(n)
            continue
            if n in term_parents:
                print(term_parents)
                path = [n,]
                f = term_parents[n]
                while f != n and f != -1:
                    path.append(f)
                    print(path)
                    f = term_parents[f]
                print('{} has loop'.format([str(x) for x in path]))
                sys.exit(1)
            stack.append(n)


cursor.close()
cursor = connection.cursor()
cursor.execute('SELECT DISTINCT TermID, ParentTermID FROM rpt_thesaurus3 WHERE ThesaurusType = 3 and ParentType = 1')
print('{} term parents'.format(len(term_parents)))
for row in cursor:
    if TermID == ParentTermID:
        continue
    term_parents[row[0]] = term_parents[row[0]].union(term_parents[row[1]]) # .extend(term_parents[row[1]])
print('{} term parents'.format(len(term_parents)))


cursor = connection.cursor()
cursor.execute('DROP TABLE IF EXISTS term_first_level_parents')
cursor.execute('''
CREATE TABLE term_first_level_parents (
    term_id INT NOT NULL,
    first_level_parent_id INT NOT NULL
)
''')


for k, v in term_parents.items():
    for v1 in v:
        cursor.execute('INSERT INTO term_first_level_parents (term_id, first_level_parent_id) VALUES (%s, %s)', (k,v1))
cursor.execute('DROP TABLE IF EXISTS base_probabilities')
cursor.execute('''
    CREATE TABLE base_probabilities (
        ShortFormIDs VARCHAR(12) NOT NULL,
        Percentile INT NOT NULL,
        KeywordID INT NOT NULL,
        Probability DOUBLE NOT NULL
    )
''')
cursor.close()
connection.commit()



cursor = connection.cursor()
cursor.execute('SELECT DISTINCT ShortFormIDs FROM rpt_testimony')
out_file = codecs.open('totals.csv', 'w', encoding='utf8')
out_file.write('victim_group_id,term_id,segment_no,percentage\n')
for victim_group_id_tuple in cursor.fetchall():
    victim_group_id = victim_group_id_tuple[0]
    print('Starting short form ID {} ...'.format(victim_group_id))

    # Find testimony lengths
    testimony_lengths = {}
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT TestimonyID, Length FROM rpt_testimony WHERE ShortFormIDs = %s', (victim_group_id,))
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
    ''', (victim_group_id,)
    )
    rows = 0
    for row in cursor:
        rows += 1
        segmentile = round((row['SegmentNumber'] / testimony_lengths[row['TestimonyID']]) * 100)
        if segmentile > 99:
            # print(row['SegmentNumber'] , '/', testimony_lengths[row['TestimonyID']])
            pass
        if segmentile > 99:
            segmentile = 99
        if row['KeywordID'] not in term_parents:
            parent_terms = [row['KeywordID']]
        else:
            parent_terms = term_parents[row['KeywordID']]
        for parent_term in parent_terms:
            percentile_counts[row['TestimonyID']][segmentile].setdefault(parent_term, 0)
            percentile_counts[row['TestimonyID']][segmentile][parent_term] += 1

    if rows % 10000 == 0:
        print('{} rows completed'.format(rows))
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
    for segment_no in range(0, 100):
        for term_id, value in segment_keyword_aggregate[segment_no].items():
            percentage = value / summary[segment_no]['total']
            out_file.write('{},{},{},{}\n'.format(victim_group_id, term_id, segment_no, percentage))
            cursor.execute('''
                INSERT INTO base_probabilities (ShortFormIDs, Percentile, KeywordID, Probability) 
                VALUES (%s, %s, %s, %s)
            ''', (victim_group_id, segment_no, term_id, percentage,))

    cursor.close()
    connection.commit()
    print('Short form ID {} complete ...'.format(victim_group_id))
    
out_file.close()

connection.close()
            

    # For each segmentile, count mentions of all keywords over total. Divide these. That gives the percentage of testimonies that mention that keyword at that percentile.


