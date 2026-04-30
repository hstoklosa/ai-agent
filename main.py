import argparse
import os 
from dotenv import load_dotenv; load_dotenv()

from google import genai
from google.genai import types

from prompts import system_prompt
from call_function import call_function, available_functions


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
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    return parser.parse_args()


def generate_content(client, messages):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0
        ),
    )
    return response


def main():
    args = parse_args()

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    client = genai.Client(api_key=GEMINI_API_KEY)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    response = generate_content(client, messages)

    if response.usage_metadata is None:
        raise RuntimeError("Usage metadata is not available")

    if args.verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    print(response.text)

    if response.function_calls:
        function_results = []
        for call in response.function_calls:
            function_call_result = call_function(call, args.verbose)

            if not function_call_result.parts:
                raise Exception("No parts")
            if function_call_result.parts[0].function_response is None:
                raise Exception("Response none")
            
            function_results.append(function_call_result.parts[0])

            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")




if __name__ == "__main__":
    main()
