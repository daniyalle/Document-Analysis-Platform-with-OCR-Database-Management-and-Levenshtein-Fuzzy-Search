# Document-Analysis-Platform-with-OCR-Database-Management-and-Levenshtein-Fuzzy-Search
Python | PostgreSQL | SQL | Computer Vision | Search Engine | Database and Session Management | Testing

![searched_tocken](https://github.com/user-attachments/assets/f78633fe-2fcf-4dc1-b05f-b9d6d2bfb2f4)


Executive Summary
This project is a comprehensive document processing system that combines optical character recognition (OCR), database management, and advanced search capabilities to create a robust solution for document analysis and retrieval. The system is designed to handle both high-quality and low-quality documents, with specific mechanisms to address common issues found in scanned materials.

System Architecture
1. Optical Character Recognition (OCR) Processing
The core of the system uses Tesseract OCR to extract text from documents. The process includes:
•	Conversion of PDF documents to images using pdf2image
•	Batch processing of documents in groups of 10 pages for efficiency
•	Extraction of text along with coordinate information for spatial awareness
•	Handling of both PDF and image file formats (JPG, PNG, JPEG)
2. Database Management
A PostgreSQL database serves as the central repository for all document data:
•	documents table: Stores metadata including document paths, session IDs, and page counts
•	extracted_texts table: Contains OCR results with word coordinates and page numbers
•	sessions table: Tracks processing sessions with start and end times
•	search_result table: Records search operations and matches
3. Session Management
The system implements session-based processing to:
•	Allow users to start new sessions or continue existing ones
•	Clear previous data when starting fresh
•	Track processing history and timing
•	Maintain contextual information across document processing operations
4. Search Engine with Levenshtein Distance
The search functionality employs fuzzy matching using Levenshtein distance to:
•	Find approximate matches when exact words aren't found
•	Address common OCR errors from low-quality scans
•	Allow up to 2 character differences between search terms and document text
•	Return detailed results including document paths, coordinates, and session information
5. Visualization and Word Bordering
The system provides visual feedback by:
•	Drawing borders around search results in original documents
•	Adding 1mm margins and 2mm thick red borders for clarity
•	Saving annotated versions of documents for review
•	Handling both PDF and image formats for output
6. Noise Addition and Limitation Testing
A dedicated module degrades document quality to:
•	Test system robustness under challenging conditions
•	Simulate real-world scanning issues like blur and compression artifacts
•	Systematically evaluate performance with variable noise intensity
•	Create test documents with controlled quality degradation
Workflow Overview
1.	Document Ingestion: PDF and image files are processed through the OCR pipeline
2.	Data Storage: Extracted text and metadata are stored in the database
3.	Search Operations: Users can perform fuzzy searches across all documents
4.	Visualization: Search results are highlighted in original documents
5.	Quality Testing: Documents can be degraded to assess system performance limits
Technical Implementation
•	Python: Primary programming language
•	OpenCV: Image processing for OCR preparation
•	Tesseract: OCR engine for text extraction
•	PostgreSQL: Database management system
•	PyPDF2: PDF manipulation for testing module
•	Pillow (PIL): Image processing for visualization and degradation
Performance Considerations
•	Batch processing improves efficiency for large documents
•	Session management allows for historical tracking
•	Fuzzy search balances accuracy and recall for low-quality scans
•	Visualization components provide user-friendly results presentation
