from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

import os
import logging

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = os.environ.get("GOOGLE_ID")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(query, max_results=25):
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=DEVELOPER_KEY)

        logging.debug("issuing youtube query: %s" % query)
        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results
        ).execute()

        videos = []

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append((search_result["snippet"]["title"],
                               "https://www.youtube.com/watch?v=%s" % search_result["id"]["videoId"]))


        return videos
    except HttpError, e:
        return []

if __name__ == "__main__":
    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results", default=25)
    args = argparser.parse_args()

    try:
        videos = youtube_search(args.q, args.max_results)
        print "\n".join(["%s: %s" % (x[0], x[1]) for x in videos])
    except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
