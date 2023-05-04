from flask import jsonify,request,make_response
from functools import wraps
from utils.utils import read_env_json,read_sess_json,read_msg_json
import base64
from datetime import datetime
from flask import session
from utils.logs import logger


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        logger.info("Checking tokens")
        data_dict=read_env_json()
        ACTIVATE_LICENSE=bool(data_dict['ACTIVATE_LICENSE'])
        if ACTIVATE_LICENSE:
            AUTH_TOKEN=base64.urlsafe_b64decode(data_dict['AUTH_TOKEN'].encode()).decode()
            SESSION_TOKEN=read_sess_json()['SESS_TOKEN']
            api_sess_token=""
            api_auth_token=""
            if "auth_token" in request.headers:
                api_auth_token=request.headers['auth_token']
            else:
                logger.info("AUTHENTICATION:: Auth token missing")

            if "sess_token" in request.headers:
                api_sess_token=request.headers['sess_token']
            else:
                logger.info("AUTHENTICATION:: Session token missing")

            if(AUTH_TOKEN!='' and api_auth_token==AUTH_TOKEN):#check auth token
                if(SESSION_TOKEN!='' and api_sess_token==SESSION_TOKEN):
                    pass
                else:
                    logger.info("AUTHENTICATION:: A valid session token required")
                    return make_response(jsonify({"msg": "A valid session token required!","status_code":"401"}), 401)
            else:
                logger.info("AUTHENTICATION:: A valid auth token required")
                return make_response(jsonify({"msg": "A valid auth token is required!","status_code":"401"}), 401)
        else:
            return make_response(jsonify({"msg": "License activation is required!","status_code":"401"}), 401)
        return f(*args, **kwargs)
    return decorator