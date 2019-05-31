"""Initialize server."""
from flask import Flask

application = Flask(__name__)

application.config.from_object("config")

# Seems to only run if you import views at end of file so ignore linter.
from app import views
