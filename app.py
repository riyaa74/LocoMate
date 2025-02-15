from flask import Flask, redirect, url_for, render_template, jsonify, request, session
from config import secrets
import zipfile
import io
import os
import tempfile
from preprocess import curate_user_profile
from recommend import recommend_places
from getPlacesData import get_lat_lon_google
from chatbot import generate_answer, describe_image
import base64
import os

import tempfile
import json

# In-memory storage for user data (resets when the app restarts)
user_data_store = {}

places_api_key = secrets.PLACES_API_KEY
gemini_api_key = secrets.GEMINI_API_KEY
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.secret_key = os.urandom(24)
app.config['GOOGLE_MAPS_API_KEY'] = secrets.PLACES_API_KEY

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_form')
def upload_form():
    return render_template('upload.html')

@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html", api_key=places_api_key)

conversation_history = []

@app.route('/send_message', methods=['POST'])
def send_message():
    global conversation_history
    user_message = request.json.get('message')
    
    # Generate bot response
    bot_response = generate_answer("", "Hello", api_key=gemini_api_key)
    # bot_response = generate_answer(conversation_history, user_message, api_key=gemini_api_key)
    
    # Update conversation history
    conversation_history.append((user_message, bot_response))
    
    return jsonify({'response': bot_response})

@app.route("/preferences")
def preferences():
    return render_template("preferences.html")

@app.route("/radius")
def radius():
    api_key = app.config['GOOGLE_MAPS_API_KEY']
    return render_template("radius.html", api_key=api_key)

@app.route('/create_itinerary', methods=['POST'])
def create_itinerary():
    selected_places = request.json.get('places')
    session['selected_places'] = selected_places  # Store in session
    return jsonify({'success': True})

@app.route('/create_cart', methods=['POST'])
def create_cart():
    selected_places = request.json.get('places')
    session['selected_places'] = selected_places  # Store in session
    return jsonify({'success': True})

@app.route("/cart")
def cart():
    selected_places = session['selected_places'] 
    return render_template('cart.html', places=selected_places)

@app.route('/budget.html')
def budget():
    selected_places = session.get('selected_places', [])
    print(selected_places)
    return render_template('budget.html', places=selected_places)

@app.route("/submit_preferences", methods=["POST"])
def submit_preferences():
    preferences = request.json.get('preferences', [])
    if len(preferences) < 3:
        return jsonify({"error": "Please select at least 3 preferences"}), 400

    # Ensure user_profile exists in the session
    if 'user_profile' not in session:
        session['user_profile'] = {}

    session['user_profile']['preferences'] = preferences  # Store preferences inside user_profile

    return jsonify({"success": "Preferences saved"}), 200

@app.route("/recommendations")
def recommendations():
    api_key = app.config['GOOGLE_MAPS_API_KEY']
    return render_template("recommendations.html", api_key=api_key)

# @app.route("/recommendations-data")
# def recommendations_data():
#     formatted_text = session.get('formatted_text')
#     recommendations = session.get('recommendations')
#     location = session.get('location')
#     place = get_lat_lon_google(location,places_api_key)
#     print(recommendations, ' in recommendations-data')

#     if not formatted_text or not recommendations:
#         return jsonify({"error": "No recommendations found"}), 400

#     return jsonify({"text": formatted_text, "recommendations": recommendations, "lat":place[0], "lon":place[1]})

@app.route("/recommendations-data")
def recommendations_data():
    user_id = session.get('user_id')
    if not user_id or user_id not in user_data_store:
        return jsonify({"error": "User session expired"}), 400

    user_data = user_data_store[user_id]

    formatted_text = user_data.get('formatted_text')
    recommendations = user_data.get('recommendations')
    location = user_data.get('location')
    
    if not formatted_text or not recommendations:
        return jsonify({"error": "No recommendations found"}), 400

    place = get_lat_lon_google(location, places_api_key)

    return jsonify({"text": formatted_text, "recommendations": recommendations, "lat": place[0], "lon": place[1]})

