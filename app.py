from flask import Flask, render_template, request, redirect, url_for, flash
import os
import numpy as np
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from PIL import Image

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'secret_key'

# Load the embedding model and database
embedding_model = tf.keras.models.load_model('model/embedding_model.h5')
with open('model/database.pkl', 'rb') as file:
    database = pickle.load(file)

# Function to preprocess the uploaded image
def preprocess_image(image_path):
    img = Image.open(image_path).resize((160, 160))  # Resize to 160x160
    img = np.array(img) / 255.0                     # Normalize to [0, 1]
    img = np.expand_dims(img, axis=0)               # Add batch dimension
    return img

# Function to find the closest match
def find_match(test_image):
    test_embedding = embedding_model.predict(test_image).flatten()
    max_similarity = -1
    matched_label = None

    for label, embeddings in database.items():
        for embedding in embeddings:
            similarity = cosine_similarity([test_embedding], [embedding])[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                matched_label = label

    return matched_label, max_similarity

# Route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            # Save the file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Preprocess and predict
            test_image = preprocess_image(filepath)
            matched_label, similarity = find_match(test_image)
            
            return render_template('index.html', 
                                   uploaded_image=filepath, 
                                   matched_label=matched_label, 
                                   similarity=similarity)
    
    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
