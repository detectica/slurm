from sqlite_store import SqliteStore


class Plusser():
    def __init__(self):
        self.sqlite = SqliteStore()

    def plus(self, name, reason = ""):
        count = self.sqlite.increment_plusses(name, reason)
        if count == 1:
            return "a plus for %s!" % name
        else:
            return "another plus for %s! %s total" % (name, count)

    def get(self, name):
        count = self.sqlite.get_plusses(name)

        if count == 0:
            return "no plusses just yet for %s" % name
        else:
            return "%s has %s plusses!" % (name, count)
