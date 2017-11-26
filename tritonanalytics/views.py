
from flask import Blueprint

main = Blueprint('main', __name__)
graphs = Blueprint('graphs', __name__)

@main.route('/')
def landing_page():
  return 'Analytics site for The Triton'

@graphs.route('/')
def graphs_landing_page():
  return 'Graphs will go here'