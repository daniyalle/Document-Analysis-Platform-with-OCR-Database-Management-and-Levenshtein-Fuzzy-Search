# Part 1: Original code (Document Processing and Database Interaction)
import os
import cv2
import pytesseract
import psycopg2
import numpy as np  # Add this line
from pdf2image import convert_from_path
from PIL import Image

# Set up Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Directory containing the documents (using raw string to handle backslashes)
documents_directory = r'documents_folder'

# Connect to PostgreSQL database
try:
    conn = psycopg2.connect("dbname= user= password=")
    cur = conn.cursor()
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Function to clear all data from documents and extracted_texts
def clear_all_data():
    try:
        cur.execute("TRUNCATE TABLE extracted_texts, documents RESTART IDENTITY CASCADE;")
        print("All previous data cleared from 'documents' and 'extracted_texts'.")
    except Exception as e:
        print(f"Error clearing data: {e}")

# Function to get or create a session
def get_or_create_session():
    try:
        user_input = input("Do you want to start a new session? (yes/no): ").strip().lower()

        if user_input == "yes":
            # Update the end_time of the last session before starting a new one
            cur.execute("""
                UPDATE sessions
                SET end_time = CURRENT_TIMESTAMP
                WHERE session_id = (
                    SELECT session_id
                    FROM sessions
                    WHERE end_time IS NULL
                    ORDER BY start_time DESC
                    LIMIT 1
                );
            """)

            # Clear all previous data from tables
            clear_all_data()

            # Create a new session
            cur.execute("""
                INSERT INTO sessions (start_time)
                VALUES (CURRENT_TIMESTAMP)
                RETURNING session_id;
            """)
            session_id = cur.fetchone()[0]
            print(f"New session created with session_id: {session_id}")
        else:
            # Retrieve the most recent session
            cur.execute("SELECT session_id FROM sessions ORDER BY start_time DESC LIMIT 1;")
            session = cur.fetchone()

            if session is None:
                print("No existing session found. Please create a new session.")
                return None
            else:
                session_id = session[0]
                print(f"Continuing with existing session_id: {session_id}")

        return session_id
    except Exception as e:
        print(f"Error getting or creating session: {e}")
        return None


# Function to insert document metadata into the database
def insert_document_metadata(file_path, session_id, page_count):
    try:
        cur.execute("""
            INSERT INTO documents (document_path, session_id, page_count)
            VALUES (%s, %s, %s)
            RETURNING document_id;
        """, (file_path, session_id, page_count))
        document_id = cur.fetchone()[0]
        return document_id
    except Exception as e:
        print(f"Error inserting document metadata: {e}")
        return None

# Function to extract text and coordinates using Tesseract
def extract_text_and_coordinates(image):
    try:
        ocr_result = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        words = []
        for i, word in enumerate(ocr_result['text']):
            if word.strip():
                word_info = {
                    'word': word,
                    'x_min': ocr_result['left'][i],
                    'y_min': ocr_result['top'][i],
                    'x_max': ocr_result['left'][i] + ocr_result['width'][i],
                    'y_max': ocr_result['top'][i] + ocr_result['height'][i]
                }
                words.append(word_info)
        return words
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return []

# Function to process PDF files and extract images
def process_pdf(file_path):
    try:
        # Convert PDF pages to images
        images = convert_from_path(file_path, dpi=300)
        return images
    except Exception as e:
        print(f"Error processing PDF {file_path}: {e}")
        return []

# Main processing loop
# Function to process PDF files in batches of 10 pages
def process_pdf_in_batches(file_path, session_id):
    try:
        images = convert_from_path(file_path, dpi=300)
        total_pages = len(images)
        batch_size = 10

        # Insert metadata for the PDF
        document_id = insert_document_metadata(file_path, session_id, total_pages)
        if not document_id:
            return

        # Process pages in batches of 10
        for start_page in range(0, total_pages, batch_size):
            end_page = min(start_page + batch_size, total_pages)
            print(f"Processing pages {start_page + 1}-{end_page} of {file_path}...")

            # Process each page in the current batch
            for page_number in range(start_page, end_page):
                image = images[page_number]
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Extract text from the page
                words = extract_text_and_coordinates(open_cv_image)

                # Insert the extracted text into the database
                for word_info in words:
                    try:
                        cur.execute("""
                            INSERT INTO extracted_texts (document_id, word, x_min, y_min, x_max, y_max, page_number, session_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        """, (document_id, word_info['word'], word_info['x_min'], word_info['y_min'],
                              word_info['x_max'], word_info['y_max'], page_number + 1, session_id))
                    except Exception as e:
                        print(f"Error inserting word '{word_info['word']}' from page {page_number + 1}: {e}")
    except Exception as e:
        print(f"Error processing PDF {file_path}: {e}")

