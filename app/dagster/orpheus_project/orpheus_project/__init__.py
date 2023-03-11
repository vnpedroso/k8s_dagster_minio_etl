from dagster import Definitions, load_assets_from_modules
from . import assets
from .resources import (
	get_scopes,
	get_conn_recent_history
)

required_resources = {"get_scopes":get_scopes,"get_conn_recent_history":get_conn_recent_history}

defs = Definitions(
	assets=load_assets_from_modules([assets]),
	resources=required_resources
)
