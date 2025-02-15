import google.generativeai as genai
from PIL import Image
import io

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