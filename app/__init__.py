from flask import Blueprint
from controller import *

project = Blueprint(
	__name__,
	__name__,
	template_folder="views",
	static_folder="static"
)

app.register_views( project )