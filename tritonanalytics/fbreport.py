
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import HoverTool, ColumnDataSource, Span, FuncTickFormatter
from bokeh.layouts import column
from bokeh.transform import dodge

from pymongo import MongoClient

from collections import defaultdict

import argparse
import csv
import pandas as pd
import datetime
import os
import math
import logging
import time
import re

# Only copy over certain columns from database to dataframe
selected_columns = [
  'Date',
  'Daily Page Engaged Users',
  'Daily Total Impressions',
  'Daily Organic Reach',
  'Daily Viral Reach',
  'Daily Total Reach',
  'Lifetime Total Likes',
  'Posted',
  'Post Message',
  'Lifetime Post Total Reach',
  'Lifetime Engaged Users',
  'Lifetime Post Consumers',
  'Lifetime Post Consumptions'
  'Daily City: People Talking About This - '
]
selected_columns_regex = None

# Cache used for storing dataframes
df_cache = {}



def generate_dataframes(db, force_update=False):
  global selected_columns, selected_columns_regex

  # Get a list of cities and add them to our selected columns
  if not selected_columns_regex:
    selected_columns_regex = '|'.join(selected_columns)

  # Retrieve our page analytics dataframe
  df_page = _get_dataframe(db, 'fbpages', force_update)
  df_page['Date'] = pd.to_datetime(df_page['Date'])
  df_page = df_page.sort_values(by='Date')

  # Retrieve our posts analytics dataframe
  df_posts = _get_dataframe(db, 'fbposts', force_update)

  return df_page, df_posts



def _get_dataframe(db, coll_name, force_update):
  global df_cache, selected_columns_regex

  # Dataframe is already present in the cache (force updating is off)
  if not force_update and coll_name in df_cache:
    return df_cache[coll_name]

  # Either we got a cache miss or updates are being forced
  coll = db[coll_name]

  # Convert MongoDB documents to tabular data
  data = {}
  for doc in coll.find():
    for column, value in doc.items():
      if re.search(selected_columns_regex, column):
        if column in data:
          data[column].append(value)
        else:
          data[column] = [value]

  # Cache the new dataframe
  df = pd.DataFrame(data=data)
  df_cache[coll_name] = df

  return df



def generate_page_analytics(db, html_outfile, show_in_browser=False):
  # Generate column sources from the dataframes
  df_page, df_posts = generate_dataframes(db)
  source_page = ColumnDataSource(df_page)
  source_posts = ColumnDataSource(df_posts)

  # Recursively create directories up to the outfile if they do not exist already
  if not os.path.exists(os.path.dirname(html_outfile)):
    try:
      os.makedirs(os.path.dirname(html_outfile))
    except OSError as exc:
      if exc.errno != errno.EEXIST:
        raise

  # Set our output file
  output_file(html_outfile)

  #############################################################################

  def get_engagement_figure():
    # Create our figure
    p = figure(
      plot_width=1300, plot_height=600,
      x_axis_type="datetime",
      x_axis_label="Date", y_axis_label="Count", title="Page Engagement",
      tools="pan,wheel_zoom,box_zoom,reset"
    )

    # Add line(s)
    p.line('Date', 'Daily Page Engaged Users', source=source_page, color='#7fc97f', legend='daily clicks', line_width=3)
    p.line('Date', 'Daily Total Impressions', source=source_page, color='#fdc086', legend='daily visits', line_width=3)
    p.line('Date', 'Daily Organic Reach', source=source_page, color='#e0ecf4', legend='daily organic visitors', line_width=1)
    p.line('Date', 'Daily Viral Reach', source=source_page, color='#9ebcda', legend='daily viral visitors', line_width=1)
    p.line('Date', 'Daily Total Reach', source=source_page, color='#beaed4', legend='daily visitors', line_width=3)

    # Specify legend behavior
    p.legend.location = "top_left"
    p.legend.click_policy="hide"

    # Add the hover tool
    p.add_tools(HoverTool(
      tooltips=[
        ('Date', '@Date{%F}'),
        ('Count', '$y{int}')
      ],
      formatters={
        'Date': 'datetime'
      },
      mode='mouse' # TODO: Figure out why vline is not working
    ))

    return p

  #############################################################################

  def get_likes_figure():
    # Create our figure
    p = figure(
      plot_width=1300, plot_height=600,
      x_axis_type="datetime",
      x_axis_label="Date", y_axis_label="Count", title="Total Likes",
      tools="pan,wheel_zoom,box_zoom,reset"
    )

    # Add line(s)
    p.line('Date', 'Lifetime Total Likes', source=source_page, color='black', legend='likes', line_width=4)

    # Specify legend behavior
    p.legend.location = "top_left"

    # Add the hover tool
    p.add_tools(HoverTool(
      tooltips=[
        ('Date', '@Date{%F}'),
        ('Count', '$y{int}')
      ],
      formatters={
        'Date': 'datetime'
      },
      mode='mouse' # TODO: Figure out why vline is not working
    ))

    return p

  #############################################################################

  def get_geographical_distribution_figure(df_page):

    # Reduce columns of the dataframe down to geographics
    column_header = 'Daily City: People Talking About This - '
    unwanted_cols = [col for col in df_page.columns if column_header not in col]
    df_page = df_page[df_page.columns.drop(unwanted_cols)]

    # Switch columns with rows in DataFrame, reduce to top 10 cities
    series_page = df_page.sum()
    df_page = pd.DataFrame({'City': series_page.index, 'Readers': series_page.values})
    df_page = df_page.nlargest(10, 'Readers')
    df_page['City'] = df_page['City'].replace({row:row.replace(column_header, '') for row in df_page['City']})
    source_page = ColumnDataSource(df_page)

    # Prune out columns
    geographic_cols = df_page['City'].tolist()

    # Create our figure
    p = figure(
      x_range=geographic_cols,
      plot_width=1300, plot_height=600,
      x_axis_label="Cities", y_axis_label="Count", title="Reader Locations"
    )

    # Add demographics
    p.vbar(x='City', top='Readers', source=source_page, width=0.8)

    # Add hover tool
    p.add_tools(HoverTool(
      tooltips=[
        ('City', '@City'),
        ('Readers', '@Readers')
      ],
      formatters={
        'Posted': 'datetime'
      },
      mode='vline'
    ))

    # No vertical grid lines
    p.xgrid.grid_line_color = None

    return p

  #############################################################################

  # Create our engagement and likes line graphs
  p0 = get_engagement_figure()
  p1 = get_likes_figure()

  '''
  # Add vertical spans to denote stories/dates of interest
  notable_stories = [
    Span(
      location=datetime.datetime(2017,11,1,17,0).timestamp() * 1000,
      dimension='height',
      line_color='red', line_dash='dashed', line_width=1
    )
  ]
  p0.renderers.extend(notable_stories)
  p1.renderers.extend(notable_stories)
  '''

  # Create a geographical distribution bar chart below line graphs
  p2 = get_geographical_distribution_figure(df_page)

  # Show all charts vertically displaced from each other
  if show_in_browser:
    show(column(p0, p1, p2))
  else:
    save(column(p0, p1, p2))
    _disable_jinja2(html_outfile)



