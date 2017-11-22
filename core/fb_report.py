
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

def main():
  parser = argparse.ArgumentParser(description='Generates an analytics report from Facebook analytics')
  parser.add_argument('filename', help='Facebook data exported in CSV format')
  args = parser.parse_args()

  def get_parsed_dataframe(csv_infile):
    df = pd.read_csv(csv_infile)
    df.drop(df.index[0])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')
    return df

  csv_page_infile = args.filename
  csv_post_infile = args.filename

  df_page = get_parsed_dataframe(csv_page_infile)
  df_posts = get_parsed_dataframe(csv_post_infile)

  csv_page_infile_name = os.path.basename(csv_page_infile).replace('.csv', '')
  analytics_page_html = os.path.join((Path(__file__) / ".." / "..").resolve(), 'graphs', '{0}.html'.format(csv_page_infile_name))
  generate_analytics_page(df_page, df_posts, analytics_page_html)

def generate_analytics_page(df_page, df_posts, html_outfile):

  def get_engagement_figure(source):
    p = figure(
      plot_width=1300, plot_height=600,
      x_axis_type="datetime",
      x_axis_label="Date", y_axis_label="Count", title="Page Engagement",
      tools="pan,wheel_zoom,box_zoom,reset"
    )

    p.line('Date', 'Daily Page Engaged Users', source=source, color='#7fc97f', legend='daily clicks', line_width=3)
    p.line('Date', 'Daily Total Impressions', source=source, color='#fdc086', legend='daily visits', line_width=3)
    p.line('Date', 'Daily Organic Reach', source=source, color='#e0ecf4', legend='daily organic visitors', line_width=1)
    p.line('Date', 'Daily Viral Reach', source=source, color='#9ebcda', legend='daily viral visitors', line_width=1)
    p.line('Date', 'Daily Total Reach', source=source, color='#beaed4', legend='daily visitors', line_width=3)

    p.legend.location = "top_left"
    p.legend.click_policy="hide"

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

  def get_likes_figure(source):
    p = figure(
      plot_width=1300, plot_height=600,
      x_axis_type="datetime",
      x_axis_label="Date", y_axis_label="Count", title="Total Likes",
      tools="pan,wheel_zoom,box_zoom,reset"
    )

    p.line('Date', 'Lifetime Total Likes', source=source, color='black', legend='likes', line_width=4)

    p.legend.location = "top_left"
    p.legend.click_policy="hide"

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

  def get_geographical_distribution_figure(df):

    column_header = 'Daily City: People Talking About This - '
    unwanted_cols = [col for col in df.columns if column_header not in col]
    df = df[df.columns.drop(unwanted_cols)]
    geographic_cols = [col.replace(column_header, '') for col in df.columns]
    geographic_values = []
    for col in df.columns:
      s = 0
      for xd in df[col]:
        try:
          x = float(xd)
        except ValueError:
          continue
        s += x if not math.isnan(x) else 0
      geographic_values.append(s)

    geographic_tuples = list(zip(geographic_cols, geographic_values))
    geographic_tuples.sort(key=lambda x : x[1], reverse=True)

    geographic_cols, geographic_values = zip(*geographic_tuples[0:10])

    p = figure(
      x_range=geographic_cols,
      plot_width=1300, plot_height=600,
      x_axis_label="Cities", y_axis_label="Count", title="Reader Locations"
    )
    p.vbar(x=geographic_cols, top=geographic_values, width=0.8)

    return p

  source_page = ColumnDataSource(df_page)

  if not os.path.exists(os.path.dirname(html_outfile)):
    try:
      os.makedirs(os.path.dirname(html_outfile))
    except OSError as exc:
      if exc.errno != errno.EEXIST:
        raise
  output_file(html_outfile)

  p0 = get_engagement_figure(source_page)
  p1 = get_likes_figure(source_page)

  notable_stories = [
    Span(
      location=datetime.datetime(2017,11,1,17,0).timestamp() * 1000,
      dimension='height',
      line_color='red', line_dash='dashed', line_width=1
    )
  ]
  p0.renderers.extend(notable_stories)
  p1.renderers.extend(notable_stories)

  p2 = get_geographical_distribution_figure(df_page)

  show(column(p0, p1, p2))

if __name__ == '__main__':
  main()