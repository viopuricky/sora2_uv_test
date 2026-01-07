import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def main():
    print("Hello from sora2-uv-test!")
    

    # Get API key from environment variable
    test_api_key = os.getenv('OPENAI_API_KEY')
    if not test_api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return

    client = OpenAI(api_key=test_api_key)

    response = client.responses.create(
    model="gpt-5-nano",
    input="tell me a joke about computers",
    store=True,
    )

    print(response.output_text);



if __name__ == "__main__":
    main()
