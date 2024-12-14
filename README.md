# OCR to Label Studio Converter

A Flask-based OCR application that processes images while maintaining their exact layout and generates JSON output compatible with Label Studio import format. This tool is particularly optimized for processing German medical documents with specialized text correction features.

## Features

- Image OCR processing with layout preservation
- Automatic conversion to Label Studio compatible JSON format
- Built-in German medical terminology corrections
- Support for multiple image formats (PNG, JPG, JPEG, GIF, TIFF, BMP)
- Automatic text cleaning and formatting
- Layout-aware text extraction that maintains the original document structure
- Built-in health check endpoint for monitoring
- Automatic JSON output storage with timestamps

## Prerequisites

- Python 3.x
- Flask
- python-doctr
- Pillow
- NumPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SakibAhmedShuva/OCR-to-Label-Studio.git
cd OCR-to-Label-Studio
```

2. Install the required dependencies:
```bash
pip install flask doctr-ocr Pillow numpy
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. The server will start on port 5000 by default. You can send POST requests to `/process-image` endpoint with image files.

### API Endpoints

#### POST /process-image
Process an image and get Label Studio compatible JSON output.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file)

**Response:**
```json
{
    "id": 1,
    "data": {
        "text": "Extracted text with preserved layout"
    },
    "meta": {},
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "inner_id": 1,
    "project": 3
}
```

#### GET /health
Health check endpoint to verify service status.

**Response:**
```json
{
    "status": "healthy"
}
```

## Image Processing Features

- Grayscale conversion for better OCR accuracy
- Image stretching to improve boundary text recognition
- Intelligent line merging based on Y-coordinates
- Special character and unit corrections for medical terminology

## Text Post-Processing

The application includes specialized post-processing for German medical texts:
- Automatic correction of commonly misread German medical terms
- Special character corrections (â → ä, ô → ö, etc.)
- Unit standardization (g7dl → g/dl, /u1 → /µl, etc.)
- Layout preservation using newline characters

## Output

- Processed results are automatically saved in the `json_outputs` folder
- Each output file is timestamped for easy tracking
- JSON format is directly compatible with Label Studio import functionality

## Error Handling

- Comprehensive error logging
- Input validation for file types
- Automatic cleanup of temporary files
- Detailed error responses for API calls

## Project Structure

```
OCR-to-Label-Studio/
├── app.py              # Main Flask application
├── post_processing.py  # Text correction utilities
├── uploads/           # Temporary folder for uploaded images
└── json_outputs/      # Folder for processed JSON outputs
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

## Acknowledgments

- Built with [python-doctr](https://github.com/mindee/doctr) for OCR processing
- Compatible with [Label Studio](https://labelstud.io/) for annotation
