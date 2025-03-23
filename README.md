# PDF Subject Extractor

A system that processes PDFs directly from Google Cloud Storage to identify key subjects, checks if they exist in a database, and adds new subjects to the database. It uses LLM-enhanced text extraction for better structure understanding and subject identification.

## Features

- Processes PDFs directly from Google Cloud Storage without downloading locally
- Extracts text content from PDFs using both PyPDF2 and LLM-enhanced extraction
- LLM extraction provides structured document analysis (title, authors, abstract, sections)
- Uses Google's Gemini AI to identify key subjects in the document with categorization
- Checks if subjects already exist in a database
- Adds new subjects to the database
- Saves results back to the same GCS bucket as JSON files
- Provides detailed processing reports with structured content

## Requirements

- Python 3.8+
- Google Cloud Platform account with Vertex AI and Storage enabled
- Required Python packages (see requirements.txt)

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up GCP authentication:
   - Create a service account with appropriate permissions
   - Download the JSON key file
   - Set the environment variable: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/keyfile.json"`

4. Create a `.env` file in the parent directory with the following variables:
   ```
   PROJECT_ID=your-gcp-project-id
   GOOGLE_CLOUD_REGION=us-central1
   ```

## Usage

You can use the PDFProcessor class in your code:

```python
from gcp.pdf_sectioner import PDFProcessor

# Initialize the processor with your credentials file
processor = PDFProcessor(debug=True, credentials_path="path/to/service-account-key.json")

# Process a PDF file from GCS
results = processor.process_pdf(
    bucket_name="your-gcs-bucket-name",
    pdf_blob_name="path/to/your/document.pdf"
)

# Results are saved to the same bucket with the same name but .json extension
# e.g., "path/to/your/document.json"

# View the results
print(results)
```

Or run the script directly:

```
python gcp/pdf_sectioner.py
```

## How It Works

1. **PDF Access**: The system reads the PDF directly from Google Cloud Storage as a BytesIO object in memory.

2. **LLM-Enhanced Text Extraction**: 
   - Extracts title, authors, and abstract from the first page
   - Identifies section titles and their content
   - Creates a structured representation of the document

3. **Subject Identification**:
   - Processes the structured content to identify key subjects
   - Assigns importance scores and categories to each subject
   - Provides contextual information for each subject

4. **Database Integration**:
   - Checks if each subject already exists in the database
   - Adds new subjects that don't already exist

5. **Results Storage**:
   - Saves the complete results as a JSON file to the same GCS bucket
   - Uses the same filename as the PDF but with a .json extension

## Database Integration

The current implementation includes placeholder functions for database integration. To integrate with your database:

1. Modify `subject_exists_in_database()` to query your actual database
2. Modify `add_subject_to_database()` to insert data into your actual database

## Output Format

The system generates a detailed JSON output with:

- Document metadata (title, authors, abstract)
- Structured sections of the document
- Extracted subjects with importance scores and categories
- Processing statistics

## License

MIT