def generate_post_analytics(db, html_outfile, show_in_browser=False):
  # Generate column sources from the dataframes
  df_page, df_posts = generate_dataframes(db)
  source_page = ColumnDataSource(df_page)
  source_posts = ColumnDataSource(df_posts)

  # Recursively create directories up to the outfile if they do not exist already
  if not os.path.exists(os.path.dirname(html_outfile)):
    try:
      os.makedirs(os.path.dirname(html_outfile))
    except OSError as exc:
      if exc.errno != errno.EEXIST:
        raise

  # Set our output file
  output_file(html_outfile)

  #############################################################################

  def get_favorite_posts_figure(df_posts):
    # Dataframe manipulation
    df_posts['Posted'] = pd.to_datetime(df_posts['Posted'])
    df_posts['Lifetime Post Total Reach'] = df_posts['Lifetime Post Total Reach'].apply(pd.to_numeric, errors='ignore')
    df_posts = df_posts.nlargest(5, 'Lifetime Post Total Reach')
    source_posts = ColumnDataSource(df_posts)

    post_messages = df_posts['Post Message'].tolist()

    # Create our figure
    p = figure(
      x_range=post_messages,
      plot_width=1300, plot_height=600,
      title="Favorite Posts",
    )

    # For each post, show total reach
    p.vbar(
      x=dodge('Post Message', -0.3, range=p.x_range), width=0.1,
      top='Lifetime Post Total Reach', source=source_posts,
      color="#1b9e77", legend="unique visitors"
    )

    # For each post, show engaged users
    p.vbar(
      x=dodge('Post Message', -0.1, range=p.x_range), width=0.1,
      top='Lifetime Engaged Users', source=source_posts,
      color="#99d8c9", legend="likes/comments/shares"
    )

    # For each post, show consumers
    p.vbar(
      x=dodge('Post Message', 0.1, range=p.x_range), width=0.1,
      top='Lifetime Post Consumers', source=source_posts,
      color="#d95f02", legend="unique clicks"
    )

    # For each post, show consumptions
    p.vbar(
      x=dodge('Post Message', 0.3, range=p.x_range), width=0.1,
      top='Lifetime Post Consumptions', source=source_posts,
      color="#fdbb84", legend="total clicks"
    )

    # Add hover tool
    p.add_tools(HoverTool(
      tooltips=[
        ('Title', '@{Post Message}'),
        ('Date', '@Posted{%F %T}')
      ],
      formatters={
        'Posted': 'datetime'
      },
      mode='vline'
    ))

    # No vertical grid lines & format ticks so whole text is not displaying
    p.xgrid.grid_line_color = None
    p.xaxis.formatter = FuncTickFormatter(code="""
        return tick.split(' ').slice(0,7).join(' ') + '...'
    """)

    return p

  #############################################################################

  p0 = get_favorite_posts_figure(df_posts)

  if show_in_browser:
    show(p0)
  else:
    save(p0)
    _disable_jinja2(html_outfile)

def _disable_jinja2(html_outfile):
  with open(html_outfile, 'r') as f:
    raw_html = f.read()
  with open(html_outfile, 'w') as f:
    f.write('{% raw %}')
    f.write(raw_html)
    f.write('\n{% endraw %}')

def main():
  # Setup argument parser
  parser = argparse.ArgumentParser(description='Generates an analytics report from Facebook analytics')
  parser.add_argument('db', help='URI of MongoDB used to hold analytics data')
  args = parser.parse_args()

  # Setup logging
  logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',level=logging.INFO)

  # Login to database
  logging.info("Logging into database ...")
  db = MongoClient(args.db).get_database("tritonanalytics")

  # Generate page analytics in graphs/pages.html
  logging.info('Generating page analytics ...')
  start_time = time.time()
  generate_page_analytics(db, os.path.join('graphs', 'pages.html'), show_in_browser=True)
  logging.info('Took {0:.2f} seconds.'.format(time.time() - start_time))

  # Generate post analytics in graphs/posts.html
  logging.info('Generating post analytics ...')
  start_time = time.time()
  generate_post_analytics(db, os.path.join('graphs', 'posts.html'), show_in_browser=True)
  logging.info('Took {0:.2f} seconds.'.format(time.time() - start_time))

if __name__ == '__main__':
  main()