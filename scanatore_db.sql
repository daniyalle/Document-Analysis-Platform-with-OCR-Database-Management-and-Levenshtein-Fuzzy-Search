--This table will store information about each session. A session represents one interaction of a user with the system (e.g., when they upload documents and perform searches).
-- Create the sessions table to store session data
CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,              -- Unique session identifier
    user_id INT,                                -- Optional: Identifier for the user (if you want to associate users)
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When the session started
    end_time TIMESTAMP                          -- When the session ended (optional, can be updated later)
);



--This table will store information about each document uploaded during a session. Each document will be linked to a session.
-- Create the documents table to store document metadata
CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,             -- Unique identifier for each document
    document_path VARCHAR(255),                 -- File path or name of the document
    session_id INT REFERENCES sessions(session_id),  -- Foreign key to the sessions table
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the document was uploaded
    page_count INT                              -- Number of pages in the document (useful for multi-page documents)
);


--This table will store the extracted words along with their coordinates (bounding box) and the document in which they appeared.
-- Create a table to store extracted text along with its coordinates
CREATE TABLE extracted_texts (
    text_id SERIAL PRIMARY KEY,            -- Unique identifier for each word occurrence
    document_id INT REFERENCES documents(document_id),  -- Foreign key to the documents table
    word VARCHAR(255),                     -- The word that was extracted
    x_min INT,                             -- X-coordinate of the word’s bounding box (min)
    y_min INT,                             -- Y-coordinate of the word’s bounding box (min)
    x_max INT,                             -- X-coordinate of the word’s bounding box (max)
    y_max INT,                             -- Y-coordinate of the word’s bounding box (max)
    page_number INT,                       -- The page number where the word appeared (for multi-page documents)
    session_id INT REFERENCES sessions(session_id),  -- Foreign key to the session
    UNIQUE(document_id, word, page_number, x_min, y_min)  -- Ensure that the combination is unique
);


--If you need more advanced search features, such as storing search term metadata, or if you want to perform specific queries on certain terms, you could use this table. This is optional and can be removed if unnecessary.
-- Optional table to store search term metadata for optimization or tracking
CREATE TABLE search_terms (
    term_id SERIAL PRIMARY KEY,            -- Unique identifier for each search term
    term VARCHAR(255),                     -- The actual search term (e.g., "university")
    session_id INT REFERENCES sessions(session_id),  -- Foreign key to the session
    last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When the term was last searched
);