# Main processing loop
for filename in os.listdir(documents_directory):
    file_path = os.path.join(documents_directory, filename)

    if filename.endswith('.pdf'):
        session_id = get_or_create_session()
        if session_id is None:
            print("Error: Could not retrieve or create a session.")
            break

        process_pdf_in_batches(file_path, session_id)

    elif filename.endswith(('.jpg', '.png', '.jpeg')):
        image = cv2.imread(file_path)
        if image is None:
            print(f"Failed to read image {filename}")
            continue

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        words = extract_text_and_coordinates(gray_image)

        session_id = get_or_create_session()
        if session_id is None:
            print("Error: Could not retrieve or create a session.")
            break

        document_id = insert_document_metadata(file_path, session_id, page_count=1)
        if document_id:
            for word_info in words:
                try:
                    cur.execute("""
                        INSERT INTO extracted_texts (document_id, word, x_min, y_min, x_max, y_max, page_number, session_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """, (document_id, word_info['word'], word_info['x_min'], word_info['y_min'],
                          word_info['x_max'], word_info['y_max'], 1, session_id))
                except Exception as e:
                    print(f"Error inserting word '{word_info['word']}': {e}")




# Part 2: Search Function

def search_word_in_documents(search_term, max_distance=2):
    if not search_term:
        print("Error: Search term is empty. Please provide a valid term.")
        return

    try:
        # SQL query to retrieve details about documents, words, and sessions using Levenshtein distance
        query = """
            SELECT
                d.document_id,
                d.document_path,
                d.page_count,
                et.word,
                et.x_min,
                et.y_min,
                et.x_max,
                et.y_max,
                et.page_number,
                s.session_id
            FROM
                public.extracted_texts et
            JOIN
                public.documents d ON et.document_id = d.document_id
            JOIN
                public.sessions s ON et.session_id = s.session_id
            WHERE
                levenshtein(et.word, %s) <= %s
            ORDER BY
                d.document_id, et.page_number, et.x_min, et.y_min;
        """

        # Execute the query with the search term and max_distance
        cur.execute(query, (search_term, max_distance))

        # Fetch results
        results = cur.fetchall()

        if not results:
            print(f"No documents found containing a close match for the word '{search_term}'.")
            return

        # Process and display results, including the original term
        for result in results:
            document_id, document_path, page_count, word, x_min, y_min, x_max, y_max, page_number, session_id = result
            print(f"Original Search Term: {search_term}")
            print(f"Document ID: {document_id}")
            print(f"Document Path: {document_path}")
            print(f"Page Count: {page_count}")
            print(f"Found Word: {word}")
            print(f"Coordinates: ({x_min}, {y_min}) to ({x_max}, {y_max})")
            print(f"Page Number: {page_number}")
            print(f"Session ID: {session_id}")
            print("-" * 50)

            # Insert the search result into the search_result table
            try:
                cur.execute("""
                    INSERT INTO search_result (search_term, session_id, document_id, word, x_min, y_min, x_max, y_max, page_number, match_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                """, (search_term, session_id, document_id, word, x_min, y_min, x_max, y_max, page_number))
                print(f"Search result for '{word}' inserted into 'search_result' table.")
            except Exception as e:
                print(f"Error inserting search result for word '{word}': {e}")

        # Optionally, return the results and original term for further processing
        return {"search_term": search_term, "results": results}

    except Exception as e:
        print(f"Error during search: {e}")

# Part 3: User Input and Search Invocation
search_term = input("Enter the word you want to search for: ").strip()

# Validate search term
if not search_term:
    print("Error: Search term cannot be empty. Please try again.")
else:
    search_word_in_documents(search_term)


# Commit and close the database connection
conn.commit()
cur.close()
conn.close()
