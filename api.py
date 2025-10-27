# API for Luminaire Testing and Monocular Depth Distance
from flask import Flask, request, jsonify
import cv2
import numpy as np
from pipeline import LightLocalization3D

app = Flask(__name__)

# Initialize the pipeline
pipeline = LightLocalization3D()

@app.route('/detect', methods=['POST'])
def detect():
    """
    Perform luminaire detection on an uploaded image.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Read the image
        in_memory_file = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(in_memory_file, cv2.IMREAD_COLOR)

        # Process the image
        results = pipeline.process_image(img)

        return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
