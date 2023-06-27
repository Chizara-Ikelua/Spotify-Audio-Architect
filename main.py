from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import mysql.connector


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return  {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist,track&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content) ["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

    tracks = json_result["tracks"]["items"]
    for track in tracks:
            album = track["album"]["name"]
            duration_ms = track["duration_ms"]
            explicit = track["explicit"]
            track_number = track["track_number"]
            popularity = track["popularity"]
            name = track["name"]
            song_id = track["id"]
            artists = ", ".join([artist["name"] for artist in track["artists"]])
            liveness = track.get("liveness", "Not available")
            loudness = track.get("loudness", "Not available")
            tempo = track.get("tempo", "Not available")
            time_signature = track.get("time_signature", "Not available")
            energy = track.get("energy", "Not available")
            danceability = track.get("danceability", "Not available")
            

            print("Album:", album)
            print("Duration (ms):", duration_ms)
            print("Explicit:", explicit)
            print("Track Number:", track_number)
            print("Popularity:", popularity)
            print("Name:", name)
            print("ID:", song_id)
            print("Artists:", artists)
            print("Liveness:", liveness)
            print("Loudness:", loudness)
            print("Tempo:", tempo)
            print("Time Signature:", time_signature)
            print("Energy:", energyi)
            print("Danceability:", danceability)
            print()
    

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content) ["tracks"]

    # Iterate over the tracks and include additional keys
    for track in json_result:
        # Retrieve the additional keys
        audio_features = get_audio_features(token, track["id"])
        track.update(audio_features)

    return json_result

def get_audio_features(token, song_id):
    url = f"https://api.spotify.com/v1/audio-features/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return {
        "liveness": json_result.get("liveness", "Not available"),
        "loudness": json_result.get("loudness", "Not available"),
        "tempo": json_result.get("tempo", "Not available"),
        "time_signature": json_result.get("time_signature", "Not available"),
        "energy": json_result.get("energy", "Not available"),
        "danceability": json_result.get("danceability", "Not available")
    }


token = get_token()
result = search_for_artist(token, "BEYONCE")
artist_id = result["id"]
songs = get_songs_by_artist(token, artist_id)

# for idx, song in enumerate(songs):
    # print(f"{idx + 1}. {song['name']}")

for idx, song in enumerate(songs):
    print(f"{idx + 1}. {song['name']}")
    print("Album:", song['album']['name'])
    print("Duration (ms):", song['duration_ms'])
    print("Explicit:", song['explicit'])
    print("Track Number:", song['track_number'])
    print("Popularity:", song['popularity'])
    print("ID:", song['id'])
    print("Artists:", ", ".join([artist['name'] for artist in song['artists']]))
    print("liveness:", song['liveness'])
    print("Loudness:", song['loudness'])
    print("Tempo:", song['tempo'])
    print("Time Signature:", song['time_signature'])
    print("Energy:", song['energy'])
    print("Danceability:", song['danceability'])
    print()
    

    if 'artists' in song:
        artists = song['artists']
        artist_names = [artist['name'] for artist in artists]
        print("Artists:", ", ".join(artist_names))
    else:
        print("Artists: Not available")
    
def connect_to_mysql():
    try:
    # Connect to the MySQL database
        db = mysql.connector.connect(
            host="localhost",  # Replace with your Docker container's IP or hostname
            port=3306,  # Replace with the mapped port if different from 3306
            user="root",  # Replace with the MySQL username
            password="root",  # Replace with the MySQL password
            database="SPOTIFY_SERVICES"  # Replace with the MySQL database name
        )

        print("Connected to the MySQL database!")
        return db
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL database:", error)
    return None


db = connect_to_mysql()
if db:
    cursor = db.cursor()

    # Iterate over the songs and insert them into the database
    for song in songs:
        album = song['album']['name']
        duration_ms = song['duration_ms']
        explicit = song['explicit']
        track_number = song['track_number']
        popularity = song['popularity']
        name = song['name']
        song_id = song['id']
        artists = [artist['name'] for artist in song['artists']]
        liveness = song['liveness']
        loudness = song['loudness']
        tempo = song['tempo']
        time_signature = song['time_signature']
        energy = song['energy']
        danceability = song['danceability']

        # Execute SQL query to insert the song into the database
        query = """
        INSERT INTO songs (album, duration_ms, explicit, track_number, popularity, name, artists, liveness, loudness, tempo, time_signature, energy, danceability, song_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
        album, duration_ms, explicit, track_number, popularity, name, ", ".join(artists), liveness, loudness, tempo, time_signature, energy, danceability, song_id
                )
        
    cursor.execute(query, values)
    

     # Commit the changes and close the cursor and database connection
    db.commit()
    cursor.close()
    db.close()