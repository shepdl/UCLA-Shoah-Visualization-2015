
-- get segment counts
SELECT sk.IntCode, t.ShortFormID, MAX(SegmentNumber) AS total_segments 
FROM segmentKeywordsNew2015 AS sk
    JOIN testimonies2015 AS t ON t.IntCode = sk.IntCode
GROUP BY IntCode

-- get segmentile

SELECT FirstLevelParentID / COUNT(*), segmentCounts.SegmentNumber / segmentCounts.total_segments 
FROM segmentKeywordsNew2015 AS sk
    JOIN (
        SELECT sk.IntCode, t.ShortFormID, MAX(SegmentNumber) AS total_segments 
        FROM segmentKeywordsNew2015 AS sk
            JOIN testimonies2015 AS t ON t.IntCode = sk.IntCode
        GROUP BY IntCode
    ) AS segmentCounts ON sk.IntCode = segmentCounts.IntCode
GROUP BY segmentCounts.ShortFormID, (segmentCounts.SegmentNumber / segmentCounts.total_segments), FirstLevelParentID 




( 
    SELECT ShortFormID, IntCode, MAX(SegmentNumber) AS total 
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN testimonies AS t ON t.IntCode = sk.IntCode
    GROUP BY IntCode
) AS totalSegments

JOIN (
    -- Total keywords by segment and ShortFormID
    SELECT ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS totalKeywords, t.ShortFormID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN totalSegments ON totalSegments.IntCode = sk.IntCode
    GROUP BY totalSegments.ShortFormID, segmentile
) AS totalKeywordsBySegment ON totalKeywordsBySegment.IntCode = totalSegments.IntCode

JOIN (
    SELECT COUNT(*) / totalKeywordsBySegment.totalKeywords, t.ShortFormID, FirstLevelParentID, ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile
    FROM segmentKeywordsFirstParents2015 AS sk 
    JOIN totalSegments ON sk.IntCode = totalSegments.IntCode
    JOIN totalKeywordsBySegment ON totalKeywordsBySegment.segmentile = sk.segmentile
    GROUP BY totalSegments.ShortFormID, ROUND(SegmentNumber /totalSegments.total * 100), FirstLevelParentID
) 



SELECT COUNT(*) / totalKeywordsBySegment.totalKeywords, t.ShortFormID, FirstLevelParentID, ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile
FROM segmentKeywordsFirstParents2015 AS sk 
JOIN 
( 
    SELECT ShortFormID, IntCode, MAX(SegmentNumber) AS total 
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN testimonies AS t ON t.IntCode = sk.IntCode
    GROUP BY IntCode
) AS totalSegments ON sk.IntCode = totalSegments.IntCode

JOIN (
    -- Total keywords by segment and ShortFormID
    SELECT ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS totalKeywords, t.ShortFormID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN totalSegments ON totalSegments.IntCode = sk.IntCode
    GROUP BY totalSegments.ShortFormID, segmentile
) AS totalKeywordsBySegment ON totalKeywordsBySegment.IntCode = totalSegments.IntCode AND totalKeywordsBySegment.segmentile = sk.segmentile
GROUP BY totalSegments.ShortFormID, ROUND(SegmentNumber /totalSegments.total * 100), FirstLevelParentID


-- I think this is the final version that I started running

SELECT COUNT(*) / totalKeywordsBySegment.totalKeywords, totalSegments.ShortFormID, FirstLevelParentID, ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile
FROM segmentKeywordsFirstParents2015 AS sk
JOIN
(
    SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
    GROUP BY sk.IntCode
) AS totalSegments ON sk.IntCode = totalSegments.IntCode

