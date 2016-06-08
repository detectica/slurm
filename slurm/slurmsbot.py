import os
import time
from slackclient import SlackClient
import sqlite3
import logging
import sys

from learner import Learner
from plusser import Plusser

"""
  looks for commands that start with ?
"""


# starterbot's ID as an environment variable
BOT_ID = str(os.environ.get("BOT_ID"))


# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"


# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, details, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    if command == "learn":
        learner = Learner()
        response = learner.learn(details[0], " ".join(details[1:]))
    elif command == "unlearn":
        learner = Learner()
        content = None
        if len(details) > 1:
            content = " ".join(details[1:])
    
        response = learner.unlearn(details[0], content)

    elif command == "++" or command == "endorse":
        plusser = Plusser()
        reason = ""
        if len(details) > 1:
            reason = " ".join(details[1:])

        response = plusser.plus(details[0], reason)
    elif command == "plusses":
        plusser = Plusser()
        response = plusser.get(details[0])

    else:
        """
          see if a randomly entered command is something that was previously learned
        """
        learner = Learner()
        response = learner.get(command)
    
    if response:
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and output['text'].startswith("?"):
                # return text after the @ mention, whitespace removed
                cleaned = output['text'].strip().lower().split()
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
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        logging.info("StarterBot connected and running!")
        while True:
            command, details, channel = parse_slack_output(slack_client.rtm_read())

            if command and channel:
                handle_command(command, details, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        logging.error("Connection failed. Invalid Slack token or bot ID?")

