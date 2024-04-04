import requests
import time
import pandas as pd
from datetime import datetime, timedelta

base_url = "https://api.inaturalist.org/v1"
endpoint = "/observations"

end_date = datetime.now().date()
start_date = end_date - timedelta(days=5*365)
print('start date:', start_date)
print('end date:', end_date)

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

headers = {}

def make_request(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    print(f"API Response Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"API Response Data: {data}")
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def process_data(data):
    observations = []
    for obs in data:
        observation = {
            "id": obs["id"],
            "species_guess": obs.get("species_guess", ""),
            "observed_on": obs.get("observed_on", ""),
            "place_guess": obs.get("place_guess", ""),
            "latitude": obs.get("location", "").split(",")[0],
            "longitude": obs.get("location", "").split(",")[-1],
            "user_login": obs.get("user", {}).get("login", ""),
            "created_at": obs.get("created_at", "")
        }
        observations.append(observation)
    
    df = pd.DataFrame(observations)
    return df

def get_all_data():
    all_data = []
    while True:
        url = base_url + endpoint
        data = make_request(url, params, headers)
        
        if data:
            all_data.extend(data["results"])
            print(f"Retrieved {len(data['results'])} observations")
            
            if data["total_results"] <= params["per_page"] * params["page"]:
                break
            
            params["page"] += 1
            time.sleep(1)
        else:
            break
    
    return all_data

def main():
    all_data = get_all_data()
    print(f"Total observations retrieved: {len(all_data)}")
    
    df = process_data(all_data)
    print("DataFrame:")
    print(df.head())

    df.to_csv("inaturalist_observations.csv", index=False)

if __name__ == "__main__":
    main()