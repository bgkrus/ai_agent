import os
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key == None:
        raise RuntimeError("API key necessary")

    client = genai.Client(api_key=api_key)

    
    parser = argparse.ArgumentParser(description="AI agent")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
       
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents= messages
    )
    
    if response is None or response.usage_metadata is None:
        raise RuntimeError ("failed API request")
    if args.verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    print(response.text)

if __name__=="__main__":
    main()