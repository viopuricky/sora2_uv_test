import os
import time
from datetime import datetime
from dotenv import load_dotenv
import boto3
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


def generate_sora_video(client, s3_client, s3_bucket, prompt, duration=8, resolution="1280x720"):
    """
    Generate a video using OpenAI's Sora 2 model and upload to S3.

    Args:
        client: OpenAI client instance
        s3_client: boto3 S3 client instance
        s3_bucket: S3 bucket name
        prompt: User's text prompt for video generation
        duration: Video duration in seconds (4, 8, or 12)
        resolution: Video resolution (720x1280, 1280x720, 1024x1792, 1792x1024)

    Returns:
        S3 path of uploaded video or None if failed
    """
    print(f"\nStarting video generation with prompt: {prompt}")

    try:
        # Start video generation
        video = client.videos.create(
            model="sora-2",
            prompt=prompt,
            duration=duration,
            resolution=resolution
        )
        print(f"Video job created with ID: {video.id}")

        # Poll for completion
        while video.status not in ["completed", "failed"]:
            print(f"Status: {video.status}... waiting")
            time.sleep(10)
            video = client.videos.retrieve(video.id)

        if video.status == "failed":
            print(f"Video generation failed: {video.error}")
            return None

        print("Video generation completed! Downloading...")

        # Download the video
        video_content = client.videos.download(video.id)

        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sora_video_{timestamp}.mp4"

        # Upload to S3
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=filename,
            Body=video_content,
            ContentType='video/mp4'
        )

        s3_path = f"s3://{s3_bucket}/{filename}"
        print(f"Successfully uploaded video to S3: {s3_path}")
        return s3_path

    except Exception as e:
        print(f"Error generating video: {e}")
        return None


def main():
    print("Hello from sora2-uv-test!")
    
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_FREE_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return

    # Get AWS credentials
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


    client = OpenAI(api_key=api_key)
    num_of_task = 3

    # Assign tasks to the OpenAI and upload results to S3
    for i in range(1, 1 + num_of_task):
        print(f"\nGenerating joke {i}...")
        
        response = client.responses.create(             # test with text response only
            model="gpt-5-nano",
            input="tell me a joke about computers",
            store=True,
        )

        # Get response from OpenAI
        output_text = response.output_text
        print(f"Joke {i}: {output_text}")

        # Create a unique filename with timestamp and joke number
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"openai_joke_{i}_{timestamp}.txt"

        try:
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=filename,
                Body=output_text,
                ContentType='text/plain'
            )
            print(f"Successfully uploaded joke {i} to S3: s3://{s3_bucket}/{filename}")
        except Exception as e:
            print(f"Error uploading joke {i} to S3: {e}")

    # Generate a Sora video
    # user_prompt = "A cat riding a skateboard through a neon-lit city at night"
    # generate_sora_video(client, s3_client, s3_bucket, user_prompt)

if __name__ == "__main__":
    main()
