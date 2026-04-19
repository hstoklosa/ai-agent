import argparse
import os 
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")



def parse_args():
    parser = argparse.ArgumentParser(description="AI Coding Agent")
    parser.add_argument(
        "user_prompt", 
        type=str,
        help="The prompt for the AI agent to process."
    )
    return parser.parse_args()


def generate_content(client, messages):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages
    )
    return response

def main():
    args = parse_args()

    client = genai.Client(api_key=GEMINI_API_KEY)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    response = generate_content(client, messages)

    if response.usage_metadata is None:
        raise RuntimeError("Usage metadata is not available")

    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    print(response.text)


if __name__ == "__main__":
    main()
