"""
Init file for Flask application.
"""

from flask import Flask

app = Flask(__name__)

app.config.update({"DEBUG": True, "TESTING": False})
