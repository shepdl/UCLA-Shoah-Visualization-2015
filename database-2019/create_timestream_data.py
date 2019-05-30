import codecs
import collections
import json

import mysql.connector


connection = mysql.connector.connect(user='root', database='vhf_report_nov_2018')

# # Build tree of topics
# cursor = connection.cursor(dictionary=True)
# cursor.execute('SELECT DISTINCT TermID, ParentTermID FROM rpt_thesaurus3 WHERE ThesaurusType IN (1, 3) AND ParentTypeID = 1')
# # Find all parents through DFS
# children = collections.defaultdict(list)
# for row in cursor.fetchall():
#     children[row['ParentTermID']].append(row['TermID'])
#     # children[row['TermID']].append(row['ParentTermID'])

cursor = connection.cursor(dictionary=True)
cursor.execute('SELECT DISTINCT TermID, Label FROM rpt_thesaurus3')
labels = {}
for row in cursor.fetchall():
    labels[row['TermID']] = row['Label'].strip()


cursor = connection.cursor()
cursor.execute('SELECT DISTINCT ShortFormIDs, ShortFormLabels FROM rpt_testimony')

for victim_group_id_tuple in cursor.fetchall():
    victim_group_id, victim_group_name = victim_group_id_tuple
    print('Starting {} ...'.format(victim_group_name))
    victim_group_id_separated = victim_group_id[0][1:-1]
    
    cursor = connection.cursor()
    cursor.execute('''
        SELECT KeywordID, Percentile, Probability -- , t.Label
        FROM base_probabilities AS bp
            -- JOIN rpt_thesaurus3 AS t ON t.TermID = KeywordID
        WHERE ShortFormIDs = %s -- AND ThesaurusType IN (1, 3)
        ORDER BY ShortFormIDs, Percentile
    ''', (victim_group_id,))
    data = {}
    for row in cursor:
        data.setdefault(labels[row[0]], {k: 0 for k in range(100)})
        # data[row[0]][row[1]] = row[2]
        data[labels[row[0]]][row[1]] = row[2]
        # data[row[0].strip()][row[1]] = row[2]
        # data[row[0]].append(row[2])

    for k, items in data.items():
        modified = [0.0,] * 100
        for segmentile, value in items.items():
            modified[segmentile] = value
        data[k] = modified
        # assert len(items) == 100

    out = open('timestreams-edited/{}.js'.format(victim_group_name.lower().replace('(', '').replace(')', '').replace(' ', '-')), 'w')
    json_data = json.dumps(data, indent=4)
    out.write(json_data)
    # out.write("""var data = {}""".format(json_data))

