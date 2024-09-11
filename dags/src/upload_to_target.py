import logging
import os
import json
from datetime import datetime
import time
import boto3
from src import pull_source

from airflow.models import Variable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# S3 configurations
AWS_ACCESS_KEY_ID = Variable.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = Variable.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = Variable.get("AWS_REGION")

# Initialize S3 client
logger.info("Initializing S3 client.")
s3_client = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def process_and_upload_to_s3(data, target):

    logger.debug("Processing message: %s", data)

    timestamp_epoch = data.get('time_last_update_unix', None)
    
    if timestamp_epoch:
        # Convert epoch to datetime
        timestamp = datetime.fromtimestamp(timestamp_epoch)

        # Create folder structure based on timestamp
        year = timestamp.strftime('%Y')
        month = str(int(timestamp.strftime('%m')))  # Removing leading zeros
        day = str(int(timestamp.strftime('%d')))  # Removing leading zeros
        hour = timestamp.strftime('%H')
        minute = timestamp.strftime('%M')
        second = timestamp.strftime('%S')

        # Create folder path
        folder_path = f"{year}/{month}/{day}"

        # Create file name (e.g., 01.json)
        file_name = f"currancy_rate_{year}-{month}-{day}-{hour}-{minute}-{second}.json"

        # Full S3 path
        s3_path = os.path.join(folder_path, file_name)

        try:
            body = {
                'base_code': data.get('base_code', 'USD'), 
                'rates': data.get('rates', {}), 
                'data_load_datetime_epoch': data.get('time_last_update_unix', None)}
            
            # Uploading data to S3
            s3_client.put_object(
                Bucket=target,
                Key=s3_path,
                Body=json.dumps(body)  # Assuming you're storing the message as JSON
            )
            logger.info(f"Uploaded to S3: {s3_path}")
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
    else:
        logger.warning("Timestamp not found in message.")

def consume(**kwrgs):
        url = kwrgs['url']
        target = kwrgs['S3_BUCKET_NAME']
        data = pull_source.pull_source(url)
        
        process_and_upload_to_s3(data, target)

if __name__ == "__main__":
    try:
        # time.sleep(60)
        consume()
    except Exception as e:
        logger.error(f"An error occurred in the consumer: {e}")
