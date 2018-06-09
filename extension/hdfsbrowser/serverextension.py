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

    http = httpclient.AsyncHTTPClient()

    def set_default_headers(self):
        print "setting headers!!!"
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', "*")

    @tornado.web.asynchronous
    def get(self):
        """Handles get requests to the HDFS Browser
        Fetches the webHDFS from the configured ports
        """
        # Without protocol and trailing slash
        baseurl = os.environ.get("HDFS_NAMENODE_HOST", "80.158.23.74")
        port = os.environ.get("HDFS_NAMENODE_PORT", "50070")
        url = "http://" + baseurl + ":" + port
        
	self.request_path = self.request.uri[(
            self.request.uri.index(proxy_root) + len(proxy_root) + 1):]

        self.replace_path = self.request.uri[:self.request.uri.index(
            proxy_root) + len(proxy_root)]

	log.debug("GET: Request uri:%s Port: %s request_path: %s replace_path: %s", self.request.uri, port, self.request_path, self.replace_path)
  
        self.fetch_content(url_path_join(url, self.request_path))


    def fetch_content(self, url):
        """Fetches the requested content"""
        log.debug("Fetching content from: %s", url)
        self.http.fetch(url, self.handle_response)


    def handle_response(self, response):
        """Sends the fetched page as response to the GET request"""
        if response.error:
            content_type = "application/json"
            content = json.dumps({"error": "HDFS Browser not reachable",
                                  "backendurl": response.effective_url, "replace_path": self.replace_path})
            print("HDFS_BROWSER: HDFS Browser not reachable")
        else:
            content_type = response.headers["Content-Type"]
            if "text/html" in content_type:
                content = replace(response.body, self.replace_path)
            elif "javascript" in content_type:
                content = response.body.decode().replace(
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
    # Configuring logging for the extension
    # This is necessary because in some versions of jupyter, print statements are not output to console.

    global log
    log = logging.getLogger('tornado.hdfsbrowser.server')
    log.name = "hdfsBrowser"
    log.setLevel(logging.DEBUG)
    log.propagate = True

    log.info("Loading Server Extension")

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
PROXY_PATH_RE = re.compile(r"(.*)")
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
            tag_old = tag
            value = tag[attribute]
            match = PROXY_PATH_RE.match(value)
            if match is not None:
                value = match.groups()[0]
            tag[attribute] = url_path_join(root_url, value)
            log.debug("REPLACE: tag_attribute_old: %s tag_attribute_new: %s", value, tag[attribute])
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
