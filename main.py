import os
import sys
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types
from system_prompt import prompt
from call_function import available_functions, call_function

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

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    
    for x in range(20):
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents= messages,
            config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=prompt
    )
        )
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)
        if response is None or response.usage_metadata is None:
            raise RuntimeError ("failed API request")
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        if response.function_calls:
            function_responses = []
            for function_call in response.function_calls:
                result = call_function(function_call, args.verbose)
                
                if not result.parts:
                    raise Exception ("should have a non-empty .parts list")
                if not result.parts[0].function_response:
                    raise Exception ("It should be a FunctionResponse object")
                if not result.parts[0].function_response.response:
                    raise Exception ("the actual function result should not be None")
                if args.verbose:
                    print(f"-> {result.parts[0].function_response.response}")
                function_responses.append(result.parts[0])
            messages.append(types.Content(role="user", parts=function_responses))
        else:
            print(response.text)
            return
    print("maximum number of iterations is reached") 
    sys.exit(1)
if __name__=="__main__":
    main()