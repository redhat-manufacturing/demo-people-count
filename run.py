from application import app
from dotenv import *
load_dotenv(override=True)
import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ['SPORT'])