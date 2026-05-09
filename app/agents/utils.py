from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

FLASH_MODEL = "gemini-2.5-flash"
PRO_MODEL = "gemini-2.5-pro"


def generate_response(prompt, model=FLASH_MODEL):

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text


def test_gemini():

    return generate_response(
        "Say hello professionally."
    )