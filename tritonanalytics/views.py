
from tritonanalytics.constants import *

from flask import Blueprint, render_template, abort
from jinja2.exceptions import TemplateNotFound

import os
import glob
import ntpath

main = Blueprint('main', __name__)
graphs = Blueprint('graphs', __name__)

@main.route('/')
def landing_page():
  return render_template('index.html')

@graphs.route('/')
def graphs_landing_page():
  return render_template('graphs.html')

@graphs.route('/pages')
def graphs_page_analytics():
  return render_template(PAGE_ANALYTICS_OUTPATH)

@graphs.route('/posts')
def graphs_posts_analytics():
  return render_template(POST_ANALYTICS_OUTPATH)