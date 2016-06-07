from __future__ import division
import common.db as db
import  json
import csv
import argparse
import re
from math import floor, ceil

# Supporting functions: 
def getParents(level):
	parents = {}
	tablename = level + 'LevelParents2015'
	query = 'SELECT * from {tablename}'.format(tablename = tablename)
	cursor = db.get_cursor()
	cursor.execute(query)
	while True: 
		row = cursor.fetchone()
		if not row:
			break
		else:
			parents[str(row["TermID"])] = row["TermLabel"] 
	return parents	
			
def getBaseProbabilities(level, database):
	base_probabilities = {}
	if database:
		level = level[0].upper() + level[1:]	
	tablename = database + level + 'LevelBaseProbabilities2015'
	query = 'SELECT *  FROM {tablename}'.format(tablename = tablename)
	cursor = db.get_cursor()
	cursor.execute(query)
	count = 0
	while True: 
		row = cursor.fetchone()
		if not row: 
			break
		else:
			if level.lower() == 'first':
                		if count <= 100: 
                        		for row_val in row:
                                		if row_val not in base_probabilities:
                                        		base_probabilities[row_val] = {}
                                		base_probabilities[row_val][count+1] = {}
                                		base_probabilities[row_val][count+1] = row[row_val]
				
			if level.lower() == 'second':
                		parent = "L" + str(row["ParentID"])
                		if parent not in base_probabilities:
                        		base_probabilities[parent] = {}
                		for index in range(1,101):
                        		base_probabilities[parent][index] = {}
                        		base_probabilities[parent][index] = row["L" + str(index)]					
		count += 1 
	newtablename = '{tablename}_extended'.format(tablename = tablename)
	return base_probabilities, newtablename

def createNewTable(level, database, tablename):
	query = 'CREATE TABLE IF NOT EXISTS {tablename}'.format(tablename = tablename) 	
	columnList = ['ParentID INT', 'ParentLabel VARCHAR(200)']
	for num in range(1,101):
		columnList.append('L' + str(num) + ' FLOAT')
	columnsString = ', '.join(columnList)
	query = query + ' ( ' + columnsString + ' ) '
	cursor = db.get_cursor()
	cursor.execute(query)
	cursor.close()	

def insertToNewTable(baseProbabilities, parents, tablename):
	columnList = ['ParentID', 'ParentLabel']
        for num in range(1,101):
                columnList.append('L' + str(num))
        columnsString = ', '.join(columnList)
	
	queryTemplate = 'INSERT INTO {tablename} ({columns}) VALUES ({values})'
	cursor = db.get_cursor()
	for parent in baseProbabilities:
		if parent[1:] in parents:
			baseProbabilities[parent]["ParentLabel"] = parents[parent[1:]]
		
			values = baseProbabilities[parent]
			string = values["ParentLabel"].encode('ascii', 'ignore')
			string = re.sub("'", "", string)
			label  = "'{label}'".format(label = string)
			valueList = []
			valueList.append(parent[1:])
			valueList.append(label)
			for num in range(1,101):
				valueList.append(str(values[num]))
			valuesString  = ', '.join(valueList)
			query = queryTemplate.format(tablename = tablename, columns = columnsString, values = valuesString)
			print(query)
			cursor.execute(query)
	cursor.close()
		
# Main code; 
def main():
	# Step 1: Parse arguments. 
    parser = argparse.ArgumentParser(description='Get parents level and database.')
	parser.add_argument('--db', type = str, help = 'DB type. Choose: nanjing, rwandan, armenian, sintiRoma, liberator, rescuer, political', default = '')
	parser.add_argument('--l', type = str, help = 'Parent level. Choose: first or second.')
	args = parser.parse_args() 
	
	# Step 2: Get 'l' parents. 
	parents = getParents(args.l)
	
	# Step 3: Get 'l' baseprobabilities of 'db'. 
	baseProbabilities, newtablename = getBaseProbabilities(args.l, args.db)
	
	# Step 3: Create new table.
	createNewTable(args.l, args.db, newtablename)
	
	# Step 4: Match and insert. 
	insertToNewTable(baseProbabilities, parents, newtablename)

if __name__ == "__main__":
    	main()


