from datetime import datetime, timedelta
import json
import requests
import pandas as pd
import boto3
import re

def lambda_handler(event, context):
    # Parse query parameters from the event
    query_params = event.get('queryStringParameters', {})
    endpoint = event.get('requestContext', {}).get("path") # returns the endpoint path
    
    # Check for API key
    api_key = query_params.get('api_key', "")
    if api_key != "Fish_Sea_Hat_Forest!":
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorised. Invalid API key."})
        }
    
    if endpoint == '/metadata':
        # Return data from iNaturalist
        return get_metadata_table(query_params)
    
    elif endpoint == '/data':
        # Return metadata table
        return get_observation_data(query_params)
    else:
        # Handle if the endpoint is not recognized
        response = {
            'statusCode': 400,
            'body': 'Invalid endpoint'
        }
    # return {'statusCode': 400, 'body': endpoint}
    

# def get_metadata_table(query_params):
#     # Parse start_date and end_date from query parameters
#     metadata_version = query_params.get('metadata_version', '')
#     if metadata_version == "":
#         metadata_version = "LATEST"  # get latest metadata version if none is given
    
#     # Link to S3 to pull metadata from there
#     # temp solution
#     # metadata = get_metadata_table(metadata_version)

#     return {
#         "statusCode": 200,
#         "body": json.dumps("metadata to come")
#     }


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
    bucket_name = 'data472-jkn35-metadata-fungi-observations'
    prefix = 'metadata/metadata_v'  # Metadata is stored with names like "metadata_v1-0-0.csv"


    if metadata_version == 'LATEST':
        # List objects in the metadata folder
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        # Extract version numbers from object keys
        versions = [re.findall(r'metadata_v(\d+-\d+-\d+)', obj['Key'])[0] for obj in response.get('Contents', [])]
        
        # Find the latest version
        latest_version = max(versions)
        
       # Construct key for the latest metadata file
        key = f'{prefix}{latest_version}.csv'

    else:
        key = f'{prefix}{metadata_version}.csv'  # Assuming metadata is stored in CSV format
    
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        metadata_df = pd.read_csv(response['Body'])

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    # Convert DataFrame to CSV string
    csv_data = metadata_df.to_csv(index=False)
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/csv",
            "Content-Disposition": f"attachment; filename=metadata.csv"
        },
        "body": csv_data
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
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid date format. Please use YYYY-MM-DD."})
            }
        
        if end_date <= start_date:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "End date must be after start date."})
            }
        
    elif (start_date_str and not end_date_str) or (end_date_str and not start_date_str):
        # If only one date is given, state that both are required.
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
    
    # Make request to iNaturalist API
    response = requests.get("https://api.inaturalist.org/v1/observations", params=params)
    
    # Process response data
    if response.status_code == 200:
        data = response.json().get('results', [])
        df = process_data(data)
        
        # Convert DataFrame to CSV
        csv_data = df.to_csv(index=False)
        
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
    else:
        response_body = {
            "statusCode": response.status_code,
            "body": response.text
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