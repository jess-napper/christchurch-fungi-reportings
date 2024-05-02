from datetime import datetime, timedelta
import json
import requests
import pandas as pd

def lambda_handler(event, context):
    # Parse query parameters from the event
    query_params = event.get('queryStringParameters', {})
    
    # Check for API key
    api_key = query_params.get('api_key')
    if api_key != "your_api_key":
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized. Invalid API key."})
        }
    
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
                "Content-Disposition": f"attachment; filename=inaturalist_observations.csv"
            },
            "body": csv_data,
            "metadata_version": "1.0.0"  # Metadata version information here
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
