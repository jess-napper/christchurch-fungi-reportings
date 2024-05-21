# iNaturalist API Integration Project

## Overview
This project is an AWS Lambda function that integrates with the iNaturalist API to retrieve observation data for fungi species in the Christchurch, New Zealand region. The function provides two endpoints:

1. `/metadata`: Returns a CSV file containing metadata about the available observation data, such as the columns and their descriptions.
2. `/data`: Returns a CSV file containing the actual observation data for a specified date range.

## Prerequisites
- AWS Lambda function with Python 3.12 runtime
- AWS S3 bucket for storing metadata files and the Lambda function code

## Setup
1. Create an AWS Lambda function with the provided Python code (`fungi-function.py` or `fungi-function.zip`).
2. Set the required environment variables:
   - `API_KEY`: Your iNaturalist API key (used for authentication).
   - `BUCKET_NAME`: The name of your S3 bucket where metadata files will be stored.
3. Ensure that the Lambda function has the necessary permissions to access the S3 bucket.

### Creating the Lambda Function
To create the Lambda function, use the following AWS CLI command:

```bash
aws lambda create-function \
--function-name data472-jkn35-fungi-observations \
--runtime python3.12 \
--role arn:aws:iam::454456403374:role/DATA472-Lambda \
--handler lambda_function.lambda_handler \
--code S3Bucket=data472-jkn35-metadata-fungi-observations,S3Key=lambda/fungi-function.zip \
--description "" \
--timeout 60 \
--memory-size 1024 \
--tracing-config Mode=PassThrough \
--layers arn:aws:lambda:ap-southeast-2:336392948345:layer:AWSSDKPandas-Python312:8 \
--architectures x86_64 \
--ephemeral-storage Size=512
```

Note: Make sure to replace the function-name with the appropriate name, S3Bucket and S3Key with the corresponding names and `arn:aws:iam::454456403374:role/DATA472-Lambda` with the appropriate IAM role ARN for your Lambda function.

### Updating the Lambda Function Code
If you need to update the Lambda function code, follow these steps:

1. Modify the `fungi-function.py` file with your changes.
2. Create a new ZIP file containing the updated code:

   ```bash
   zip -r fungi-function.zip fungi-function.py
   ```

3. Upload the updated ZIP file to your S3 bucket:

   ```bash
   aws s3 cp fungi-function.zip s3://data472-jkn35-metadata-fungi-observations/lambda/
   ```

4. Update the Lambda function code with the new ZIP file from S3:

   ```bash
   aws lambda update-function-code --function-name data472-jkn35-fungi-observations --s3-bucket data472-jkn35-metadata-fungi-observations --s3-key lambda/fungi-function.zip
   ```

   Note: Make sure to have the necessary AWS credentials and permissions to perform these operations.

## Usage
### Metadata Endpoint
To retrieve the metadata CSV file, make a GET request to the `/metadata` endpoint with the following optional query parameter:

- `metadata_version`: The version of the metadata to retrieve (e.g., `1.0.0`). If not provided, the latest available version will be returned.

Example: `/metadata?api_key=*****&metadata_version=1.0.0` 
NB: replace api_key value with correct key.

### Data Endpoint
To retrieve the observation data CSV file, make a GET request to the `/data` endpoint with the following optional query parameters:

- `start_date`: The start date for the observation data range (format: `YYYY-MM-DD`).
- `end_date`: The end date for the observation data range (format: `YYYY-MM-DD`).

If no date range is provided, the function will return data for the past 30 days.

Example: `/data?api_key=*****&start_date=2023-05-01&end_date=2023-05-15`
NB: replace api_key value with correct key.

## Testing
The `api-test-calls` folder contains JSON files that can be used to test the Lambda function with different configurations. These files can be used as input payloads for invoking the Lambda function.

For example, to test the Lambda function with the `input_startNoEndDates_validAPIKey.json` file, you can use the following AWS CLI command:

```bash
aws lambda invoke --function-name data472-jkn35-fungi-observations --payload file://api-test-calls/input_startNoEndDates_validAPIKey.json output.txt
```

This command will invoke the Lambda function with the provided payload and store the output in the `output.txt` file.

## Implementation Details
### Metadata Endpoint
1. The function checks for the presence of the `metadata_version` query parameter.
2. If the `metadata_version` is not provided or is set to `LATEST`, the function retrieves the latest metadata file from the S3 bucket.
3. If a specific `metadata_version` is provided, the function retrieves the corresponding metadata file from the S3 bucket.
4. The metadata file is read into a Pandas DataFrame and returned as a CSV file in the response.

### Data Endpoint
1. The function checks for the presence of the `start_date` and `end_date` query parameters.
2. If the date parameters are valid, the function constructs the API request parameters for the iNaturalist API.
3. The function sends a request to the iNaturalist API to retrieve observation data for fungi species in the Christchurch, New Zealand region within the specified date range.
4. The response data from the API is processed and converted into a Pandas DataFrame.
5. The DataFrame is returned as a CSV file in the response.

## Metadata
The metadata CSV file contains information about the columns in the observation data CSV file. Each row in the metadata file represents a column, and the columns in the metadata file are:

- `column_name`: The name of the column in the observation data.
- `description`: A brief description of the column's content.
- `data_type`: The data type of the column (e.g., string, integer, float).
- `example`: An example value for the column.

Note: The metadata file is versioned, and the latest version is stored in the S3 bucket with a name like `metadata_v1-0-0.csv`. When a new version of the metadata is available, it will be stored with an incremented version number (e.g., `metadata_v1-0-1.csv`).

## Observation Data
The observation data CSV file contains the following columns:

- `id`: The unique identifier for the observation.
- `observed_on`: The date when the observation was made (format: `YYYY-MM-DD`).
- `latitude`: The latitude coordinate of the observation location.
- `longitude`: The longitude coordinate of the observation location.
- `user_login`: The username of the user who submitted the observation.
- `created_at`: The date and time when the observation was created (format: `YYYY-MM-DDTHH:MM:SSZ`).
- `name`: The scientific name of the observed species.
- `preferred_common_name`: The preferred common name of the observed species (if available).
- `native`: Indicates whether the observed species is native to the region or not.
- `photo_url`: The URL of a photo associated with the observation (if available).

## Error Handling
The Lambda function includes error handling for various scenarios:

- If an invalid API key is provided, a 401 Unauthorized response is returned.
- If an invalid endpoint is requested, a 400 Bad Request response is returned.
- If the date parameters are in an invalid format or the end date is before the start date, a 400 Bad Request response is returned.
- If an error occurs while retrieving data from the S3 bucket or the iNaturalist API, a 500 Internal Server Error response is returned with the error message.

## Future Improvements
- Provide static address to host lambda with API Gateway or similar.
- Enhance error handling and logging for better monitoring and debugging.
- Implement automated deployment and testing processes.
