# This is to count the number of testimonies whose uniqueness/normativity score falls into the incremental histogram bins. 
# The increments are set by the definition of max inteh script. 

from __future__ import division
import common.db as db
import simplejson as json
import csv
from math import floor, ceil

# Open. 
fd = open('uniqueness_full_unsorted.json', 'r')
jsondata = json.load(fd)
fd.close()

# Set max. 
countArray = []
count2 = 0
max = -1
maxCount = 0
for jdata in jsondata:
	if True:
		print jdata
		if jsondata[jdata]["uniqueness_score"] > max:
			max = jsondata[jdata]["uniqueness_score"]
	count2 += 1

# Set up bins. 
for i in range(0,ceil(max)):
	countArray.append(0)

# Remember first 100 testimonies of eah bin. 
countTestimonies = {}
tcount = 0 
for jdata in jsondata:
	index = int(floor(jsondata[jdata]["uniqueness_score"]))
	if index!= 0:
		countArray[index] += 1
		print index
		if countArray[index] <= 100:
			if index not in countTestimonies:
				countTestimonies[index] = {}
			countTestimonies[index][jsondata[jdata]["testimony_id"]] = jsondata[jdata] 	
	tcount += 1
jsondata = json.dumps(countTestimonies)

# Write to file. 
fd = open('testimony_details100.json', 'w')
fd.write(jsondata)
fd.close()
