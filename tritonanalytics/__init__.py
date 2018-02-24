#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from pymongo import MongoClient
from threading import Thread

from tritonanalytics.fbreport import generate_page_analytics, generate_post_analytics, generate_dataframes
from tritonanalytics.views import main, graphs
from tritonanalytics.constants import *

import time
import logging
import os

# Amount of time to delay between force refreshes of the database
UPDATE_DELAY_SECONDS = 3600 # Every hour

# Setup logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',level=logging.INFO)
logging.info("Logging initialized ... ✓")

# Login to database
db_uri = os.environ.get("TRITON_ANALYTICS_MONGODB")
db = MongoClient(db_uri).get_database("tritonanalytics")
logging.info("Database login successful ... ✓")

# Pull information from the database occasionally
def update_analytics(db):
  logging.info("Forcing update of dataframes ...")

  start_time = time.time()
  generate_dataframes(db, force_update=True)
  logging.info("Force update took {0:.2f}s.".format(time.time() - start_time))

  sleep(UPDATE_DELAY_SECONDS)
  update_analytics(db)

# Start thread that updates dataframes
Thread(target=update_analytics, args=(db,))
logging.info("Database updater started ... ✓")

# Generate analytic HTML files
generate_page_analytics(db, PAGE_ANALYTICS_OUTFILE)
logging.info("Page analytics generated ... ✓")
generate_post_analytics(db, POST_ANALYTICS_OUTFILE)
logging.info("Post analytics generated ... ✓")

# Start the web server
app = Flask(__name__)

# Register our blueprints
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(graphs, url_prefix='/graphs')