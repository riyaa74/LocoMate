import os
import json
import pandas as pd

# Define the base directory (update this path accordingly)
# base_dir = "/content/drive/MyDrive/hackher/Takeout"

# Data storage
extracted_data = {
    "maps_names": [],
    "saved_titles": [],
    "discover_followed_entities": [],
    "reservations": [],
    "labeled_places": []
}

# Function to extract 'name' from Maps JSON files
def extract_name_from_maps(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            names = [feature["properties"]["location"]["name"] for feature in data.get("features", []) if "properties" in feature]
            extracted_data["maps_names"].extend(names)
    except Exception as e:
        print(f"Error processing Maps JSON file {file_path}: {e}")

# Function to extract 'Title' column from CSV files in Saved folder
def extract_title_from_saved(file_path):
    try:
        df = pd.read_csv(file_path)
        if "Title" in df.columns:
            titles = df["Title"].dropna().tolist()
            extracted_data["saved_titles"].extend(titles)
    except Exception as e:
        print(f"Error processing Saved CSV file {file_path}: {e}")

# Function to extract 'Followed Entity' column from CSV files in Discover folder
def extract_followed_entity_from_discover(file_path):
    try:
        df = pd.read_csv(file_path)
        if "Followed Entity" in df.columns:
            followed_entities = df["Followed Entity"].dropna().tolist()
            extracted_data["discover_followed_entities"].extend(followed_entities)
    except Exception as e:
        print(f"Error processing Discover CSV file {file_path}: {e}")

# Function to extract 'name' and 'merchantName' from JSON files in Purchases & Reservations and My labeled places folder
def extract_booking_info(file_path, category):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            name = data.get("booking", {}).get("name", None)
            merchant_name = data.get("booking", {}).get("merchantName", None)
            if category == "reservations":
                extracted_data["reservations"].append({"name": name, "merchantName": merchant_name})
            elif category == "labeled_places":
                extracted_data["labeled_places"].append({"name": name, "merchantName": merchant_name})
    except Exception as e:
        print(f"Error processing Booking JSON file {file_path}: {e}")

# Function to iterate through folders and process them uniquely
def curate_user_profile(directory, user_info):
    for root, dirs, files in os.walk(directory):
        folder_name = os.path.basename(root)
        parent_folder = os.path.basename(os.path.dirname(root))

        if folder_name == "Maps (your places)":
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".json"):
                    extract_name_from_maps(file_path)

        elif folder_name == "Saved":
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".csv"):
                    extract_title_from_saved(file_path)

        elif folder_name == "Discover":
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".csv"):
                    extract_followed_entity_from_discover(file_path)

        elif folder_name == "Purchases & Reservations":
            for subdir in dirs:
                if subdir == "Reservations":
                    reservations_path = os.path.join(root, subdir)
                    for reservation_file in os.listdir(reservations_path):
                        reservation_file_path = os.path.join(reservations_path, reservation_file)
                        if reservation_file.endswith(".json"):
                            extract_booking_info(reservation_file_path, "reservations")

        elif folder_name == "Maps":
            for subdir in dirs:
                if subdir == "My labeled places":
                    labeled_places_path = os.path.join(root, subdir)
                    for file in os.listdir(labeled_places_path):
                        file_path = os.path.join(labeled_places_path, file)
                        if file.endswith(".json"):
                            extract_booking_info(file_path, "labeled_places")

        elif parent_folder == "Purchases & Reservations" and folder_name == "Reservations":
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".json"):
                    extract_booking_info(file_path, "reservations")

        elif parent_folder == "Maps" and folder_name == "My labeled places":
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".json"):
                    extract_booking_info(file_path, "labeled_places")

    print(f'In preprocess :{directory}')
    return {
        "user_info": user_info,
        "maps_names": extracted_data['maps_names'],
        "saved_titles": extracted_data['saved_titles'],
        "discover_followed_entities": extracted_data['discover_followed_entities'],
        "reservations": extracted_data['reservations'],
        "labeled_places":extracted_data["labeled_places"]
    }
