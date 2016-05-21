# This includes: 
# 	- PARSING the xmls in /home/mkumar/xml_2015-11-06 as py dicts
#	- INSERTS of the required information in the xml dicts to the otterhound mysql db

import argparse
import common.db as db
import json
import xmltodict
from __future__ import division
from bs4 import BeautifulSoup
from math import floor, ceil
from os import walk

# python query -thesaurus /home/mkumar/thesaurus_2015-11-03/ -segments /home/mkumar/xml_2015-11-06

# Commandline Arguments: 
parser = argparse.ArgumentParser()
parser.add_argument("-thesaurus", help = "Path to Thesaurus Files.", required = True) 	
parser.add_argument("-segments", help = "Path to Segment XMLs.", required = True)		
args = parser.parse_args()

# Opening all files in order: 
allfiles = []
mypath = args.segments
for (dirpath, dirnames, filenames) in walk(mypath):
    allfiles.extend(filenames)
    break

# Write order to file
def get_param(list, variable): 
	if(variable in list):
		return list[variable]
	else:
		return "NULL"

query_insert = """
INSERT INTO testimonies2015 
(IntCode, IntervieweeName, ShortFormID, ShortFormText, Gender, HistoricEvent, ConOrg, IntState, IntCountry, IntDate, IntLanguages, IntLength)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

query_insert2 = """
INSERT INTO segmentKeywords2015 
(IntCode, SegmentID, SegmentNumber, KeywordID,  Keyword, SegInTime, SegOutTime)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
"""
cursor = db.get_cursor()
#cursor2 = db.get_cursor()
count = 1
for file in allfiles:
	if(True):
		# Read xml file, pipe xml through the utf pipelines, and parse xml to a python dictionary 'pydict'. 
		#print(file)
		try:
			filename = '/home/mkumar/xml_2015-11-06/' + file
			myfile = open(filename, 'r')
			data = myfile.read()
			udata = unicode(data, 'utf-8')
			encoded_udata = udata.encode('utf-8-sig')
			decoded_udata = encoded_udata.decode('utf-8-sig')
			ordered_dict = xmltodict.parse(decoded_udata)
			pydict = dict(ordered_dict)
			intcode = pydict["USCShoahFoundationInstituteData"]["source"]["#text"]
			interviewee_name = pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["name"]["#text"]
			sh_id = pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["source"]["#text"]
			sh_text = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["format"][0], "#text")
			gender = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["format"][1], "#text")
			h_event = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["interview"]["references"]["reference"][0], "#text")
			con_org = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["interview"]["references"]["reference"][1], "#text")
			state_int = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["interview"]["references"]["reference"][2], "#text")
			country_int = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["interview"]["references"]["reference"][3], "#text")
			date_int = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["interview"]["references"]["reference"][4], "#text")
			languages_int = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["interview"]["references"]["reference"][5], "#text")
			length_int = get_param(pydict["USCShoahFoundationInstituteData"]["BiographicalInformation"]["interview"]["references"]["reference"][6], "#text")	
			
			# First query execution: 
			#cursor.execute(query_insert, (intcode, interviewee_name, sh_id, sh_text, gender, h_event, con_org, state_int, country_int, date_int, languages_int, length_int))			
		# Process each segment, check if it has keywords and extract from keyqord. 
			#segments = pydict["USCShoahFoundationInstituteData"]["Testimony"]["segments"]
			#tot = len(segments["segment"])
			#for no in range(0,tot): 
			#	if "keywords" in segments["segment"][no]:
			#		s_num = segments["segment"][no]["@Number"]
			#		s_ID = segments["segment"][no]["@ID"]
			#		s_intime = segments["segment"][no]["@InTime"]
			#		s_outtime = segments["segment"][no]["@OutTime"]
			#		ktot = len(segments["segment"][no]["keywords"]["keyword"])
			#		if(isinstance(segments["segment"][no]["keywords"]["keyword"], list)):
			#			for kno in range(0,ktot):
			#				key_ID = segments["segment"][no]["keywords"]["keyword"][kno]["@SFI-Thesaurus-TermId"]
			#				key_word = segments["segment"][no]["keywords"]["keyword"][kno]["#text"]
			#				cursor2.execute(query_insert2, (intcode, s_ID, s_num, key_ID, key_word, s_intime, s_outtime));	
			#		else:
			#			key_ID = segments["segment"][no]["keywords"]["keyword"]["@SFI-Thesaurus-TermId"]
			#			key_word = segments["segment"][no]["keywords"]["keyword"]["#text"]
			#			cursor2.execute(query_insert2, (intcode, s_ID, s_num, key_ID, key_word, s_intime, s_outtime))
		except Exception as e:
			print(file)
			print(str(e))
			pass
			 
	if(count%1000 == 1):
		print (count)				
	count = count + 1 
conn = db.get_connection()
conn.commit()
cursor.close()
#cursor2.close()
"""





# Processing the Thesaurus next.
# Opening all files in order: 
from os import walk
allfiles = []
mypath = args.thesaurus
for (dirpath, dirnames, filenames) in walk(mypath):
    allfiles.extend(filenames)
    break


insert_query3 = """
INSERT INTO thesaurus2015
(TermID, TermLabel, ParentTermID, ParentTermLabel, ThesaurusID, ThesaurusType, KeywordCount, TypeID, IsParent, KWDefinition)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

count = 1
cursor = db.get_cursor()

for file in allfiles: 
	if True: 
		try:
			filename = args.thesaurus + file
			myfile = open(filename, 'r')
			data = myfile.read()
			udata = unicode(data, 'utf-8')
			encoded_udata = udata.encode('utf-8-sig')
			decoded_udata = encoded_udata.decode('utf-8-sig')
			ordered_dict = xmltodict.parse(decoded_udata)
			pydict = dict(ordered_dict)	
			items = pydict["USCShoahFoundationInstituteData"]["ThesaurusData"]["Items"]
			l = len(items["Item"])
			for no in range(0,l):
				ThesaurusID = get_param(items["Item"][no], "@ThesaurusID")
				TermID = get_param(items["Item"][no], "@TermID")
				TermLabel = get_param(items["Item"][no], "@SearchLabel")
				ParentTermID = get_param(items["Item"][no], "@ParentTermID")
				ParentTermLabel = get_param(items["Item"][no], "@ParentLabel")
				ThesaurusType = get_param(items["Item"][no], "@ThesaurusType")
				KeywordCount = get_param(items["Item"][no], "@KeywordCount")
				TypeID = get_param(items["Item"][no], "@TypeID")
				IsParent = get_param(items["Item"][no], "@IsParent")
				KWDefinition = get_param(items["Item"][no], "@KWDefinition")
				cursor.execute(insert_query3, (TermID, TermLabel, ParentTermID, ParentTermLabel, ThesaurusID, ThesaurusType, KeywordCount, TypeID, IsParent, KWDefinition)) 
				
			# Now, process pydict for TermId, Term Label, TermParent, TermParentLabel, additionals. 
		except Exception as e:
			print(file)
			print(str(e))
			pass
			 
		if(count%50 == 1):
			print (count)				
	count = count + 1 


conn = db.get_connection()
conn.commit()
cursor.close()