@app.route('/send_photo', methods=['POST'])
def send_photo():
    photo_data = request.json.get('photo')
    
    # Decode the base64-encoded photo
    photo_bytes = base64.b64decode(photo_data.split(',')[1])
    
    # Save the photo to a temporary location
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
    #     temp_file.write(photo_bytes)
    #     photo_path = temp_file.name
    
    # Generate a response using the LLM
    # user_message = f"User uploaded a photo. Photo saved at {photo_path}."
    global conversation_history
    # bot_response = generate_answer(conversation_history, user_message, api_key=gemini_api_key)
    bot_response = describe_image(photo_bytes, gemini_api_key)
    
    # Update conversation history
    conversation_history.append(("Image", bot_response))
    
    return jsonify({'response': bot_response})

# @app.route("/submit_form", methods=["POST"])
# def submit_form():
#     if "file-upload" not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files["file-upload"]

#     if file.filename == "":
#         return jsonify({"error": "No selected file"}), 400

#     if not file.filename.endswith(".zip"):
#         return jsonify({"error": "Invalid file format. Please upload a ZIP file"}), 400
    
#     user_info = {
#         "location": request.form.get("location", "").strip(),
#         "additional_info": request.form.get("additional-info", "").strip(),
#     }
    
#     with tempfile.TemporaryDirectory() as temp_dir:
#         with zipfile.ZipFile(io.BytesIO(file.read()), "r") as zip_ref:
#             zip_ref.extractall(temp_dir)  

#         user_profile = curate_user_profile(temp_dir+'/Takeout', user_info)

#     session['user_profile'] = user_profile
#     #print(user_profile)
#     #print(request.form.get("location", "").strip(), "in submit form of APP.PY")
#     session['location'] = request.form.get("location", "").strip()

#     return redirect(url_for("radius"))

@app.route("/submit_form", methods=["POST"])
def submit_form():
    if "file-upload" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file-upload"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".zip"):
        return jsonify({"error": "Invalid file format. Please upload a ZIP file"}), 400

    user_id = os.urandom(8).hex()  # Generate a unique ID
    session['user_id'] = user_id   # Store only the ID in session

    user_info = {
        "location": request.form.get("location", "").strip(),
        "additional_info": request.form.get("additional-info", "").strip(),
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(io.BytesIO(file.read()), "r") as zip_ref:
            zip_ref.extractall(temp_dir)  

        user_profile = curate_user_profile(temp_dir+'/Takeout', user_info)

    user_data_store[user_id] = {
        'user_profile': user_profile,
        'location': user_info['location']
    }  # Store in memory, not session

    return redirect(url_for("radius"))

# @app.route("/process_recommendations")
# def process_recommendations():
#     user_profile = session.get('user_profile')
#     location = session.get('location')
    
#     if not user_profile or not location :
#         return jsonify({"error": "Missing user profile, location"}), 400
#     #rint(user_profile," app.py")
#     recommendations, text = recommend_places(user_profile, location)
#     #print(location+" app.py")
#     #print(recommendations)
#     # Store recommendations in the session or temporary storage
#     session['recommendations'] = recommendations
#     print(recommendations)
#     session['formatted_text'] = text

#     return redirect(url_for("recommendations"))

@app.route("/process_recommendations")
def process_recommendations():
    user_id = session.get('user_id')
    if not user_id or user_id not in user_data_store:
        return jsonify({"error": "User session expired"}), 400

    user_profile = user_data_store[user_id]['user_profile']
    location = user_data_store[user_id]['location']

    recommendations, text = recommend_places(user_profile, location)

    # Store recommendations in memory
    user_data_store[user_id]['recommendations'] = recommendations
    user_data_store[user_id]['formatted_text'] = text

    return redirect(url_for("recommendations"))

if __name__ == '__main__':
    app.run(debug=True)
