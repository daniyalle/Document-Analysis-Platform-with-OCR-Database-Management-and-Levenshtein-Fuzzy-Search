import os
import cv2
import psycopg2
import numpy as np
from pdf2image import convert_from_path

# Database connection
try:
    conn = psycopg2.connect("dbname= user= password=")
    cur = conn.cursor()
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Directories
documents_directory = r''
processed_directory = r''
os.makedirs(processed_directory, exist_ok=True)

def draw_borders(image, word_details):
    """
    Draws borders around words on the image.
    Adds 1mm margin on each side and uses a 2mm thick border.
    """
    try:
        dpi = 300  # Assuming images have 300 DPI
        pixels_per_mm = dpi / 25.4  # Convert millimeters to pixels
        margin = int(pixels_per_mm * 1)  # 1mm margin in pixels
        border_thickness = int(pixels_per_mm * 0.5)  # 2mm thick border

        for word_info in word_details:
            # Adjust coordinates to include the margin
            x_min = max(0, word_info['x_min'] - margin)  # Ensure not below 0
            y_min = max(0, word_info['y_min'] - margin)  # Ensure not below 0
            x_max = word_info['x_max'] + margin
            y_max = word_info['y_max'] + margin

            # Draw the rectangle
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 0, 255), thickness=border_thickness)

        return image
    except Exception as e:
        print(f"Error drawing borders: {e}")
        return image

def process_document(document_path, word_details, output_path):
    """
    Processes a document (PDF or image) by drawing borders around words found in the search result.
    """
    try:
        if document_path.endswith('.pdf'):
            # Process PDF
            images = convert_from_path(document_path, dpi=300)
            for page_number, image in enumerate(images, start=1):
                # Convert PIL image to OpenCV format
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Filter words for the current page
                page_words = [word for word in word_details if word['page_number'] == page_number]

                # Draw borders
                processed_image = draw_borders(open_cv_image, page_words)

                # Save the processed image
                output_page_path = os.path.join(output_path, f"{os.path.basename(document_path)}_page_{page_number}.png")
                cv2.imwrite(output_page_path, processed_image)
        else:
            # Process image
            image = cv2.imread(document_path)
            if image is None:
                print(f"Failed to read image {document_path}")
                return

            # Draw borders
            processed_image = draw_borders(image, word_details)

            # Save the processed image
            output_image_path = os.path.join(output_path, os.path.basename(document_path))
            cv2.imwrite(output_image_path, processed_image)
    except Exception as e:
        print(f"Error processing document {document_path}: {e}")

def process_search_results():
    """
    Fetches search results from the database and processes the documents.
    """
    try:
        # Query to join search_result with documents to fetch document_path
        cur.execute("""
            SELECT sr.document_id, d.document_path, sr.word, sr.x_min, sr.y_min, sr.x_max, sr.y_max, sr.page_number
            FROM search_result sr
            JOIN documents d ON sr.document_id = d.document_id;
        """)
        results = cur.fetchall()

        if not results:
            print("No search results found in the database.")
            return

        # Group results by document_path
        documents = {}
        for result in results:
            document_id, document_path, word, x_min, y_min, x_max, y_max, page_number = result
            if document_path not in documents:
                documents[document_path] = []
            documents[document_path].append({
                'word': word,
                'x_min': x_min,
                'y_min': y_min,
                'x_max': x_max,
                'y_max': y_max,
                'page_number': page_number
            })

        # Process each document
        for document_path, word_details in documents.items():
            original_document_path = os.path.join(documents_directory, document_path)
            if not os.path.exists(original_document_path):
                print(f"Document not found: {original_document_path}")
                continue

            # Set output path
            output_path = os.path.join(processed_directory, os.path.splitext(os.path.basename(document_path))[0])
            os.makedirs(output_path, exist_ok=True)

            # Process the document
            process_document(original_document_path, word_details, output_path)

    except Exception as e:
        print(f"Error processing search results: {e}")

# Main Execution
if __name__ == "__main__":
    process_search_results()

# Commit and close the database connection
conn.commit()
cur.close()
conn.close()
