import google.generativeai as genai
from PIL import Image
import io
import re
import json
import os

def describe_image(image_data, api_key):

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")

    try:
        image = Image.open(io.BytesIO(image_data))

        image_content = {
            'mime_type': 'image/jpeg',  # Adjust if your image is in a different format
            'data': image_data
        }

        prompt = "Describe the place shown in the image."
        response = model.generate_content(contents=[prompt, image_content])
        return response.text
    except Exception as e:
        return f"An error occurred while processing the image: {e}"

def generate_answer(conversation_history, new_question, model="gemini-2.0-flash", temperature=0.5, api_key=""):
    """
    Generates a precise answer based on past conversation history and a newly asked question using Gemini API.
    
    Parameters:
        conversation_history (list): A list of past conversation tuples (user_message, bot_response).
        new_question (str): The new question asked by the user.
        model (str): The language model to use (default: "gemini-pro").
        temperature (float): Controls randomness (0 = deterministic, 1 = creative).
        api_key (str): Your Gemini API key.
    
    Returns:
        str: The generated response.
    """
    
    # Initialize Gemini API
    genai.configure(api_key=api_key)
    
    # Construct a well-structured prompt
    prompt = """
    Below is the conversation history between you and the user.
    
    {conversation_context}
    
    Now, the user has asked a new question:
    User: {new_question}
    
    Respond concisely and accurately based on the past context.
    Don't use markdown
    """.strip()
    
    # Format conversation history
    conversation_context = "\n".join(
        [f"User: {user}\nBot: {bot}" for user, bot in conversation_history]
    )
    
    formatted_prompt = prompt.format(
        conversation_context=conversation_context, new_question=new_question
    )
    
    # Generate response using Gemini API
    model = genai.GenerativeModel(model)
    response = model.generate_content(formatted_prompt, generation_config={"temperature": temperature})
    
    return str(response.text.strip())

def generate_itinerary(dest, api_key):

    places = [place['name'] for place in dest]

    # Configure the Gemini API key
    genai.configure(api_key=api_key)

# Initialize the GenerativeModel
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    # Create a prompt for the Gemini model
    prompt = f"Create a detailed itinerary for visiting the following places in order: {', '.join(places)}."

    # Generate a response from the Gemini model
    response = model.generate_content(prompt)

    # Extract and return the generated itinerary
    itinerary = response.text
    return itinerary

def estimate_travel_costs(places, api_key):

    destinations = [place['name'] for place in places]


    # Create the prompt
    prompt = (
        "For each of the following destinations, provide an estimated travel cost breakdown "
        "in JSON format with three price ranges: 'Lower end', 'Mid range', and 'High range'. "
        "Each range should include an exact numerical 'estimated_cost' in USD and a two-sentence "
        "'description' explaining the pricing rationale.\n\nDestinations:\n"
    )
    for destination in destinations:
        prompt += f"- {destination}\n"
    prompt += (
        "\nEnsure the output strictly follows this JSON structure:\n\n"
        "{\n"
        '  "Destination Name": {\n'
        '    "Lower end": {\n'
        '      "estimated_cost": 0,\n'
        '      "description": "Two-sentence description."\n'
        "    },\n"
        '    "Mid range": {\n'
        '      "estimated_cost": 0,\n'
        '      "description": "Two-sentence description."\n'
        "    },\n"
        '    "High range": {\n'
        '      "estimated_cost": 0,\n'
        '      "description": "Two-sentence description."\n'
        "    }\n"
        "  },\n"
        "  ...\n"
        "}"
    )

    # Generate the content
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)

    # Extract the JSON-like content from the response
    json_pattern = re.compile(r'\{.*\}', re.DOTALL)
    match = json_pattern.search(response.text)
    if match:
        json_content = match.group()
        try:
            # Parse the JSON content
            cost_estimates = json.loads(json_content)
            return cost_estimates
        except json.JSONDecodeError:
            print("Failed to decode JSON from the model's response.")
            return None
    else:
        print("No JSON content found in the model's response.")
        return None