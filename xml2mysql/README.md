

##Getting Started

- Extract the 2015 thesaurus and segment-keywords XML zips to the ../data folder. 
- Change the 'config.py' file in ./common to reflect the database to write the 
Testimonies, Thesaurus and the SegmentKeywords tables to and a username and password combination to access it. 
- Please create the following tables in the database to write xml data:

```
create table testimonies2015 ( 
	IntCode VARCHAR(10),  
	IntervieweeName VARCHAR(100), 
	ShortFormID VARCHAR(5), 
	ShortFormText VARCHAR(100), 
	Gender VARCHAR(10), 
	HistoricEvent VARCHAR(100), 
	ConOrg VARCHAR(50), 
	IntState VARCHAR(50),  
	IntCountry VARCHAR(50), 
	IntDate VARCHAR(10), 
	IntLanguages VARCHAR(100), 
	IntLength VARCHAR(30), 
	PRIMARY KEY (IntCode)
);
```

```
create table thesaurus2015 (
    TermID INT, 
    TermLabel varchar(1000), 
    ParentTermID INT, 
    ParentTermLabel varchar(500), 
	ThesaurusID INT, 
	ThesaurusType varchar(10), 
	KeywordCount INT, 
	TypeID INT, 
	IsParent varchar(6), 
	KWDefinition varchar(6000)
); 
```

```
create table segmentKeywords2015 (
	IntCode VARCHAR(10), 
	SegmentID INT, 
	SegmentNumber INT, 
	KeywordID INT, 
	Keyword VARCHAR(1000), 
	SegInTime VARCHAR(30), 
	SegOutTime VARCHAR(30)
);
```
- **query.py** - Please use 'python query -h' for more information. 

