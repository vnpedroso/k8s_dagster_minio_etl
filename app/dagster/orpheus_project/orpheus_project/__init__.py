from dotenv import load_dotenv
from os import getenv
from dagster import Definitions
from orpheus_project.assets import (
    api_conn_recent_history_scope,
    extract_most_recent_50_songs,
    transform_song_list_to_df,
    load_csv_local_dest,
    load_csv_s3_dest
) 
from orpheus_project.resources import (
	get_scopes,
	get_conn_recent_history,
    get_minio_conn
)

local_resources = {
    "get_scopes" : get_scopes,
    "get_conn_recent_history" : get_conn_recent_history
}
local_assets = [
    api_conn_recent_history_scope,
    extract_most_recent_50_songs,
    transform_song_list_to_df,
    load_csv_local_dest
]

k8s_resources = {
    "get_scopes" : get_scopes,
    "get_conn_recent_history" : get_conn_recent_history,
    "get_minio_conn": get_minio_conn
}
k8s_assets = [
    api_conn_recent_history_scope,
    extract_most_recent_50_songs,
    transform_song_list_to_df,
    load_csv_s3_dest
]

#loading env variables
load_dotenv()

if getenv("DEPLOY_MODE") == "LOCAL":
    defs = Definitions(
        assets=local_assets,
        resources=required_resources
    )
elif getenv("DEPLOY_MODE") == "K8S":
    defs = Definitions(
        assets=k8s_assets,
        resources=required_resources
    )    
else:
    raise ValueError("DEPLOY_MODE env variable either is not set or has the wrong value")
