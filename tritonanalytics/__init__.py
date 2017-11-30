#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask

from tritonanalytics.fbreport import generate_page_analytics, generate_post_analytics
from tritonanalytics.views import main, graphs
from tritonanalytics.constants import *

import logging
import glob
import os

# Setup logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',level=logging.INFO)
logging.info("Logging initialized ... ✓")

# Setup page analytics
for infile_page in glob.glob(os.path.join(DATA_INFOLDER, '*')):
  infilename_page = os.path.basename(infile_page)
  if 'page' not in infilename_page:
    continue
  infile_posts = infile_page.replace('page-', 'posts-')
  outfilename = infilename_page.replace('page-', '').replace('.csv', '.html')
  outfile_page = os.path.join(GRAPHS_OUTFOLDER, 'page', outfilename)
  outfile_posts = os.path.join(GRAPHS_OUTFOLDER, 'posts', outfilename)
  generate_page_analytics(infile_page, infile_posts, outfile_page)
  generate_post_analytics(infile_page, infile_posts, outfile_posts)
logging.info("Page & post analytics generated ... ✓")

# Start the web server
app = Flask(__name__)

# Register our blueprints
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(graphs, url_prefix='/graphs')