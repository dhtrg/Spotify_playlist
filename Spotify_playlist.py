def retrieve_data_with_authentication():
    """
    This function retrieve data on tracks in specified a playlist from Spotify API using the spotipy module
    The client credential for this API require clien_id and client_secret
    :return: a csv file that contains data on tracks in a specified playlist
    """
    #this is the link to the playlist that I will retrieve data
    playlist_link = 'https://open.spotify.com/playlist/6TY1by3xd2yDmwtZuKPKg1?si=493fcc3be21246ba'

    #set up and perform authentication with spotipy module
    #please substitute with your client_id and client_secret
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id='_______________',
                                                                                client_secret='______________'))

    #results = spotify.playlist_items(playlist_link, limit=100, offset=start)

    def retrieve_playlist(playlist_url, start):
        """
        this fuction retrieve data on track of a specified playlist and process the json data
        :param playlist_url: the URL to the Spotify playlist
        :param start: the index where I start retrieve data in the playlist. since I need to include pagination, this argument is necessary
        :return: a dataframe that contains data of tracks from index "start" up to index "start + 100"
        """
        # Create empty dataframe
        playlist_features_list = ["album_type", "artist", "album", "track_name", "track_id", "external_urls",
                                  "disc_number", "duration_ms", "episode", "explicit", "href", "is_local",
                                  "popularity", "preview_url", "type"]

        playlist_df = pd.DataFrame(columns=playlist_features_list)

        # Loop through every track in the playlist, extract features and append the features to the playlist_df
        playlist = spotify.playlist_items(playlist_url, limit=100, offset=start)['items']
        for track in playlist:
            # Create empty dict
            playlist_features = {}
            # Get metadata
            playlist_features["album_type"] = track["track"]["album"]["album_type"]
            playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
            playlist_features["album"] = track["track"]["album"]["name"]
            playlist_features["track_name"] = track["track"]["name"]
            playlist_features["track_id"] = track["track"]["id"]
            playlist_features["external_urls"] = track["track"]["external_urls"]["spotify"]

            for feature in playlist_features_list[6:]:
                playlist_features[feature] = track["track"][feature]

            #create a dataframe for each of the track
            track_df = pd.DataFrame(playlist_features, index=[0])
            # Concatenate the empty playlist_df with the data of each track in the track_df
            playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

        return playlist_df

    #create the initial dataframe to store data of the first 100 tracks
    df = retrieve_playlist(playlist_link, 0)

    #this variable represent the index where I start retrieve data in the playlist
    start = 0

    #this variable represent the number of songs that has been added to the dataframe
    count = len(retrieve_playlist(playlist_link, start))

    #this variable represent the total number of songs in the specified playlist
    total_tracks = spotify.playlist_items(playlist_link, limit=100, offset=start)['total']

    #Since I need to include pagination, I need to use while loop to get data of all the tracks in the playlist
    while count < total_tracks:
        #Since the limit to retrieve data is 100, I increase the starting index by 100 for retrieving next chunk of data
        start += 100
        #retrieving next chunk of data and put in a dataframe
        new_df = retrieve_playlist(playlist_link, start)
        #append the new dataframe to the initial dataframe
        df = df.append(new_df)
        count += len(retrieve_playlist(playlist_link, start))

    #drop the columns with at least 10% of missingness
    df = df.dropna(thresh=0.9, axis=1)
    # drop the duplicate columns by using .drop_duplicates() functions and transposing twice
    df = df.T.drop_duplicates().T

    #capitalize 'album_type' and 'type' so that the dataset is coherent
    df['album_type'] = df['album_type'].astype(str).str.title()
    df['type'] = df['type'].astype(str).str.title()

    #Fill null values with N/A (Not applicable)
    df.fillna('N/A', inplace=True)

    #create the csv file
    df.to_csv("spotify.csv", index=False)
if __name__ == '__main__':
    retrieve_data_with_authentication()