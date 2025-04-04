# mAIstro!

Being students ourselves, we've explored the depths of AI-powered education apps that claim to be the place to study. There are obviously AI study programs galore, but they all lack in a specific area: consistency while staying true to the content they need to teach.

Key Features:
- Smart Organization: Users upload their full course materials, and Maistro intelligently segments and categorizes snippets into precise subjects (e.g., vectors in Linear Algebra, decision trees in Machine Learning). This cross-document system enables subject-specific study materials.

- Adaptive Quizzes & Mastery System: Maistro tracks user understanding, generating personalized quizzes and optimizing future study sessions based on performance. It applies strategic forgetting to reinforce long-term retention 1. Over time, previously mastered topics fade, encouraging continued review and reinforcement.

- Precision Study Support: The mastery system identifies weak subjects and pinpoints exact locations in the user’s study materials for targeted revision. This grounded learning approach ensures adaptability while staying true to course content.

  ![Course Page](https://private-user-images.githubusercontent.com/66640943/425821204-a838071c-836e-4db4-a4de-d20442f1d1cf.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDI3MzA2ODUsIm5iZiI6MTc0MjczMDM4NSwicGF0aCI6Ii82NjY0MDk0My80MjU4MjEyMDQtYTgzODA3MWMtODM2ZS00ZGI0LWE0ZGUtZDIwNDQyZjFkMWNmLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAzMjMlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMzIzVDExNDYyNVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTlkMjIxOGMyNmM5ZmUzMDU2YzM5YTMzODE1MWVkOTUyZGY1OWY5OWI2ZTM3NzUyNDkzNzBmNWIwZWU4Yzg1ZjUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.3jMLbbM7j4L7tPKSwgAaVGekys5CRq8W-WMYu2J-sqE)
*Interface when looking at a course*
  

![Snippets View](https://private-user-images.githubusercontent.com/66640943/425821205-09dc9ab4-98c5-4d02-b781-3e1542f7a8d5.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDI3MzA2ODUsIm5iZiI6MTc0MjczMDM4NSwicGF0aCI6Ii82NjY0MDk0My80MjU4MjEyMDUtMDlkYzlhYjQtOThjNS00ZDAyLWI3ODEtM2UxNTQyZjdhOGQ1LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAzMjMlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMzIzVDExNDYyNVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTUyOGMxMWM3MmRkOTk4ODNmOWE0YWUwNjZhZmQ5ZjAzYWZiOWZkOGExNzliMDJlNjQyZjY4NTViZGZhZDhiMjgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.vGw8k6iN81AuPefbDjJ4aFg2WmM2DNDAGf2kUhEI-IU)
*Seeing all the relevant snippets from the uploaded data for this subject*

![Another Snippets View](https://private-user-images.githubusercontent.com/66640943/425821464-337170d0-4be7-4382-ad7c-df3816d62f39.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDI3MzA4MTEsIm5iZiI6MTc0MjczMDUxMSwicGF0aCI6Ii82NjY0MDk0My80MjU4MjE0NjQtMzM3MTcwZDAtNGJlNy00MzgyLWFkN2MtZGYzODE2ZDYyZjM5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAzMjMlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMzIzVDExNDgzMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWQ1YTQ4OGEzNTZjNzM2NGE1ZGE0YjY5YTA3MTYwNmI5MDc5ZmNhZTY2MzBlODAzNzZiNjQ1YjhkNWZmNDQ5YjUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.UO2vnHomMqxF1PpDL-1IHoqe2RpBtxwV6aMIz-8Mzow)
*Seeing all the relevant snippets from the uploaded data for another subject*

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
