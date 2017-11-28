import os

dir_path = os.path.dirname(os.path.realpath(__file__))
FB_PAGE_ANALYTICS_INFILE = os.path.join(dir_path, 'data', 'fb-page-11-27-2017.csv')
FB_POST_ANALYTICS_INFILE = os.path.join(dir_path, 'data', 'fb-posts-11-27-2017.csv')
FB_PAGE_ANALYTICS_OUTFILE = os.path.join(dir_path, 'templates', 'graphs', 'page', 'fb-11-27-2017.html')
FB_POST_ANALYTICS_OUTFILE = os.path.join(dir_path, 'templates', 'graphs', 'posts', 'fb-11-27-2017.html')

