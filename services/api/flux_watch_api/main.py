import logging.config

from flux_watch_api.create_app import create_app

app = create_app()
logging.config.dictConfig(app.config.LOGGING_CONFIG)
