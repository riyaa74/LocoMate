import requests
import json
from config import secrets
from google import genai
import re

# with open('user_profile.json', 'r') as file:
#     user_profile = json.load(file)

api_key=secrets.GEMINI_API_KEY 

#location = "New York City"


# def recommend_places(user_profile, location):
#     prompt= f"""
#     Here is a user's profile:
#     - Favorite places: {', '.join(user_profile['saved_places']['favorites'])}
#     - Places they want to visit: {', '.join(user_profile['saved_places']['want_to_go'])}
#     - Visited places: {', '.join(user_profile['visited_places'])}
#     - Interests: {', '.join(user_profile['discover_interests']['follows'])}, {', '.join(user_profile['discover_interests']['liked_content'])}

#     Suggest fun activities, places to visit, and things to do in {location} based on this user's profile.
#     """

#     client = genai.Client(api_key=api_key)
#     response = client.models.generate_content(
#         model='gemini-2.0-flash',
#         contents=prompt,
#     )

#     return response.text
#     - Labeled places: {', '.join(user_profile['labeled_places'])}
#     # - Reservations: {', '.join(user_profile['reservations'])}

def recommend_places(user_profile, location):
    prompt = f"""
    Here is a user's profile:
    - Maps they have named: {', '.join(user_profile['maps_names'])}
    - Saved places: {', '.join(user_profile['saved_titles'])}
    - Followed entities: {', '.join(user_profile['discover_followed_entities'])}



    This user has provided additional information: {' '.join(user_profile['user_info']['additional_info'])}.

    
    Suggest fun activities, places to visit, and things to do in {location} based on this user's profile.

    **Format the response as a JSON object with the following structure:**

    {{
        "text": \"\"\"
        **Recommendations Breakdown:**

        [Provide a detailed breakdown of recommendations based on the user's interests, formatted with markdown-style headings and bullet points.]

        \"\"\",
        "recommendations": [
            {{
                "name": "PLACE_NAME",
                "rating": RATING,
                "vicinity": "LOCATION_ADDRESS",
                "types": "TYPES_OF_PLACE",
                "location": {{"lat": LATITUDE, "lng": LONGITUDE}}
            }},
            ...
        ]
    }}

    Ensure the `"text"` field includes well-structured explanations but no markdown and the `"recommendations"` list contains relevant places with proper attributes. Have types of places from gym, groceries, night out, restaurants, museums and some other's too
"""


    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    )
    print(location+" in recommend.py")
    json_data = re.search(r'\{.*\}', response.text, re.DOTALL)

    if json_data:
        json_string = json_data.group()
        #print(json_string)

        # Parse the JSON string
        response_json = json.loads(json_string)

        # Extract formatted text and recommendations
        formatted_text = response_json["text"]
        recommendations = response_json["recommendations"]

        #print("Formatted Text:", formatted_text)
        #print("Recommendations:", recommendations)
    else:
        print("No JSON data found.")
    # Print extracted results
    #print("Formatted Text:\n", formatted_text)
    #print("\nRecommendations List:\n", recommendations)
    return recommendations, formatted_text

