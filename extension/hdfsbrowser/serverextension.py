"""HdfsBrowser Jupyter Web Server Extension
This module adds a custom request handler to Jupyter web server.
It proxies the HDFS Browser by default running at $HDFS_NAMENODE_HOST:$HDFS_NAMENODE_PORT
to the endpoint notebook_base_url/hdfsbrowser
"""

from notebook.base.handlers import IPythonHandler
import tornado.web
from tornado import httpclient
import json
import re
import os
import logging
from traitlets.config import LoggingConfigurable
from traitlets.traitlets import Unicode
from bs4 import BeautifulSoup

proxy_root = "/hdfsbrowser"


class HdfsBrowserHandler(IPythonHandler):
    """A custom tornado request handler to proxy HDFS Browser requests."""

    @tornado.web.asynchronous
    def get(self):
        """Handles get requests to the HDFS Browser
        Fetches the webHDFS from the configured ports
        """
        # print("HDFSBROWSER_SERVER: Handler GET")
        http = httpclient.AsyncHTTPClient()
        # Without protocol and trailing slash
        baseurl = os.environ.get("HDFS_NAMENODE_HOST", "p01001532067275.cern.ch")
        port = os.environ.get("HDFS_NAMENODE_PORT", "50070")
        url = "http://" + baseurl + ":" + port
        # print("HDFS_SERVER: Request URI" + self.request.uri)
        # print("HDFS_SERVER: Getting from " + url)
        request_path = self.request.uri[(
            self.request.uri.index(proxy_root) + len(proxy_root) + 1):]
        self.replace_path = self.request.uri[:self.request.uri.index(
            proxy_root) + len(proxy_root)]
        print("HDFS_SERVER: Request_path " +
              request_path + " \n Replace_path:" + self.replace_path)
        backendurl = url_path_join(url, request_path)
        self.debug_url = url
        self.backendurl = backendurl
        logger.info("GET: \n Request uri:%s \n Port: %s \n Host: %s \n request_path: %s ", self.request.uri, os.environ.get(
            "HDFS_NAMENODE_PORT", "4040"), os.environ.get("HDFS_NAMENODE_HOST", "127.0.0.1"), request_path)
        http.fetch(backendurl, self.handle_response)

    def handle_response(self, response):
        """Sends the fetched page as response to the GET request"""
        if response.error:
            content_type = "application/json"
            content = json.dumps({"error": "HDFS Browser not reachable",
                                  "url": self.debug_url, "backendurl": self.backendurl, "replace_path": self.replace_path})
            print("HDFS_BROWSER: HDFS Browser not reachable")
        else:
            content_type = response.headers["Content-Type"]
            if "text/html" in content_type:
                content = replace(response.body, self.replace_path)
            elif "javascript" in content_type:
                content = response.body.replace(
                    "location.origin", "location.origin +'" + self.replace_path + "' ")
            else:
                # Probably binary response, send it directly.
                content = response.body
        self.set_header("Content-Type", content_type)
        self.write(content)
        self.finish()


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the Jupyter server extension is loaded.
    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    print("HDFSBROWSER_SERVER: Loading Server Extension")
    # Configuring logging for the extension
    # This is necessary because in some versions of jupyter, print statements are not output to console.

    global logger
    logger = logging.getLogger("hdfsbrowserserver")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    # For debugging this module - Writes logs to a file
    fh = logging.FileHandler("hdfsbrowser_serverextension.log", mode="w")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(levelname)s:  %(asctime)s - %(name)s - %(process)d - %(processName)s - \
        %(thread)d - %(threadName)s\n %(message)s \n")
    fh.setFormatter(formatter)
    logger.addHandler(fh) ## Comment this line to disable logging to a file.

    web_app = nb_server_app.web_app
    host_pattern = ".*$"
    route_pattern = url_path_join(
        web_app.settings["base_url"], proxy_root + ".*")
    web_app.add_handlers(host_pattern, [(route_pattern, HdfsBrowserHandler)])


try:
    import lxml
except ImportError:
    BEAUTIFULSOUP_BUILDER = "html.parser"
else:
    BEAUTIFULSOUP_BUILDER = "lxml"
# a regular expression to match paths against the Spark on EMR proxy paths
PROXY_PATH_RE = re.compile(r"\/proxy\/application_\d+_\d+\/(.*)")
# a tuple of tuples with tag names and their attribute to automatically fix
PROXY_ATTRIBUTES = (
    (("a", "link"), "href"),
    (("img", "script"), "src"),
)


def replace(content, root_url):
    """Replace all the links with our prefixed handler links,
     e.g.:
    /proxy/application_1467283586194_0015/static/styles.css" or
    /static/styles.css
    with
    /spark/static/styles.css
    """
    soup = BeautifulSoup(content, BEAUTIFULSOUP_BUILDER)
    for tags, attribute in PROXY_ATTRIBUTES:
        for tag in soup.find_all(tags, **{attribute: True}):
            value = tag[attribute]
            match = PROXY_PATH_RE.match(value)
            if match is not None:
                value = match.groups()[0]
            tag[attribute] = url_path_join(root_url, value)
    return str(soup)


def url_path_join(*pieces):
    """Join components of url into a relative url
    Use to prevent double slash when joining subpath. This will leave the
    initial and final / in place
    """
    initial = pieces[0].startswith("/")
    final = pieces[-1].endswith("/")
    stripped = [s.strip("/") for s in pieces]
    result = "/".join(s for s in stripped if s)
    if initial:
        result = "/" + result
    if final:
        result = result + "/"
    if result == "//":
        result = "/"
    return result
