from sqlite_store import SqliteStore
import datetime
from dateutil.relativedelta import relativedelta
import logging

class Plusser():
    def __init__(self):
        self.sqlite = SqliteStore()

    def plus(self, name, reason = ""):
        count = self.sqlite.increment_plusses(name.lower(), reason)
        logging.info("a plus for %s")
        if count == 1:
            return "a plus for %s!" % name
        else:
            return "another plus for %s! %s total" % (name, count)

    def get(self, name):
        count = self.sqlite.get_plusses(name.lower())

        if count == 0:
            return "no plusses just yet for %s" % name
        else:
            return "%s has %s plusses!" % (name, count)

    def leader_board(self, min_time=0, max_time=9999999999999999, limit=20):
        leaders = self.sqlite.plus_leaders(min_time, max_time, limit=20)
        return "plus leaderboard:\n" + "\n".join([": ".join([str(y) for y in x]) for x in leaders])

    def monthly_leader_board(self, months_ago=0):
        today = datetime.date.today()
        start_time = datetime.date(today.year, today.month, 1) - relativedelta(months=abs(int(months_ago)))
        end_time = start_time + relativedelta(months=+1)
        logging.debug("finding plusses for %s to %s" % (start_time, end_time))
        
        return self.leader_board(start_time.strftime("%s"), end_time.strftime("%s"))
