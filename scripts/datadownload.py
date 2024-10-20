import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO

S3_BUCKET_URL = "https://vcthackathon-data.s3.us-west-2.amazonaws.com"

# (game-changers, vct-international, vct-challengers)
LEAGUE = "vct-challengers"

# (2022, 2023, 2024)
YEAR = 2024

def sanitize_filename(file_name):
    """Sanitize file names to replace restricted characters for local saving."""
    return file_name.replace(":", "_")


def download_gzip_and_write_to_json(file_name):
    remote_file = f"{S3_BUCKET_URL}/{file_name}.json.gz"
    response = requests.get(remote_file, stream=True)

    if response.status_code == 200:
        sanitized_file_name = sanitize_filename(file_name)
        if os.path.isfile(f"{sanitized_file_name}.json"):
            return False
        
        gzip_bytes = BytesIO(response.content)
        with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
            with open(f"{sanitized_file_name}.json", 'wb') as output_file:
                shutil.copyfileobj(gzipped_file, output_file)
        return True
    elif response.status_code == 404:
        # Ignore
        return False
    else:
        print(response)
        print(f"Failed to download {file_name}")
        return False


def download_esports_files():
    directory = f"{LEAGUE}/esports-data"

    if not os.path.exists(directory):
        os.makedirs(directory)

    esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]
    for file_name in esports_data_files:
        download_gzip_and_write_to_json(f"{directory}/{file_name}")


def download_games():
    start_time = time.time()

    local_mapping_file = f"{LEAGUE}/esports-data/mapping_data.json"
    with open(local_mapping_file, "r") as json_file:
        mappings_data = json.load(json_file)

    local_directory = f"{LEAGUE}/games/{YEAR}"
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    total_games = len(mappings_data)
    game_counter = 0

    for esports_game in mappings_data:
        s3_game_file = f"{LEAGUE}/games/{YEAR}/{esports_game['platformGameId']}"
        
        # Call the function to download and save the file
        response = download_gzip_and_write_to_json(s3_game_file)
        
        if response == True:
            game_counter += 1
            if game_counter % 10 == 0:
                elapsed_time = round(time.time() - start_time) / 60
                print(f"Downloaded {game_counter} games in {elapsed_time} minutes")
            
            # Calculate and print progress percentage
            progress_percentage = (game_counter / total_games) * 100
            print(f"[{progress_percentage:.2f}%] {game_counter}/{total_games} files downloaded.")

if __name__ == "__main__":
    download_esports_files()
    download_games()