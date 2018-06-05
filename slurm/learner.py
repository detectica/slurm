from sqlite_store import SqliteStore
import random

class Learner():
    def __init__(self):
        self.sqlite = SqliteStore()

    def learn(self, command, content):
        self.sqlite.learn_command(command, content.replace("'", "''"))
        return "ok, learned %s" % command

    def list_commands(self):
        contents = self.sqlite.get_all_commands()
        if contents:
            return "these are the commands I know:\n%s" % "\n".join(contents)
        else:
            return None

    def list(self, command):
        contents = self.sqlite.get_commands(command)
        if contents:
            return "Ok, here's %s:\n%s" % (command, "\n".join(["(%s) %s" % (j+1, k) for j,k in zip(range(len(contents)), contents)]))
        else:
            return None
        
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
    
