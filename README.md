# iNaturalist API Integration Project

## Important Note on AWS Deployment

Due to the University of Canterbury user restrictions on AWS, this Lambda application cannot run in a production environment and can only be tested within the Lambda test environment. 

I also attempted to deploy this application using AWS App Runner. However, similar permission errors were encountered, meaning it could not be deployed there either.

## Overview

This project is an AWS Lambda function. It integrates with the iNaturalist API to retrieve observation data for fungi species in the Christchurch, New Zealand region. The function provides two endpoints:

* /metadata: Returns a CSV file containing metadata about the available observation data, such as the columns and their descriptions.
* /data: Returns a CSV file containing the actual observation data for a specified date range.

## Prerequisites
- AWS Lambda function with Python 3.12 runtime
- AWS S3 bucket for storing metadata files and the Lambda function code

## Setup
1. Create an AWS Lambda function with the provided Python code (`fungi-function.py` and `requirements.txt`).
2. Set the required environment variables:
   - `API_KEY`: The API key to access this Lambda (not the iNaturalist API - that has no key).
   - `BUCKET_NAME`: The name of your S3 bucket where metadata files will be stored.
3. Ensure that the Lambda function has the necessary permissions to access the S3 bucket.

### Creating the Lambda Function
To create the Lambda function, use the following AWS CLI command:

```bash
aws lambda create-function \
--function-name **your-function-name** \
--runtime python3.12 \
--role **your-iam-role-arn** \
--handler lambda_function.lambda_handler \
--code S3Bucket=**your-s3-bucket**,S3Key=lambda/fungi-function.zip \
--description "" \
--timeout 60 \
--environment Variables="{API_KEY=**your_api_key** S3_BUCKET_NAME=**s3-bucket-name**}"
--memory-size 1024 \
--tracing-config Mode=PassThrough \
--layers arn:aws:lambda:ap-southeast-2:336392948345:layer:AWSSDKPandas-Python312:8 \
--architectures x86_64 \
--ephemeral-storage Size=512
```

Note: Make sure to replace the any fields marked with ** asterisks ** with the appropriate names.

### Updating the Lambda Function Code
If you need to update the Lambda function code, follow these steps:

1. Modify the `fungi-function.py` file with your changes.
2. Create a new ZIP file containing the updated code:

   ```bash
   zip -r fungi-function.zip fungi-function.py
   ```

3. Upload the updated ZIP file to your S3 bucket:

   ```bash
   aws s3 cp fungi-function.zip **your-s3bucket**/lambda/
   ```

4. Update the Lambda function code with the new ZIP file from S3:

   ```bash
   aws lambda update-function-code --function-name **your-func-name** --s3-bucket **your-bucket-name** --s3-key lambda/fungi-function.zip
   ```

   Note: Make sure to have the necessary AWS credentials and permissions to perform these operations and replace the fields with the correct names.

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
aws lambda invoke --function-name **your-func-name** --payload file://api-test-calls/input_startNoEndDates_validAPIKey.json output.txt
```

This command will invoke the Lambda function with the provided payload and store the output in an `output.txt` file.

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
The metadata JSON file contains detailed information about the columns in the observation data CSV file. The metadata is divided into three main sections: attributes, dimensions, and code lists.

- **Attributes**: Provide additional information about the observations, typically describing or identifying the observation in more detail.
- **Dimensions**: Categories used for analysis, providing context or structure for the data.
- **Code Lists**: Enumerations or predefined lists of values used for standardising data entries.

Each section contains the following fields:
- `name`: The name of the field.
- `description`: A brief description of the field's content.
- `type`: The data type of the field (e.g., Text, Date, Float).
- `code_values` (for code lists only): Predefined values for the field.

### Example Structure
The metadata file includes a dataset description, source URL, and version number:
```json
{
  "metadata": {
    "description": "This dataset contains observations from iNaturalist, including details such as the date and location of the observation, the user who made the observation, and the taxon observed.",
    "source_url": "https://www.inaturalist.org/",
    "version": "1.0",
    "attributes": [
      {
        "name": "id",
        "description": "Unique iNaturalist identifier for the observation",
        "type": "Text"
      },
      {
        "name": "user_login",
        "description": "Username of the user who made the observation on iNaturalist",
        "type": "Text"
      },
      ...
    ],
    "dimensions": [
      {
        "name": "observed_on",
        "description": "Date of the observation",
        "type": "Date"
      },
      ...
    ],
    "code_lists": [
      {
        "name": "native",
        "description": "Whether the observed taxon is native to the location",
        "type": "Boolean",
        "code_values": ["True", "False"]
      }
    ]
  }
}
```

### Versioning
The metadata file is versioned to track changes. The version number follows the format `vX-Y-Z`, where:
- `X` (major version): Incremented for changes to a dimension or major changes to the metadata.
- `Y` (minor version): Incremented for changes to an attribute.
- `Z` (patch version): Incremented for changes to a code list.

The latest version of the metadata file is stored in the S3 bucket with a name like `metadata_vX-Y-Z.json`. When a new version of the metadata is available, it will be stored with the appropriate incremented version number.

### Uploading a New Metadata File
To upload a new metadata file to the S3 bucket, you can use the following bash script:

```bash
#!/bin/bash

# Variables
BUCKET_URI=**your-s3-bucket-uri**
METADATA_FILE="metadata.json"
VERSION="vX-Y-Z" # Update this to the new version number

# Upload the metadata file
aws s3 cp $METADATA_FILE ${BUCKET_URI}metadata_${VERSION}.json

# Verify the upload
if [ $? -eq 0 ]; then
  echo "Metadata file uploaded successfully."
else
  echo "Error uploading metadata file."
fi
```

Make sure you have the AWS CLI installed and configured with the appropriate credentials and permissions to access the S3 bucket. Adjust the `VERSION` variable to reflect the new version number of your metadata file based on the changes made.


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

## Logging Configuration

The logging setup uses Python's logging library to establish a logger. A file handler is configured to write logs to a temporary file (/tmp/execution_log.log), a necessity for AWS Lambda which only permits writing to the /tmp directory.

### Logging Events and Errors

Throughout the function, key events and potential errors are logged using various log levels:

- **INFO:** Logs general information regarding the function's execution, such as start, endpoints accessed, and successful operations.
- **WARNING:** Records warnings, like unauthorised access attempts.
- **ERROR:** Captures error messages, including invalid inputs or failures to retrieve data.
- **EXCEPTION:** Documents stack traces in case of exceptions, facilitating detailed debugging.

### Storing Logs in S3

Upon completion of the function, the log file is uploaded to an S3 bucket. Logs are stored in the specified S3 bucket. This approach ensures each execution's logs are appended to the existing log file, maintaining a log history.


## Future Improvements
- Provide static address to host lambda function.
- Improve the error handling and logging for better monitoring and debugging.
- Implement automated deployment and testing.
