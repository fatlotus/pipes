# head.py

"""
A basic PIPEs handler for the Google App Engine that returns the first N lines
of the given file.
"""

import urllib
import urlparse
import cgi
from google.appengine.api.urlfetch import fetch

def app(environ, start_response):
    """
    Main WSGI entry point for the head handler.
    """

    parameters = urlparse.parse_qs(environ["QUERY_STRING"])
    url_to_fetch = parameters.get("url", [""])[0]
    number_of_lines = int(parameters.get("lines", ["0"])[0])

    if url_to_fetch:
        # Fetch the incoming data.
        result = fetch(url_to_fetch, validate_certificate=True)

        # Propagate automatic retries upstream.
        if result.status_code == 404:
            start_response("404 Not Yet Ready", [])
            return []

        lines = result.content.split("\n")

        # Return as response to the user.
        content_type = result.headers.get("Content-type", "text/plain")
        start_response("200 Okay", [("Content-type", content_type)])

        # Join the records together into lines.
        return [line + "\n" for line in lines[:number_of_lines]]

    else:
        # Parse the request body as a form parameters.
        field_storage = cgi.FieldStorage(
            fp=environ["wsgi.input"],
            environ=environ
        )

        # Retrieve the file to sort.
        source = field_storage.getfirst("source", "")
        lines = int(field_storage.getfirst("lines", "100"))

        if source:
            # Prepare a redirect to the proper URL.
            new_url = "/head?" + urllib.urlencode(
              {"url":source, "lines":str(lines)})

            start_response('303 See Other', [('Location', new_url)])
            return []

        else:
            # Generate a human-readable help page.
            start_response('200 Okay', [('Content-type', 'text/html')])
            return ["""
              <form method="post">
                Source URL: <input type="text" name="source"/>
                Number of lines: <input type="text" name="lines" value="100"/>
                <input type="submit"/>
              </form>
            """]
