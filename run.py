"""Python script to run flask directly."""
#!/bin/python3.6
from app import application
from flask_wtf.csrf import CSRFProtect
import sys

sys.path.insert(0, "/var/www/html/rack/")

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8000, debug=False)
