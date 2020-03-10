<h1 align="center">
<img width="400" src="https://www.python.org/static/community_logos/python-logo-inkscape.svg" alt="Python">
<br>
</h1>


>  # _python-bamboo-api_
- [INFO](#info)
- [REQS](#Requirements)



## INFO
An HTTP(S) REST API library used to communicate with [Bamboo Server](https://www.atlassian.com/software/bamboo).
This is beta version.

It was written in Python3.8.

The library handles authentication on behalf of the user.
The library exposes an API for stopping Bamboo plans.
If the Bamboo plan has artifacts on a particular stage, it can crawl the Bamboo server and return the direct
link to the artifact. Support for download is available too.


## Requirements

- For development I have used [Pycharm CE](https://www.jetbrains.com/pycharm/),
[Pyenv](https://github.com/pyenv/pyenv),
[Pipenv](https://pipenv-fork.readthedocs.io/en/latest/) and
[Poetry](https://python-poetry.org/).
- For testing I have use [Pytest](https://docs.pytest.org/en/latest/).