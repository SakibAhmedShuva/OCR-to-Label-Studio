from flask import Flask, request, jsonify
import os
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from PIL import Image
import numpy as np
import datetime
import uuid
import json
from typing import List, Dict, Union
import logging
from werkzeug.utils import secure_filename
from post_processing import *
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def save_json_response(data: Dict) -> None:
    """Save JSON response to a file in json_outputs folder."""
    # Create json_outputs folder if it doesn't exist
    output_folder = 'json_outputs'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"result_{timestamp}.json"
    filepath = os.path.join(output_folder, filename)
    
    # Save JSON data to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"JSON response saved to {filepath}")
    except Exception as e:
        logger.error(f"Error saving JSON response to file: {str(e)}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def stretch_image(img: Image.Image, n_pixels: int = 50) -> Image.Image:
    """Stretch image by adding white pixels to right and bottom."""
    width, height = img.size
    new_img = Image.new('L', (width + n_pixels, height + n_pixels), 255)
    new_img.paste(img, (0, 0))
    return new_img

def post_process_text(text: str) -> str:
    """Clean up extracted text."""
    if text:
        text = text.strip()
        text = german_word_correction(text)
        return text
    return ""

def create_label_studio_annotation(text: str) -> Dict:
    """Create annotation in Label Studio format without annotations."""
    output = {
        "id": 1,
        "data": {"text": text},
        "meta": {},
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "inner_id": 1,
        "project": 3
    }
    return output

def process_image(image_path: str, n_pixels: int = 50) -> Dict:
    """Process image and return Label Studio formatted results."""
    try:
        # Initialize OCR model
        # model = ocr_predictor(pretrained=True)
        model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True, resolve_blocks=False)
        
        # Process image
        img = Image.open(image_path).convert("L")  # Convert to grayscale
        img = stretch_image(img, n_pixels)
        
        # Convert PIL Image to numpy array
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=-1)
        img_array = np.repeat(img_array, 3, axis=-1)
        
        # Perform OCR
        result = model([img_array])
        
        # Process OCR results
        current_y = -1
        line_texts = []
        temp_line = []
        
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    line_text = " ".join([word.value for word in line.words])
                    processed_text = post_process_text(line_text)
                    if processed_text:
                        line_y = line.geometry[0][1]
                        
                        if abs(line_y - current_y) > 0.01:
                            if temp_line:
                                line_texts.append(" ".join(temp_line))
                                temp_line = []
                            current_y = line_y
                        
                        temp_line.append(processed_text)
        
        if temp_line:
            line_texts.append(" ".join(temp_line))
        
        full_text = "\n".join(line_texts)
        
        return create_label_studio_annotation(full_text)
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise

@app.route('/process-image', methods=['POST'])
def process_image_endpoint():
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image
        result = process_image(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)

        # Save JSON response to file (without affecting the API response)
        save_json_response(result)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in API endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
