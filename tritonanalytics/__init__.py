#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask

from tritonanalytics.fbreport import generate_page_analytics, generate_post_analytics
from tritonanalytics.views import main, graphs
from tritonanalytics.constants import *

import logging

# Setup logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',level=logging.INFO)
logging.info("Logging initialized ... ✓")

# Setup page analytics
generate_page_analytics(FB_PAGE_ANALYTICS_INFILE, FB_POST_ANALYTICS_INFILE, FB_PAGE_ANALYTICS_OUTFILE)
generate_post_analytics(FB_PAGE_ANALYTICS_INFILE, FB_POST_ANALYTICS_INFILE, FB_POST_ANALYTICS_OUTFILE)
logging.info("Page & post analytics generated ... ✓")

# Start the web server
app = Flask(__name__)

# Register our blueprints
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(graphs, url_prefix='/graphs')