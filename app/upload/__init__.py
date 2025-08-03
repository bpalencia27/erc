from flask import Blueprint
bp = Blueprint('uploader', __name__)
from app.upload import routes
