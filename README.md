# tritonanalytics

![Analytics sample](https://github.com/TritonNews/tritonanalytics/blob/master/tritonanalytics/static/img/sample_graph.png)

__tritonanalytics__ is the work of the fledging analytics department of [The Triton](http://triton.news) newspaper.

It currently contains:
* A core module that turns exported data from Facebook Analytics into pretty, informative graphs (see top). Currently run manually; once data collection is automated, this will be run as a cron task.
* A Flask microserver that, along with displaying the graphs, outputs useful information about The Triton and the work we do.
* An internal repository of data including unparsed Facebook Analytics CSV files.

Keep in mind that this is a work-in-progress. On our TODO list ...
* Integrating post-specific data in the form of Spans on to existing page-specific graphs
* Predicting optimal times to post (time & day)
* Finding an ideal headline format as well as ideal content types
* Finding optimal times to market with paid ads

Libraries used:
* Python 3.6
* bokeh 0.12.10
* pandas 0.20.3
* flask 0.12.2
