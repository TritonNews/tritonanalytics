import os

dir_path = os.path.dirname(os.path.realpath(__file__))
FB_PAGE_ANALYTICS_INFILE = os.path.join(dir_path, 'data', 'fb_page_analytics_2017-11-19.csv')
FB_POST_ANALYTICS_INFILE = os.path.join(dir_path, 'data', 'fb_post_analytics_2017-11-19.csv')
FB_PAGE_ANALYTICS_OUTFILE = os.path.join(dir_path, 'graphs', 'fb_page_analytics_2017-11-19.html')
FB_POST_ANALYTICS_OUTFILE = os.path.join(dir_path, 'graphs', 'fb_post_analytics_2017-11-19.html')

