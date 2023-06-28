# Spotify API Data Retrieval and MySQL Database Insertion 

 This python script will demonstrate how to  use the Spotify API to search for an artist, retrieve their top tracks amd insert the following track data into MySQL database: album, duration_ms, explicit, track_number, popularity, name, artists, liveness, loudness, tempo, time_signature, energy, danceability, song_id. 

 The script uses 'dotenv' library to load the environment variables from a '.env' file, which will contain your Spotify API client ID and client secret. This can be attained from 'spotify for developers account.' 

## Prerequisites
Before installing the script, make sure you have the followinng:
 - Python 3 installed on your machine 
 - MySQL server installed and running 
 - Spotify API credentials (client ID and client secret). This can be obtained by creatinng a spotify Developer account and creating a application. 
 - 'mysql-connector-python' Python package. To get this, type the following command into the terminal: 'pip install mysql-connector-python'. (If 'pip' does not work then use pip3). I used pip3 for this command. 
    
## Setup
 1. Create a '.env' file in your project directory and add your Spotify API credentials gennerated from you spotify for developers app.

        CLIENT_ID=your_client_id
        CLIENT_SECRET=your_client_secret

 2. On the terminal, write the code 'pip3 install python-dotenv'. This will allow us to load our environment variables file. 

 3. After the enviroment variables have been loaded, we need to install the request module. To do this, on your terminal type: pip3 install requests. 

 4. Lets create a MySQL client (e.g MySQL Workbench, phpMyAdmin) and create a new datdabse 'SPOTIFY_SERVICES'. You can give it any name that suits your project. 

## Writing the Code
 1. The important modules have to be installed as it will be used later in our code. The modules to be installed are: 'dotenv', 'os', 'base64', 'requests', 'json', and 'mysql.connector'. 

        from dotenv import load_dotenv
        import os
        import base64
        from requests import post, get
        import json
        import mysql.connector

 2. The 'load_dotenv()' funtion is used to load the Spotify API client ID and client secret from the .env file we created earlier. 
    
 3. The 'get_token()' funtion is retrieving the access token from the spotify API using client credentials flow. So it is exchanging our client ID and client secret credentials for an access token. Our client ID and client secret are encoded with base64 and sent in the headers of a POST request to the token endpoint. 

        def get_token():
            auth_string = client_id + ":" + client_secret
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

 4. The 'get_auth_header(token)' returns the authorization header with the access token:

        def get_auth_header(token):
            return  {"Authorization": "Bearer " + token}

 5. The 'search_for_artist(token, artist)' function will search for  an artist using the spotify API. The artist name will be passed as a query parameter, and the function returns the first matching artist from the search result.

        def search_for_artist(token, artist_name):
            url = "https://api.spotify.com/v1/search"
            headers = get_auth_header(token)
            query = f"?q={artist_name}&type=artist,track&limit=1"

 6. The 'get_songs_by_artist(token, artist_id)' function extracts the toptracks of the artist by using the Spotify API. The artist ID is passed as a path parameter in the API endpoint URL. 

        def get_songs_by_artist(token, artist_id):
            url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
            headers = get_auth_header(token)
            result = get(url, headers=headers)
            json_result = json.loads(result.content) ["tracks"] 
    
 The function also uses 'get_audio_features()'function to achive additional audio features for each track. 

        for track in json_result:
            # Retrieve the additional keys
            audio_features = get_audio_features(token, track["id"])
            track.update(audio_features)

        return json_result

 Then the 'get_audio_features_(token, song_id)' function extracts the audio features of a song usimg the Spotify API. The song ID is passed as a path parameter in the API endpoint URL. 

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
 Then the access token searches for an artist, retrieves their top tracks and prints detailed information about every single track as well as the artist involed. the code to achive this is: 

        token = get_token()
        result = search_for_artist(token, "BEYONCE")
        artist_id = result["id"]
        songs = get_songs_by_artist(token, artist_id)

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

 7. The script iterates over the songs that have been retrived and inserts them into the 'songs' table in the MySQL database. The 'cursor.execute()' method as shown below is used to execute the SQL query with the song data: 

        def connect_to_mysql():
            try:
            # Connect to the MySQL database
                db = mysql.connector.connect(
                    host="localhost",  # Replace with your Docker container's IP or hostname
                    port=3306,  # Replace with the mapped port if different from 3306
                    user="root",  # Replace with your MySQL username
                    password="root",  # Replace with the MySQL password
                    database="SPOTIFY_SERVICES"  # Replace with your MySQL database name
                )

                print("Connected to the MySQL database!")
                return db
            except mysql.connector.Error as error:
                print("Failed to connect to MySQL database:", error)
            return None

### Limitations and Future Enhancements
 This code currently inserts our data in the MySQL database but it can also be modified to work with other databases by changing the connection and insertion mode. 
    
    


