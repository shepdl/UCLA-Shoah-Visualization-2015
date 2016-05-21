## Getting Started

- Change the 'config.py' file in ./common to reflect the database to write the Testimonies, Thesaurus and the SegmentKeywords tables to and a username and password combination to access it.

- Please create the following tables in the database to write new Thesaurus and the SegmentKeywords table to - 

```
create table thesaurusNew2015 (
	TermID INT, 
	TermLabel varchar(400), 
	ParentTermID INT, 
	ParentTermLabel varchar(500), 
	OldTermID INT, 
	ThesaurusID INT, 
	ThesaurusType varchar(10), 
	KeywordCount INT, 
	TypeID INT, 
	IsParent varchar(6), 
	KWDefinition varchar(5000)
); 
```

```
create table segmentKeywordsNew2015 (
	IntCode INT, 
	SegmentID INT, 
	SegmentNumber INT, 
	KeywordID INT, 
	Keyword VARCHAR(1000), 
	SegInTime VARCHAR(30), 
	SegOutTime VARCHAR(30)
);
```


