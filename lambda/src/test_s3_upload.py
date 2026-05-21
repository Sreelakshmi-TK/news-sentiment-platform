import json
import boto3
from datetime import datetime

s3_client = boto3.client("s3", region_name="ap-south-1")

bucket_name = "news-platform-raw-json-ap-south-1"

sample_data = {
    "status": "test",
    "message": "S3 upload successful"
}

current_time = datetime.utcnow()

file_key = (
    f"{current_time.year}/"
    f"{current_time.month:02d}/"
    f"{current_time.day:02d}/"
    f"news_{current_time.strftime('%H_%M_%S')}.json"
)

json_content = json.dumps(sample_data)

s3_client.put_object(
    Bucket=bucket_name,
    Key=file_key,
    Body=json_content,
    ContentType="application/json"
)

print(f"Uploaded successfully to: {file_key}")