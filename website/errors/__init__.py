from flask import Blueprint

bp = Blueprint('errors', __name__)

from website.errors import handlers
