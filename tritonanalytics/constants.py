import os

dir_path = os.path.dirname(os.path.realpath(__file__))
GRAPHS_OUTFOLDER = os.path.join(dir_path, 'templates', 'graphs')

PAGE_ANALYTICS_OUTFILE = os.path.join(GRAPHS_OUTFOLDER, 'pages.html')
PAGE_ANALYTICS_OUTPATH = 'graphs/pages.html'

POST_ANALYTICS_OUTFILE = os.path.join(GRAPHS_OUTFOLDER, 'posts.html')
POST_ANALYTICS_OUTPATH = 'graphs/posts.html'