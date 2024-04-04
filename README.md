# iNaturalist Fungi Observations Data Project

This project retrieves and processes fungi observation data from the iNaturalist API for Christchurch, New Zealand, within a specified date range. The retrieved data is filtered, cleaned, and stored in a CSV file for further analysis and integration.

## Project Structure

- `inaturalist_data_retrieval.py`: Python script to retrieve and process observation data from the iNaturalist API.
- `inaturalist_observations.csv`: CSV file containing the retrieved and processed observation data.
- `data_contract.md`: Data contract defining the structure and format of the observation data.

## Data Format

The observation data retrieved from the iNaturalist API adheres to the following structure:

- `id`: Unique identifier for the observation (integer).
- `species_guess`: Species guess provided by the observer (string).
- `observed_on`: Date of the observation (ISO 8601 format, e.g., "2024-03-30").
- `place_guess`: Location where the observation was made (string).
- `latitude`: Latitude coordinate of the observation (float).
- `longitude`: Longitude coordinate of the observation (float).
- `user_login`: Login username of the observer (string).
- `created_at`: Timestamp when the observation was created (ISO 8601 format, e.g., "2024-03-30T10:30:00Z").

## Usage

1. Install the required dependencies: `pandas` and `requests`.
2. Update the `start_date` and `end_date` variables in the `inaturalist_data_retrieval.py` script to specify the desired observation date range.
3. Run the `inaturalist_data_retrieval.py` script to retrieve and process the observation data.
4. The retrieved data will be saved in the `inaturalist_observations.csv` file.

## Next Steps

- Explore and analyze the retrieved observation data.
- Integrate the data into a suitable database system (e.g., Amazon RDS with PostgreSQL).
- Develop an API based on the SDMX protocol to serve the data.
- Containerize the application using Docker.
- Set up a CI/CD pipeline for automated testing and deployment.
- Implement monitoring and maintenance processes.