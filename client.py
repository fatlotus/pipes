#!/usr/bin/env python

"""
Client driver for PIPE.
"""

from __future__ import print_function

import os
import sys
import urllib2
import urllib
import cookielib
import urlparse

class RedirectBlocker(urllib2.HTTPErrorProcessor):
    """
    This subclass disables automatic redirect handling in the client.
    """

    def __init__(self):
        pass

    def http_response(self, request, response):
        return response
    https_response = http_response
        # http://stackoverflow.com/a/11744894/1028526


def main():
    """
    Main parser for a PIPE shell script.
    """

    # Set up background.
    prefixes = (os.environ.get('HTTPPATH') or "").split(";")
    commands = (url.strip() for url in sys.argv[1].split("|"))
    previous = None

    if "" not in prefixes:
        prefixes.append("")

    # Prepare a redirect-less URL opener.
    cookiejar = cookielib.CookieJar()
    opener = urllib2.build_opener(RedirectBlocker,
                                  urllib2.HTTPCookieProcessor(cookiejar))

    for command in commands:
        for prefix in prefixes:
            # Build a plausible URL with this prefix.
            url = prefix + "/" + command

            if not url.startswith('http'):
                continue

            # Fetch each code, as appropriate.
            result = opener.open(url, urllib.urlencode({'source': previous}))

            # Handle resulting data.
            if result.code == 303:
                previous = urlparse.urljoin(url, result.info()['Location'])
            elif result.code in (200, 201):
                previous = url
            elif result.code == 404:
                continue
            else:
                print("URL: {!r}".format(url))
                print("HTTP Error: {!r}".format(result.code))
                print("")
                print(result.read())
                sys.exit(1)

            break

        else:
            print("Unknown command: {!r}".format(command))
            sys.exit(2)

    # Retrieve the final result from the last item in the pipeline.
    result = urllib.urlopen(previous)
    print(result.read())

if __name__ == "__main__":
    main()
