from datetime import datetime, timedelta
import json
import requests
import pandas as pd
import boto3
import re
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

log_file = '/tmp/execution_log.log'  # Temporary file in the Lambda environment
file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def lambda_handler(event, context):
    logger.info("Lambda function started")
    try:
        # Parse query parameters from the event
        query_params = event.get('queryStringParameters', {})
        endpoint = event.get('requestContext', {}).get("path")  # returns the endpoint path
        
        # Check for API key
        api_key = query_params.get('api_key', "")
        if api_key != os.environ.get('API_KEY'):
            logger.warning("Unauthorized access attempt with invalid API key")
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorised. Invalid API key."})
            }
        
        if endpoint == '/metadata':
            logger.info("Endpoint '/metadata' accessed")
            # Return data from iNaturalist
            response = get_metadata_table(query_params)
        
        elif endpoint == '/data':
            logger.info("Endpoint '/data' accessed")
            # Return metadata table
            response = get_observation_data(query_params)
        
        else:
            logger.error("Invalid endpoint accessed")
            response = {
                'statusCode': 400,
                'body': 'Invalid endpoint'
            }
        
        logger.info("Lambda function executed successfully")
        return response

    except Exception as e:
        logger.exception("Exception occurred during Lambda execution")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    finally:
        upload_log_to_s3()

def transform_version(version):
    # Transform version from v1.0.0 to 1-0-0
    return version[1:].replace('.', '-')

def get_metadata_table(query_params):
    # Parse metadata_version from query parameters
    metadata_version = query_params.get('metadata_version', 'LATEST')

    if metadata_version != 'LATEST':
        metadata_version = transform_version(metadata_version)
    
    # Retrieve metadata from S3 based on the specified version
    s3 = boto3.client('s3')
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    prefix = 'metadata/metadata_v'  # Metadata is stored with names like "metadata_v1-0-0.json"

    if metadata_version == 'LATEST':
        # List objects in the metadata folder
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        # Extract version numbers from object keys
        versions = [re.findall(r'metadata_v(\d+-\d+-\d+)', obj['Key'])[0] for obj in response.get('Contents', []) if 'Key' in obj]
        
        # Find the latest version
        latest_version = max(versions)
        
        # Construct key for the latest metadata file
        key = f'{prefix}{latest_version}.json'

    else:
        key = f'{prefix}{metadata_version}.json'
    
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        metadata_json = json.loads(response['Body'].read())
        logger.info("Metadata retrieved successfully")
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    # Convert metadata JSON to string
    metadata_str = json.dumps(metadata_json, indent=4)
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Content-Disposition": f"attachment; filename=metadata.json"
        },
        "body": metadata_str
    }


def get_observation_data(query_params):
    
    # Parse start_date and end_date from query parameters
    start_date_str = query_params.get('start_date', '')
    end_date_str = query_params.get('end_date', '')
    
    # Convert query parameters to datetime objects and validate
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        except ValueError:
            logger.error("Invalid date format")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid date format. Please use YYYY-MM-DD."})
            }
        
        if end_date <= start_date:
            logger.error("End date must be after start date")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "End date must be after start date."})
            }
        
    elif (start_date_str and not end_date_str) or (end_date_str and not start_date_str):
        # If only one date is given, state that both are required.
        logger.error("Both start date and end date must be provided")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "End date and start date must both be given."})
        }

    else:
        # If no dates are provided, use default values (e.g., past 30 days)
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
    
    # Construct params for iNaturalist API

    params = {
        "place_id": 40469,  # Christchurch, New Zealand place ID
        "iconic_taxa": "Fungi",
        "order": "desc",
        "order_by": "created_at",
        "per_page": 200,  # Number of results per page (max is 200)
        "page": 1,  # Start from the first page
        "d1": start_date.isoformat(),
        "d2": end_date.isoformat(),
        "quality_grade": "research"  # Retrieve only verified observations
    }

    logger.info(f"API input parameters: {params}")
    
    observations = []  # List to store all observations
    
    # Continue making requests until all pages are fetched
    while True:
        # Make request to iNaturalist API
        response = requests.get("https://api.inaturalist.org/v1/observations", params=params)
        
        # Process  response data
        if response.status_code == 200:
            data = response.json().get('results', [])
            observations.extend(data)  # Add observations from current page
            
            # Check if there is more than one page
            if response.json().get('total_results', 0) > len(observations):
                params['page'] += 1  # Move to the next page
            else:
                break  # No more pages, break the loop
        
        else:
            logger.error(f"Error retrieving observation data: {response.status_code}")
            return {
                "statusCode": response.status_code,
                "body": response.text
            }
    
    df = process_data(observations)
    
    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False)
    logger.info(f"Observation data retrieved successfully. Number of observations: {len(observations)}")
    
    # Prepare response
    response_body = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/csv",
            "Content-Disposition": f"attachment; filename=inaturalist_observations.csv",
            "metadata_version": "1.0.0",  # Metadata version information here
        },
        "body": csv_data,
    }
    
    return response_body


def process_data(data):
    observations = []
    for obs in data:
        photo_url = ""
        if "photos" in obs and obs["photos"]:
            photo_url = obs["photos"][0]['url'].replace('square', 'medium')
        
        observation = {
            "id": obs["id"],
            "observed_on": obs.get("observed_on", ""),
            "latitude": obs.get("location", "").split(",")[0],
            "longitude": obs.get("location", "").split(",")[-1],
            "user_login": obs.get("user", {}).get("login", ""),
            "created_at": obs.get("created_at", ""),
            "name": obs.get("taxon", {}).get("name", ""),
            "preferred_common_name": obs.get("taxon", {}).get("preferred_common_name", "").title(),
            "native": obs.get("taxon", {}).get("native", ""),
            "photo_url": photo_url,
        }
        observations.append(observation)

    df = pd.DataFrame(observations)
    return df

def upload_log_to_s3():
    try:
        s3 = boto3.client('s3')
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        log_prefix = 'logs/execution_log.log'
        
        # Read existing log data from S3
        existing_log_data = ""
        try:
            obj = s3.get_object(Bucket=bucket_name, Key=log_prefix)
            existing_log_data = obj['Body'].read().decode('utf-8')
        except s3.exceptions.NoSuchKey:
            # If the log file doesn't exist yet, ignore the error
            pass
        
        # Append new log data to existing log data
        with open(log_file, 'r') as new_log_file:
            new_log_data = new_log_file.read()
        
        combined_log_data = existing_log_data + new_log_data
        
        # Upload combined log data to S3
        s3.put_object(Bucket=bucket_name, Key=log_prefix, Body=combined_log_data.encode('utf-8'))
        
        logger.info("Log file uploaded to S3 successfully")
    except Exception as e:
        logger.error(f"Error uploading log file to S3: {str(e)}")

