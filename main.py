import argparse
import os 
import sys
from dotenv import load_dotenv; load_dotenv()

from google import genai
from google.genai import types

from prompts import system_prompt
from call_function import call_function, available_functions
from config import MAX_ITERATIONS


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


def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0
        ),
    )

    if response.usage_metadata is None:
        raise RuntimeError("Usage metadata is not available")

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if not response.function_calls:
        print("Response:")
        print(response.text)
        return response.text

    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    function_responses = []
    for call in response.function_calls:
        result = call_function(call, verbose)

        if not result.parts:
            raise Exception("No parts")
        if result.parts[0].function_response is None:
            raise Exception("Response none")
        
        if verbose:
            print(f"-> {result.parts[0].function_response.response}")
        
        function_responses.append(result.parts[0])

    messages.append(types.Content(role="user", parts=function_responses))



def main():
    args = parse_args()

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    client = genai.Client(api_key=GEMINI_API_KEY)
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    for _ in range(MAX_ITERATIONS):
        try:
            final_response = generate_content(client, messages, args.verbose)
            if final_response:
                return
        except Exception as e:
            print(f"Error in generate_content: {e}")

    print(f"Maximum iterations ({MAX_ITERATIONS}) reached.")
    sys.exit(1)


if __name__ == "__main__":
    main()
