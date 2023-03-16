
import spotipy
from minio import Minio
from minio.error import S3Error
from contextlib import contextmanager
from dagster import resource
from os import getenv
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth 

@resource(
	description='all the permission strings that define spotify connection scope'
)
def get_scopes(init_context):
    read_scopes = {
    'library':'user-library-read',
    'recent_history':'user-read-recently-played',
    'currently_playing':'user-read-currently-playing',
    'top_songs_n_artists':'user-top-read',
    'following':'user-follow-read',
    'private':'user-read-private'}
    return read_scopes

@resource(
	description='general function to get spotify connection',
	required_resource_keys={'get_scopes'}
)
@contextmanager
def get_conn_recent_history(init_context):
    chosen_scope = init_context.resources.get_scopes
    try:
        # loading .env file variables
        load_dotenv()
        # defining py objects for the .env file variables 
        SPOTIPY_CLIENT_ID=getenv('SPOTIPY_CLIENT_ID')
        SPOTIPY_CLIENT_SECRET=getenv('SPOTIPY_CLIENT_SECRET')
        SPOTIPY_REDIRECT_URI=getenv('SPOTIPY_REDIRECT_URI')
        conn = spotipy.Spotify(
            auth_manager=SpotifyOAuth(scope=chosen_scope['recent_history'])
        )
        yield conn
    finally:
        for i in [SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI]: 
            del i

@resource(
    description='connection to minio s3 buckets'
)
@contextmanager
def get_minio_conn(init_context):
    try:
        # loading .env file variables
        load_dotenv()
        minio_conn = Minio(
            endpoint=getenv("MINIO_ENDPOINT"),
            access_key=getenv("MINIO_ACCESS_KEY"),
            secret_key=getenv("MINIO_SECRET_KEY"),
            secure=False #needed to use HTTP instead of HTTPS, since we don't have a TLS certificated
        )
        yield minio_conn
    except S3Error as excep:
        print("error occurred. ", excep)
    finally:
        del minio_conn
