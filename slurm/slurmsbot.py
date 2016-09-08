#!/home/ubuntu/anaconda2/bin/python

import os
import time
from slackclient import SlackClient
import json
import logging
import sys

from sqlite_store import SqliteStore
from learner import Learner
from plusser import Plusser
from imgur import Imgur
import youtube
from writer import Writer
from meme import Memer

import subprocess

"""
  looks for commands that start with ?
"""


# starterbot's ID as an environment variable
BOT_ID = str(os.environ.get("BOT_ID"))
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

def pipe(command, details, channel):    
    details_string = " ".join(details)
    components = details_string.split("|")
    details = [x for x in components.pop(0).split(" ") if x != ""]
    command = details.pop(0)

    while len(components) > 0:
        print details
        response = handle_command(command, details, channel, False)
        new_components = [x for x in components.pop(0).split(" ") if x != ""]
        command = new_components.pop(0)
        details = new_components + response.split(" ")

    handle_command(command, details, channel)

def handle_command(command, details, channel, respond = True):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = False
    if command == "learn":
        learner = Learner()
        response = learner.learn(details[0], " ".join(details[1:]))
    elif command == "unlearn":
        learner = Learner()
        content = None
        if len(details) > 1:
            content = " ".join(details[1:])
    
        response = learner.unlearn(details[0], content)

    elif command == "meme":
        memer = Memer()
        if not details or len(details) == 0:
            response = memer.list_templates()
        else:
            template = details.pop(0).strip()
            parts = [x.strip() for x in " ".join(details).split(",")]
            top = parts[0] if len(parts) > 0 else None
            bottom = parts[1] if len(parts) > 1 else None

            response = memer.get_meme(template, top, bottom)
            
    elif command == "hostname":
        response = "slurms coming to you live from: `%s (%s)`" % (subprocess.check_output("hostname -A",  shell=True).strip(), subprocess.check_output("hostname -i",  shell=True).strip())
    elif command == "write":
        writer = Writer()
        response = writer.get_writing(" ".join(details))
    elif command == "imglearn":
        learner = Learner()
        imgur = Imgur()
        image_url = imgur.save_from_url(" ".join(details[1:]))
        response = learner.learn(details[0], image_url)

    elif command == "++" or command == "endorse":
        plusser = Plusser()
        reason = ""
        if len(details) > 1:
            reason = " ".join(details[1:])

        response = plusser.plus(details[0], reason)
    elif command == "plusses":
        plusser = Plusser()
        response = plusser.get(details[0])
        
    elif command == "leaders" or command == "leader_board":
        plusser = Plusser()
        response = plusser.leader_board()

    elif command == "monthly_leaders" or command == "monthly_leader_board":
        plusser = Plusser()
        months_ago = 0
        if details and len(details) > 0:
            months_ago = details[0]
        response = plusser.monthly_leader_board(months_ago)

    elif command == "youtube":
        query = " ".join(details)
        videos = youtube.youtube_search(query)
        if len(videos) > 0:
            response = videos[-1]
        else:
            response = "sorry, couldnt find any videos for %s" % query
    elif command == "echo":
        response = " ".join(details)
    elif command == "pipe":
        pipe(command, details, channel)
    else:
        """
          see if a randomly entered command is something that was previously learned
        """
        learner = Learner()
        response = learner.get(command)
    
    if response and respond:
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
    elif not respond:
        return response


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message 
        starts with ?.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and output['text'].startswith("?"):
                cleaned = output['text'].strip().split()
                command = cleaned[0][1:]

                if len(cleaned) > 1:
                    details = cleaned[1:]
                else:
                    details = None

                return command, details, output['channel']

    return None, None, None


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s',
                        stream=sys.stdout,
                        level=logging.DEBUG)
    sqlite = SqliteStore()
    
    if slack_client.rtm_connect():
        logging.info("StarterBot connected and running!")
        while True:
            content = slack_client.rtm_read()
            """          
            if content and len(content) > 0:
                for output in content:
                    if output and 'text' in output:
                        sqlite.log_content(json.dumps(output))
            """
            command, details, channel = parse_slack_output(content)

            if command and channel:
                handle_command(command, details, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        logging.error("Connection failed. Invalid Slack token or bot ID?")

