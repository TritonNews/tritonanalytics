
from flask import Blueprint, render_template

import os

main = Blueprint('main', __name__)
graphs = Blueprint('graphs', __name__)

@main.route('/')
def landing_page():
  return render_template('index.html')

@graphs.route('/')
def graphs_landing_page():
  return render_template('graphs.html')

@graphs.route('/page/<analytics_id>')
def graphs_page_analytics(analytics_id):
  return render_template('graphs/page/{0}.html'.format(analytics_id))

@graphs.route('/posts/<analytics_id>')
def graphs_post_analytics(analytics_id):
  return render_template('graphs/posts/{0}.html'.format(analytics_id))