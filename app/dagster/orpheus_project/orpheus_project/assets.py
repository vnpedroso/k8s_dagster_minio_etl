

import os
import pandas as pd
from dagster import (
	asset,
	Output,
    RetryPolicy,
	FreshnessPolicy,
    file_relative_path
)
from datetime import datetime, timezone
from io import BytesIO



# Retry policy with delay in seconds
retry_policy = RetryPolicy(max_retries=2,delay=30)
# Source freshness determined from the latest run
freshness_policy = FreshnessPolicy(maximum_lag_minutes=180)

#decorator that defines a software defined asset function
@asset(
    group_name='orpheus_pipeline',
    retry_policy=retry_policy,
	freshness_policy=freshness_policy,
	required_resource_keys={"get_conn_recent_history"} #resource key required for this asset
)
def api_conn_recent_history_scope(context) -> Output: 
    '''
    return the connection object with the access scope to get the recent songs of the user
    '''
    spotify_conn = context.resources.get_conn_recent_history
    spotipy_conn_obj = spotify_conn.current_user_recently_played(
        limit=50,
        after=None,
        before=None
    )
    #standard output object through which function's "returns" and metadata can be returned
    return Output(spotipy_conn_obj)

@asset(
	group_name='orpheus_pipeline',
	retry_policy=retry_policy,
	freshness_policy=freshness_policy
)
def extract_most_recent_50_songs(context,api_conn_recent_history_scope) -> Output[list]:
    '''
    return a list with the last 50 songs listenend by the user 
    '''
    extract_list = []
    for i in api_conn_recent_history_scope['items']:
        track = i['track']
        extract_list.append(
            (
                track['id'],
                track['name'],
                track['artists'][0]['id'],
                track['artists'][0]['name'],
                track['album']['id'],
                track['album']['name']
            )
        )

    #the context object allow us to manifest information in the logs every run:
    context.log.info(f'''
            the top item of our list: 

            song_id: {extract_list[0][0]}
            song: {extract_list[0][1]}
            artist_id: {extract_list[0][2]}
            artist: {extract_list[0][3]}
            album_id: {extract_list[0][4]}
            album: {extract_list[0][5]}
        ''')
    return Output(extract_list)

@asset(
    group_name='orpheus_pipeline',
    retry_policy=retry_policy,
	freshness_policy=freshness_policy
)
def transform_song_list_to_df(context,extract_most_recent_50_songs) -> Output[pd.DataFrame]:
    '''
    transforming the extract list of tuples into a dataFrame
    '''
    datapoints = extract_most_recent_50_songs
    columns = ['song_id','song','artist_id','artist','album_id','album']
    df = pd.DataFrame(datapoints,columns=columns)

    context.log.info(df.head(5))
    return Output(df)

@asset(
    group_name='orpheus_pipeline',
    retry_policy=retry_policy,
    freshness_policy=freshness_policy
)
def load_csv_local_dest(context,transform_song_list_to_df) -> None:
    '''
    writing the dataFrame with the songs into csv file
    '''

    csv_filepath = file_relative_path(
        __file__,
        '../local_destination/dest_orpheus_pipeline.csv'
    )
    transform_song_list_to_df.to_csv(csv_filepath)

    file_stats = os.stat(csv_filepath)
    csv_last_modification_date = datetime.fromtimestamp(
        file_stats.st_mtime,
        tz=timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S")

    context.log.info(f'''
    last modification on csv content (utc time): {csv_last_modification_date}
    ''')

@asset(
    group_name='orpheus_pipeline',
    retry_policy=retry_policy,
    freshness_policy=freshness_policy,
    required_resource_keys={"get_minio_conn"}
)
def load_csv_s3_dest(context, transform_song_list_to_df) -> None:
    '''
    '''
    minio_client = context.resources.get_minio_conn
    dest_bucket = os.getenv("S3_DESTINATION_BUCKET")
    csv_bytes = transform_song_list_to_df.to_csv().encode('utf-8')
    csv_buffer = BytesIO(csv_bytes)

    if minio_client.bucket_exists(dest_bucket) == True:
        minio_client.put_object(
            dest_bucket,
            "dest_orpheus_pipeline.csv",
            data=csv_buffer,
            length=len(csv_bytes),
            content_type='application/csv'
        )
    else:
        raise Exception(f'{dest_bucket} DOES NOT EXISTS')   
