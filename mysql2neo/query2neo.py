import common.db as db
import json
import py2neo
from __future__ import division
from math import floor, ceil
from py2neo import Node
from py2neo import Graph
from py2neo import Relationship
from py2neo import authenticate

mysql_query = "SELECT  `TermID` ,  `TermLabel`,  `ParentTermID` ,  `ParentTermLabel` FROM  `thesaurus2015`"

cursor = db.get_cursor()
cursor.execute(mysql_query)
term_relationships = {}

while True:
	row=cursor.fetchone()
        if not row:
        	break
	if row:
		term_relationships[row["TermID"]] = {
		"term_id": row["TermID"],
		"term_label": row["TermLabel"],
		"parent_term_id": row["ParentTermID"],
		"parent_term_label": row["ParentTermLabel"]
		}
cursor.close()

#Now, processing each term separately! 
unique_nodes = {}

unique_query = """SELECT DISTINCT  `TermID` ,  `TermLabel` FROM  `thesaurus2015`"""
cursor = db.get_cursor()
cursor.execute(unique_query)
count = 1
while True:
        row=cursor.fetchone()
        if not row:
                break
        if row:
		if row["TermID"] not in unique_nodes:
			unique_nodes[row["TermID"]] = {
			"term_id": row["TermID"],
			"term_label": row["TermLabel"]
			}
		count += 1
cursor.close()
		
unique_query = """SELECT DISTINCT `ParentTermID` ,  `ParentTermLabel` FROM  `thesaurus2015`"""
cursor = db.get_cursor()
cursor.execute(unique_query)
while True:
        row=cursor.fetchone()
        if not row:
                break
        if row:
                if row["ParentTermID"] not in unique_nodes:
                        unique_nodes[row["ParentTermID"]] = {
                        "term_id": row["ParentTermID"],
                        "term_label": row["ParentTermLabel"]
                        }
		count += 1
cursor.close()

jsondata = json.dumps(term_relationships)
fd = open('node_relationships.json', 'w')
fd.write(jsondata)
fd.close()

jsondata = json.dumps(unique_nodes)
fd = open('unique_nodes.json', 'w')
fd.write(jsondata)
fd.close()


authenticate("localhost:7474", "neo4j", "cdhcjs")
graph = Graph("http://localhost:7474/db/data/")

print("Connectly to database(Neo4j).")
count = 0  
for term in unique_nodes:
	if True:
		node = Node.cast("TERM", unique_nodes[term])
		graph.create(node)
	count += 1
print "All nodes in database."

count = 0 
for rel in term_relationships:
	if True:
		child = term_relationships[rel]["term_id"]
		parent = term_relationships[rel]["parent_term_id"]
		match_query = "MATCH (n:TERM{term_id:{child}}), (m:TERM{term_id:{parent}}) CREATE (n)-[:IS_CHILD_OF]->(m), (m)-[:IS_PARENT_OF]->(n)"
		graph.cypher.execute(match_query,{"child":child,"parent":parent})
		if count % 1000 == 0:
			print str(count) + "  relationship (" + str(child) + ") <--> (" + str(parent) + ") written!"  
	count += 1 
print "All relationships in database."

# Need the pruned testimonies for this: 
query4testimonies = "SELECT * FROM  `e2_testimonies_pruned`"
testimonies_pruned = {}
cursor = db.get_cursor()
cursor.execute(query4testimonies)
while True:
        row=cursor.fetchone()
        if not row:
                break
        if row:
		testimonies_pruned[row["testimony_id"]] = {
			"testimony_id": row["testimony_id"],
			"tape_label": row["table_label"],
			"saturation_score": row["saturation_score"],
			"tot_segments": row["tot_segments"],
			"tape_code": row["tape_code"]
		}
cursor.close()

# Writing the testimonies to file. 
jsondata = json.dumps(testimonies_pruned)
fd = open('ordered_testimonies.json', 'w')
fd.write(jsondata)
fd.close()

with open('ordered_testimonies.json') as data_file: 
	testimonies_pruned = json.load(data_file)
print testimonies_pruned["10"]["tape_label"]

# Going on to creating just the testimonies now:
for tmony in testimonies_pruned:
	new = Node.cast("TESTIMONY",testimonies_pruned[tmony])
	graph.create(new)

print "All testimony nodes have already been created!"

print "Now, going for the segmentile creations!"


for tmony in testimonies_pruned:
	tmony_node = graph.find_one("TESTIMONY", "testimony_id", tmony);
	print "For testimony " + tmony 
	for i in range(1,101):
		new = Node.cast("SEGMENTILE",{"name": str(i),"node_id": i, "testimony_id": tmony})
		tmony_has_new = Relationship(tmony_node, "HAS", new)
		graph.create(new)
		graph.create(new_belongs_to_tmony)
	print "Node " + str(i) + "created! " + tmony 

print "All the segmentiles must have been created by now!"

print "Going on to creating links between the segmentiles and the keywords that they have"

# Must modify this to consider: ALL parents. 
# But currently: It takes the first level parents directly. 
query1 = """
SELECT DISTINCT parent_id
FROM even_segment_keywords_2
WHERE testimony_id = %s
AND segment_no >= %s
AND segment_no <= %s
"""
query2neo4id = """
MATCH (n:TESTIMONY{testimony_id:{tmony}})-[r]->(m:SEGMENTILE{name:{segment}}) 
RETURN ID(m)
"""
query2neo = """
MATCH (tn:TESTIMONY{testimony_id:{t_id}})-[:HAS]->(n:SEGMENTILE{name:{n_id}}), (m:TERM{term_id:{p_id}}) 
CREATE (n)-[:HAS_TERM]->(m), (m)-[:IS_IN]->(n)
"""

testimonies = testimonies_pruned

count = 1
for tmony in testimonies:
	if (count >= 2841 and count <=3000):
                tot_len = testimonies[tmony]["tot_segments"]
                print "#" + str(count) + ": For testimony: " + str(tmony) + "--- " + str(tot_len) + " segments."
                
		for i in range(0,100):
                        if i==0:
                                l1 = floor(tot_len * i * 0.01)
                        else:
                                l1 = floor(tot_len * i * 0.01) + 1
                        r1 = floor(tot_len * (i + 1) * 0.01)

                        if l1-1 == r1:
                                l1 = r1
    			cursor1 = db.get_cursor()
                        cursor1.execute(query1,(str(tmony),str(l1),str(r1)))
			if(i == 50):
                        while True:
                                row = cursor1.fetchone()
                                if not row:
                                        break
				# Process each of these UNIQUE parent id's here 
				if row:					
					term_node = graph.find_one("TERM", "term_id", row["parent_id"])
					segment_node_id = graph.cypher.execute(query2neo4id, {"tmony": tmony, "segment": str(i+1)})
                                        segment_node = graph.node(segment_node_id[0][0])
					
					has_term_relationship = Relationship(segment_node, "HAS_TERM", term_node)	
					is_in_relationship = Relationship(term_node, "IS_IN", segment_node)
					
					graph.create(has_term_relationship)
					graph.create(is_in_relationship)
			cursor1.close()    	
	count += 1






