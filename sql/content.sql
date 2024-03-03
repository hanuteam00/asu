SELECT
	contents.id,
	contents.book_id,
	contents.chapter_id,
    lo.id as lo_id,
    lo.title as lo_title,
    contents.type as content_type,
    contents.content as content,
    contents.raw_content as raw_content
FROM 
    (
        SELECT 
            id,
            lo_id,
            chapter_id,
       		book_id,
        	type,
            content,
            raw_content 
        FROM 
            `v1.1_contents`
        WHERE 
            book_id in (11, 12) AND
            lo_id IS NOT NULL
    ) AS contents
LEFT JOIN 
    `v1.1_learning_objectives` as lo ON contents.lo_id = lo.id;