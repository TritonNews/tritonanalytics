
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
  return render_template('graphs.html', page_records=_get_html_by_ctime('page'), posts_records=_get_html_by_ctime('posts'))

@graphs.route('/page/<analytics_id>')
def graphs_page_analytics(analytics_id):
  return _graph_analytics(analytics_id, 'page')

@graphs.route('/posts/<analytics_id>')
def graphs_posts_analytics(analytics_id):
  return _graph_analytics(analytics_id, 'posts')

def _get_html_by_ctime(analytics_type):
  dir_path = os.path.dirname(os.path.realpath(__file__))
  analytics_path = os.path.join(dir_path, 'templates', 'graphs', analytics_type, '*.html')
  sorted_files = sorted(glob.iglob(analytics_path), key=os.path.getctime, reverse=True)
  sorted_dicts = []
  for filepath in sorted_files:
    analytics_id = ntpath.basename(filepath).replace('.html', '')
    sorted_dicts.append({
      'href': '/graphs/{0}/{1}'.format(analytics_type, analytics_id),
      'caption': analytics_id
    })
  return sorted_dicts

def _graph_analytics(analytics_id, analytics_type):
  if analytics_id == 'current':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    analytics_path = os.path.join(dir_path, 'templates', 'graphs', analytics_type, '*.html')
    template_file = max(glob.iglob(analytics_path), key=os.path.getctime)
    analytics_id = ntpath.basename(template_file).replace('.html', '')
  try:
    return render_template('graphs/{0}/{1}.html'.format(analytics_type, analytics_id))
  except TemplateNotFound:
    return abort(404)