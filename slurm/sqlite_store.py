import sqlite3
import logging
from config import config
import sys
import json


"""
  schemas used
"""
class Schema:
    def __init__(self, name, fields, trigger_logic = []):
        self.name = name
        self.fields = fields
        self.field_names = [x.split()[0] for x in fields]
        self.trigger_logic = trigger_logic

    def getName(self):
        return self.name

    def getFields(self):
        return self.fields

    def getFieldNames(self):
        return self.field_names

    def getTriggers(self):
        return self.trigger_logic

class Plusses(Schema):
    name = "pluses_monthly"
    fields = ["name TEXT",
              "reason TEXT",
              "timestamp INT"]

    def __init__(self):
        Schema.__init__(self, Plusses.name, Plusses.fields)

class Learn(Schema):
    name = "learn"
    fields = ["command TEXT",
              "content TEXT"]

    def __init__(self):
        Schema.__init__(self, Learn.name, Learn.fields)


class SqliteStore():
    def __init__(self):
        self.con = None

        self.learn = self.setupTable(Learn())
        self.plusses = self.setupTable(Plusses())

        self.tables = {
            'learn':self.learn,
            'plusses':self.plusses
        }

    def get_connection(self):
        if not self.con:
            self.con = sqlite3.connect(config['sqlite_db']['dir'])
        return self.con

    def setupTable(self, schema):
        con = self.get_connection()
        try: 
            logging.info("creating table %s" % schema.getName())
            create = """CREATE TABLE IF NOT EXISTS %s (%s)""" % (schema.getName(), ", ".join(schema.getFields()))
            logging.info(create)
            con.execute(create)
            for trigger in schema.getTriggers():
                logging.info("creating trigger %s" % trigger)
                con.execute(trigger)
            con.commit()
        except sqlite3.Error, e:
            logging.error("error crating table %s, %s" % (schema.getName(), e))
            sys.exit(1)

        return schema

    def setupTables(self):
        for table in self.tables.values():
            self.setupTable(table)

    def cleanup_table(self, schema):
        con = self.get_connection()
        logging.info("deleting table %s" % (schema.getName()))
        con.execute("DELETE * FROM " + schema.getName())
        con.commit()

    def clear_tables(self):
        for table in self.tables.values():
            self.cleanup_table(table)


    """
      learn commands
    """

    def learn_command(self, command, content):
        con = self.get_connection()
        todo = "INSERT INTO %s (command, content) VALUES ('%s',  '%s')" % (self.learn.getName(), command, content)
        logging.debug(todo)
        con.execute(todo)
        con.commit()

    def get_commands(self, command):
        con = self.get_connection()
        todo = "SELECT content FROM %s WHERE command='%s'" % (self.learn.getName(), command)
        logging.debug(todo)
        cur = con.execute(todo)
        con.commit()
        return [x[0] for x in cur.fetchall()]

    def unlearn(self, command):
        con = self.get_connection()
        todo = "DELETE FROM %s WHERE command='%s'" % (self.learn.getName(), command)
        logging.debug(todo)
        con.execute(todo)
        con.commit()

    def unlearn2(command, content):
        con = self.get_connection()
        todo = "DELETE FROM %s WHERE command = '%s' AND content = '%s'" % (self.learn.getName(), command, content)
        logging.debug(todo)
        con.execute(todo)
        con.commit()


    """
      plusses commands
    """
    def increment_plusses(self, name, reason=None):
        con = self.get_connection()
        if not reason:
            reason = "NONE"
        # insert new plus to table
        todo = "INSERT INTO {} (name, reason, timestamp) VALUES ('{}', '{}', strftime('%s', 'now'))".format(self.plusses.getName(), name, reason)
        logging.debug(todo)
        con.execute(todo)
        con.commit()
        
        todo = "SELECT count(*) FROM %s WHERE name='%s'" % (self.plusses.getName(), name)
        logging.debug(todo)

        cur = con.execute(todo)
        prior = cur.fetchall()
        count = prior[0][0]
        return count
        
    def get_plusses(self, name, min_time=0):
        con = self.get_connection()
        todo = "SELECT count(*) FROM %s WHERE name='%s' AND timestamp>%s" % (self.plusses.getName(), name, min_time)

        logging.debug(todo)
        cur = con.execute(todo)
        con.commit()

        data = cur.fetchall()
        if len(data) == 0:
            return 0
        else:
            return data[0][0]

    def plus_leaders(self, min_time=0, max_time=999999999999999, limit=20):
        con = self.get_connection()
        todo = "SELECT name, count FROM (SELECT name, count(*) AS  count FROM %s WHERE timestamp > %s GROUP BY name) c  ORDER BY count DESC LIMIT %s" % (self.plusses.getName(), min_time, limit)

        logging.debug(todo)
        cur = con.execute(todo)
        con.commit()

        return [(x[0], x[1]) for x in cur.fetchall()]
