# Get logger object
import logging, logging.config
from pathlib import Path
import os
from datetime import datetime

LOGS_DIR = "application/logs/"
p = Path(LOGS_DIR)
if not p.exists():
	os.makedirs(LOGS_DIR)

dictConfig = {
	'version': 1,
	'disable_existing_loggers': True,
	'formatters': {
		'standard': {
			'format': '%(asctime)s [%(levelname)s] %(name)s:: %(message)s',
		},
	},
	'handlers': {
		'default': {
			'level': 'INFO',
			'formatter': 'standard',
			'class': 'logging.StreamHandler',
			'stream': 'ext://sys.stdout',
		},
		'file': {
			'class': 'logging.handlers.RotatingFileHandler',
			'level': 'DEBUG',
			'formatter': 'standard',
			'filename': os.path.join(LOGS_DIR,'logfile.log'),
			'mode': 'a',
			'maxBytes': 5_242_880,
			'backupCount': 3,
			'encoding': 'utf-8',
		},
	},
	'loggers': {
		'__main__': {
			'handlers': ['default','file'],
			'level': 'DEBUG',
			'propagate': False,
		},
		'camera': {
			'handlers': ['default', 'file'],
			'level': 'DEBUG',
			'propagate': False,
		},
	}
}


if (os.name == 'nt'):
    log_filename = "{}logfile_{}.log".format(LOGS_DIR, str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
else:
    log_filename = "{}logfile_{}.log".format(LOGS_DIR, str(datetime.now()))
logging.basicConfig(filename=log_filename,
                    format='%(asctime)s %(message)s',
                    filemode='w')

logging.config.dictConfig(dictConfig)
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)