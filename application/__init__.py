# application/__init__.py
import os

from flask import Flask
from flask import Flask, request, jsonify,render_template
from flask import send_file, send_from_directory
from datetime import datetime
from flask_cors import CORS
import base64
import sys
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

app = Flask(__name__, static_url_path='')
CORS(app)
app.config['SECRET_KEY']='jshdgTyHdsf123'

from sqlitedb import DataBase

DB = DataBase() 
conn = DB.create_connection(DB.DBFILE)
DB.create_table_data(conn,DB.TABLE)
DB.create_table_data(conn,DB.LOG_TABLE) 
DB.create_table_data(conn,DB.DASHBOARD_TABLE)

from . import routes