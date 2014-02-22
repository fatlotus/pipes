# sort.py

"""
A basic PIPEs handler for the Google App Engine that sorts the input as a list
of textual strings.
"""

import urllib
import urlparse
import cgi
from google.appengine.api.urlfetch import fetch

def app(environ, start_response):
    """
    Main WSGI entry point for the sort handler.
    """

    parameters = urlparse.parse_qs(environ["QUERY_STRING"])
    url_to_fetch = parameters.get("url", [""])[0]

    if url_to_fetch:
        # Fetch the incoming data.
        result = fetch(url_to_fetch, validate_certificate=True)

        # Propagate automatic retries upstream.
        if result.status_code == 404:
            start_response("404 Not Yet Ready", [])
            return []

        lines = result.content.split("\n")

        # Sort each line as a series of whitespace-delimited records.
        records = [line.strip().split() + ["", line] for line in lines]
        records.sort()

        # Return as response to the user.
        content_type = result.headers.get("Content-type", "text/plain")
        start_response("200 Okay", [("Content-type", content_type)])

        # Join the records together into lines.
        return [record[-1] + "\n" for record in records]

    else:
        # Parse the request body as a form parameters.
        field_storage = cgi.FieldStorage(
            fp=environ["wsgi.input"],
            environ=environ
        )

        # Retrieve the file to sort.
        source = field_storage.getfirst("source", "")

        if source:
            # Prepare a redirect to the proper URL.
            new_url = "/sort?" + urllib.urlencode({"url":source})

            start_response('303 See Other', [('Location', new_url)])
            return []

        else:
            # Generate a human-readable help page.
            start_response('200 Okay', [('Content-type', 'text/html')])
            return ["""
              <form method="post">
                Source URL: <input type="text" name="source"/>
                <input type="submit"/>
              </form>
            """]
