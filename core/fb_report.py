
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool, ColumnDataSource, Span
from bokeh.layouts import column

from pathlib import Path

import argparse
import csv
import pandas as pd
import datetime
import os
import math
import logging

def main():

  # Setup argument parser
  parser = argparse.ArgumentParser(description='Generates an analytics report from Facebook analytics')
  parser.add_argument('csv_page_infile', help='Facebook page data exported in CSV format')
  parser.add_argument('csv_post_infile', help='Facebook posts data exported in CSV format')
  args = parser.parse_args()

  # Get arguments
  csv_page_infile = args.csv_page_infile
  csv_post_infile = args.csv_post_infile

  # Generate page analytics in ../../graphs/{CSV_PAGE_ANALYTICS_INFILE}.html
  logging.info('Generating page analytics ...')
  html_outfile_name = os.path.basename(csv_page_infile).replace('.csv', '')
  html_outfile = os.path.join((Path(__file__) / ".." / "..").resolve(), 'graphs', '{0}.html'.format(html_outfile_name))
  generate_page_analytics(csv_page_infile, csv_post_infile, html_outfile)

  # Generate post analytics in ../../graphs/{CSV_POST_ANALYTICS_INFILE}.html
  logging.info('Generating post analytics ...')
  html_outfile_name = os.path.basename(csv_post_infile).replace('.csv', '')
  html_outfile = os.path.join((Path(__file__) / ".." / "..").resolve(), 'graphs', '{0}.html'.format(html_outfile_name))
  generate_post_analytics(csv_page_infile, csv_post_infile, html_outfile)

def generate_page_analytics(csv_page_infile, csv_post_infile, html_outfile):

  # Create our page analytics dataframe
  df_page = pd.read_csv(csv_page_infile)
  df_page.drop(df_page.index[0])
  df_page['Date'] = pd.to_datetime(df_page['Date'])
  df_page = df_page.sort_values(by='Date')

  # Create our posts analytics dataframe
  df_posts = pd.read_csv(csv_post_infile)
  df_posts.drop(df_posts.index[0])

  # Generate column sources from the dataframes
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

  def get_geographical_distribution_figure(df_page):

    # Get a list of keys to values (keys being cities, values being number of users per city)
    column_header = 'Daily City: People Talking About This - '
    unwanted_cols = [col for col in df_page.columns if column_header not in col]
    df_page = df_page[df_page.columns.drop(unwanted_cols)]
    geographic_cols = [col.replace(column_header, '') for col in df_page.columns]
    geographic_values = []
    for col in df_page.columns:
      s = 0
      for xd in df_page[col]:
        try:
          x = float(xd)
        except ValueError:
          continue
        s += x if not math.isnan(x) else 0
      geographic_values.append(s)

    # Zip up keys and values, sort, get the top 10 and then unpack
    geographic_tuples = list(zip(geographic_cols, geographic_values))
    geographic_tuples.sort(key=lambda x : x[1], reverse=True)
    geographic_cols, geographic_values = zip(*geographic_tuples[0:10])

    # Create our figure
    p = figure(
      x_range=geographic_cols,
      plot_width=1300, plot_height=600,
      x_axis_label="Cities", y_axis_label="Count", title="Reader Locations"
    )
    p.vbar(x=geographic_cols, top=geographic_values, width=0.8)

    return p

  # Create our engagement and likes line graphs
  p0 = get_engagement_figure()
  p1 = get_likes_figure()

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

  # Create a geographical distribution bar chart below line graphs
  p2 = get_geographical_distribution_figure(df_page)

  # Show all charts vertically displaced from each other
  show(column(p0, p1, p2))

def generate_post_analytics(csv_page_infile, csv_post_infile, html_outfile):
  # Create our page analytics dataframe
  df_page = pd.read_csv(csv_page_infile)
  df_page.drop(df_page.index[0])
  df_page['Date'] = pd.to_datetime(df_page['Date'])
  df_page = df_page.sort_values(by='Date')

  # Create our posts analytics dataframe
  df_posts = pd.read_csv(csv_post_infile)
  df_posts.drop(df_posts.index[0])

  # Generate column sources from the dataframes
  source_page = ColumnDataSource(df_page)

  # Recursively create directories up to the outfile if they do not exist already
  if not os.path.exists(os.path.dirname(html_outfile)):
    try:
      os.makedirs(os.path.dirname(html_outfile))
    except OSError as exc:
      if exc.errno != errno.EEXIST:
        raise

  # Set our output file
  output_file(html_outfile)

  def get_favorite_posts_figure(df_posts):
    pass

  # TODO: Add figures

if __name__ == '__main__':
  main()