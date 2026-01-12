import os
from datetime import datetime
from dotenv import load_dotenv
import boto3
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def main():
    print("Hello from sora2-uv-test!")
    
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_FREE_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return


    # Assign job to OpenAI
    client = OpenAI(api_key=api_key)

    response = client.responses.create(             # test with text response only
        model="gpt-5-nano",
        input="tell me a joke about computers",
        store=True,
    )

    #Get response from OpenAI
    output_text = response.output_text
    print("Response:", output_text)

    # Upload OpenAI response to S3
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    s3_bucket = os.getenv('S3_BUCKET_NAME')

    if not all([aws_access_key, aws_secret_key, aws_region, s3_bucket]):
        print("Error: AWS credentials not found in environment variables")
        return

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    # Create a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"openai_response_{timestamp}.txt"

    try:
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=filename,
            Body=output_text,
            ContentType='text/plain'
        )
        print(f"Successfully uploaded response to S3: s3://{s3_bucket}/{filename}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

if __name__ == "__main__":
    main()
