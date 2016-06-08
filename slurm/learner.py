from sqlite_store import SqliteStore
import random

class Learner():
    def __init__(self):
        self.sqlite = SqliteStore()

    def learn(self, command, content):
        self.sqlite.learn_command(command, content)
        return "ok, learned %s" % command

    def get(self, command):
        contents = self.sqlite.get_commands(command)
        if contents:
            return random.choice(contents)
        else:
            return None

    def unlearn(self, command, content = None):
        if content:
            self.sqlite.unlearn2(command, content)
            return "forgotten!"
        else:
            self.sqlite.unlearn(command)
            return "%s? what's %s?" % (command, command)
    
