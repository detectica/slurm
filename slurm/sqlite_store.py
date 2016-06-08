import sqlite3
import logging
from config import config
import sys


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

        self.tables = {'learn':self.learn}

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
        logging.debur(todo)
        con.execute(todo)
        con.commit()