JOIN (
    -- Total keywords by segment and ShortFormID
    SELECT ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS totalKeywords, totalSegments.ShortFormID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN (
    	SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
	    FROM segmentKeywordsFirstParents2015 AS sk
    	JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
	    GROUP BY sk.IntCode
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    GROUP BY totalSegments.ShortFormID, segmentile
) AS totalKeywordsBySegment ON totalKeywordsBySegment.ShortFormID = totalSegments.ShortFormID

GROUP BY totalSegments.ShortFormID, ROUND(SegmentNumber /totalSegments.total * 100), FirstLevelParentID



-- Does this work, or are we missing something?
SELECT COUNT(*) / totalKeywordsBySegment.totalKeywords, totalSegments.ShortFormID, FirstLevelParentID, totalKeywordsBySegment.segmentile
FROM
(
	-- totalSegments
    SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
    GROUP BY sk.IntCode
) AS totalSegments

JOIN (
    -- Total keywords by segment and ShortFormID
    SELECT FirstLevelParentID, ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS totalKeywords, totalSegments.ShortFormID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN (
    	SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
	    FROM segmentKeywordsFirstParents2015 AS sk
    	JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
	    GROUP BY sk.IntCode
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    GROUP BY totalSegments.ShortFormID, segmentile
) AS totalKeywordsBySegment ON totalKeywordsBySegment.ShortFormID = totalSegments.ShortFormID

GROUP BY totalSegments.ShortFormID, totalKeywordsBySegment.segmentile, FirstLevelParentID



-- Trying again ...
SELECT keywordCountsBySegment.keywordCount / totalKeywordsBySegment.totalKeywords AS probability, totalKeywordsBySegment.ShortFormID, FirstLevelParentID, totalKeywordsBySegment.segmentile
FROM
(
	-- totalSegments
    SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
    GROUP BY sk.IntCode
) AS totalSegments

JOIN (
    -- Total keywords by segment and ShortFormID
    SELECT ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS totalKeywords, totalSegments.ShortFormID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN (
    	SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
	    FROM segmentKeywordsFirstParents2015 AS sk
    	JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
	    GROUP BY sk.IntCode
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    GROUP BY totalSegments.ShortFormID, segmentile
) AS totalKeywordsBySegment ON totalKeywordsBySegment.ShortFormID = totalSegments.ShortFormID

JOIN (
	SELECT FirstLevelParentID, ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS keywordCount, totalSegments.ShortFormID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN (
    	SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
	    FROM segmentKeywordsFirstParents2015 AS sk
    	JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
	    GROUP BY sk.IntCode, sk.FirstLevelParentID
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    GROUP BY totalSegments.ShortFormID, segmentile
) AS keywordCountsBySegment ON totalKeywordsBySegment.ShortFormID = totalSegments.ShortFormID AND totalKeywordsBySegment.segmentile = keywordCountsBySegment.segmentile

GROUP BY totalSegments.ShortFormID, totalKeywordsBySegment.segmentile, keywordCountsBySegment.FirstLevelParentID



-- Another test:

SELECT keywordCountsBySegment.keywordCount / totalKeywordsBySegment.totalKeywords AS probability, totalKeywordsBySegment.ShortFormID, FirstLevelParentID, totalKeywordsBySegment.segmentile
FROM
(
	-- totalSegments
    SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
    GROUP BY sk.IntCode
) AS totalSegments

JOIN (
    -- Total keywords by segment and ShortFormID
    SELECT ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS totalKeywords, totalSegments.ShortFormID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN (
    	SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
	    FROM segmentKeywordsFirstParents2015 AS sk
    	JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
	    GROUP BY sk.IntCode
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    GROUP BY totalSegments.ShortFormID, segmentile
) AS totalKeywordsBySegment ON totalKeywordsBySegment.ShortFormID = totalSegments.ShortFormID

JOIN (
	SELECT FirstLevelParentID, ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS keywordCount, totalSegments.ShortFormID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN (
    	SELECT ShortFormID, sk.IntCode, MAX(SegmentNumber) AS total
	    FROM segmentKeywordsFirstParents2015 AS sk
    	JOIN `testimonies2015` AS t ON t.IntCode = sk.IntCode
	    GROUP BY sk.IntCode, sk.FirstLevelParentID
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    GROUP BY totalSegments.ShortFormID, segmentile
) AS keywordCountsBySegment ON totalKeywordsBySegment.ShortFormID = totalSegments.ShortFormID AND totalKeywordsBySegment.segmentile = keywordCountsBySegment.segmentile

GROUP BY totalSegments.ShortFormID, totalKeywordsBySegment.segmentile, keywordCountsBySegment.FirstLevelParentID


-- The version that works ...


SELECT totalKeywordsBySegment.ShortFormID, totalKeywordsBySegment.segmentile, FirstLevelParentID, keywordCountsBySegment.keywordCount, keywordCountsBySegment.keywordCount / totalKeywordsBySegment.totalKeywords AS probability

FROM (
    -- Total keywords by segment and ShortFormID
    SELECT t.ShortFormID, ROUND(SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS totalKeywords
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN (
    	SELECT sk.IntCode, MAX(SegmentNumber) AS total
        FROM segmentKeywordsFirstParents2015 AS sk
	    GROUP BY sk.IntCode
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    JOIN testimonies2015 AS t ON t.IntCode = sk.IntCode
    GROUP BY t.ShortFormID, segmentile
) AS totalKeywordsBySegment

JOIN (
	SELECT t.ShortFormID, ROUND(sk.SegmentNumber / totalSegments.total * 100) AS segmentile, COUNT(*) AS keywordCount, sk.FirstLevelParentID
    FROM segmentKeywordsFirstParents2015 AS sk
    JOIN (
    	SELECT sk.IntCode, MAX(SegmentNumber) AS total
        FROM segmentKeywordsFirstParents2015 AS sk
	    GROUP BY sk.IntCode
	) AS totalSegments ON totalSegments.IntCode = sk.IntCode
    JOIN testimonies2015 AS t ON t.IntCode = sk.IntCode
    GROUP BY t.ShortFormID, segmentile, sk.FirstLevelParentID
) AS keywordCountsBySegment ON totalKeywordsBySegment.ShortFormID = keywordCountsBySegment.ShortFormID AND totalKeywordsBySegment.segmentile = keywordCountsBySegment.segmentile

GROUP BY keywordCountsBySegment.ShortFormID, keywordCountsBySegment.segmentile, keywordCountsBySegment.FirstLevelParentID

