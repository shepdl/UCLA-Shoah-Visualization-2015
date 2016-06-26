# This is to calculate the FIRST LEVEL parents based uniqueness scores for all
# the of testimonies fed from the chosen table and write them to file. 

import common.db as db
import csv
import json
from __future__ import division
from math import floor, ceil

# Read first level parent base probabilities.
query1 = """
SELECT * 
FROM firstLevelBaseProbabilities2015
"""
cursor1 = db.get_cursor()
cursor1.execute(query1)
base_probabilities = {} 
while True:
        row = cursor1.fetchone()
        if not row:
                break
        else:
                parent = "L" + str(row["ParentID"])
                if parent not in base_probabilities:
                        base_probabilities[parent] = {}
                for index in range(1,101):
                        base_probabilities[parent][index] = {}
                        base_probabilities[parent][index] = row["L" + str(index)]
cursor1.close()


# Read testimonies to score. 
query1 = """
SELECT * 
FROM testimoniesSaturationPruned2015
"""
cursor1 = db.get_cursor()
cursor1.execute(query1)
testimony_details_pruned = {}
i=0
while True: 
	row=cursor1.fetchone()
	if not row:
		break
	else:
                testimony_details_pruned[row["IntCode"]]={
                        "IntCode" : row["IntCode"],
                        "IntervieweeName" : row["IntervieweeName"],
                        "TotSegments" : row["TotSegments"],
                        "TotTaggedSegments" : row["TotTaggedSegments"],
                        "SaturationPercent" : row["SaturationPercent"],
                        "uniqueness_score" : 0
                }
	i=i+1		
cursor1.close()


# Read first level parent IDs.
query_1_2 = """
SELECT TermID
FROM  `firstLevelParents2015`
"""
parents_list = {}
cursor_1_2 = db.get_cursor()
cursor_1_2.execute(query_1_2)

while True:
	row = cursor_1_2.fetchone()
	if not row:
		break
	else:
		if row["TermID"] not in parents_list:
			parents_list[row["TermID"]] = 0

# Get first level parent climbed to from the keyword of the testimony segmentile 
# (percentile segment). This is already done in the indexed table queried from below.
# The base probability of the seocnd level paret for that particlar segmentile is
# taken and applied to formula to calculate the uniqueness score. 
query2 = """
SELECT distinct FirstLevelParentID, SegmentNumber 
FROM  segmentKeywordsFirstParents2015b 
WHERE  `IntCode` = %s
"""
count = 0
testimony_details_temp = testimony_details_pruned
for tmony in testimony_details_temp:
 	curr_testimony_normativity=0	
	if True: 
		tot_len = testimony_details_temp[tmony]["TotSegments"]
        	index = []
        	for dex in range(0,100):
			if dex==0:
				l1 = floor(tot_len * dex * 0.01)
			else: 
				l1 = floor(tot_len * dex * 0.01) + 1
			r1 = floor(tot_len * (dex + 1) * 0.01)
			for i in range(int(l1),int(r1+1)):
				index.append(dex+1)
        
		cursor2 = db.get_cursor()
		cursor2.execute(query2, [(str(testimony_details_temp[tmony]["IntCode"]))])
		
		curr_segnum = 1
		start_seg = 1
		ind = 1
		flag = 1
		seg_parent_counts = parents_list
		while True:	
			if flag == 1:
				row = cursor2.fetchone()
			if not row:
				sum_parent=0
                                for parent in seg_parent_counts:
                                	sum_parent += seg_parent_counts[parent] 
                                seg_norm_sum=0
				c_ind = 1
				if sum_parent!=0:
                                	for parent in seg_parent_counts:
                                		parID = "L" + str(parent) 
                                       		if seg_parent_counts[parent] == 0:
                                        	        seg_norm_sum += float(base_probabilities[parID][index[prev-1]])
									c_ind += 1
                                	seg_parent_counts = parents_list
                                
		
					for pID in seg_parent_counts:
						seg_parent_counts[pID] = 0
					curr_testimony_normativity += seg_norm_sum/(32-sum_parent)
                                	flag=0
				break
			else:
				curr = row["SegmentNumber"]
				if ind == 1:
                    prev = row["SegmentNumber"]
					start_segnum = row["SegmentNumber"]
					curr_segnum = row["SegmentNumber"]
					ind += 1
                		if curr!=prev:
                			curr_segnum += 1 
				if index[curr-1]!=index[prev-1]:
					dex = index[prev-1]
					if dex==0:
						l1 = floor(tot_len * dex * 0.01)
					else: 
						l1 = floor(tot_len * dex *  0.01) + 1
					r1 = floor(tot_len * (dex + 1) * 0.01)
					sum_parent=0
					for parent in seg_parent_counts:
						sum_parent += seg_parent_counts[parent]

					seg_norm_sum=0
					c_ind = 1
					for parent in seg_parent_counts:
						parID = "L" + str(parent)
						if base_probabilities[parID][index[prev-1]] != 0 and seg_parent_counts[parent] == 0: 
							seg_norm_sum += base_probabilities[parID][index[prev-1]]
							c_ind += 1
					seg_parent_counts = parents_list	
					for pID in seg_parent_counts:
                                        	seg_parent_counts[pID] = 0
					curr_testimony_normativity += seg_norm_sum / (32 - sum_parent)	
					flag=0	
				else: 
					if curr_segnum == row["SegmentNumber"]:
						flag = 1
						seg_parent_counts[row["FirstLevelParentID"]] = 1
					flag = 1
					
				prev = row["SegmentNumber"]
			
			
		cursor2.close()
	else:
		break;
		testimony_details_pruned[tmony]["uniqueness_score"] = curr_testimony_normativity 
	count += 1

# Write to files: csv and json. 
test = testimony_details_pruned
csvfile =  open('uniqueness_full_unsorted.csv', 'w')
fieldnames = ['IntervieweeName', 'IntCode', 'uniqueness_score', 'SaturationPercent', 'TotSegments']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writerow({'IntervieweeName': 'IntervieweeName',
                                'IntCode': 'IntCode',
                                'uniqueness_score': 'uniqueness_score',
                                'SaturationPercent': 'SaturationPercent',
                                'TotSegments': 'TotSegments'
                                })
for tmony in test:
	if test[tmony]['uniqueness_score'] != 0.0 :
                writer.writerow({'IntervieweeName': unicode(test[tmony]['IntervieweeName']).encode('utf-8'),
                                'IntCode': test[tmony]['IntCode'],
                                'uniqueness_score': round(test[tmony]['uniqueness_score'],4),
                                'SaturationPercent': test[tmony]['SaturationPercent'],
                                'TotSegments': test[tmony]['TotSegments']
                                })
jsondata = json.dumps(test)
fd = open('uniqueness_full_unsorted.json', 'w')
fd.write(jsondata)			
fd.close()


