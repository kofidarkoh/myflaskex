from flask import Blueprint 
from .utils import GenHashPassword,CheckPassword, GenHexDigest

auth = Blueprint('auth', __name__)
