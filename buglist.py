from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from bug import *

class Buglist:
    def __init__(self):
        self.bugs = {}
        self.last_key = 0

    def getid(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        usernum=cursor.fetchone()
        print(usernum)
        return usernum

    def getadmin(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        name='admin'
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (name,))
        usernum=cursor.fetchone()
        return usernum

    def get_bug(self, bugid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT
                        bugs.bugid,
                        bugs.bugcause,
                        users.username,
                        bugs.focus,
                        bugs.fixed
                        FROM BUGS
                        LEFT JOIN users ON users.id = bugs.userid
                        WHERE bugs.bugid=%s""", (bugid,))
        bugid, bugcause, username, focus, fixed=cursor.fetchone()
        bugs=Bug(bugid, bugcause, username, focus, fixed)
        return bugs

    def get_bugs(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT
                        bugs.bugid,
                        bugs.bugcause,
                        users.username,
                        bugs.focus,
                        bugs.fixed
                        FROM BUGS
                        LEFT JOIN users ON users.id = bugs.userid
                        ORDER BY focus DESC, bugs.bugid DESC """)
        bugs = [(Bug(bugid, bugcause, username, focus, fixed))
                    for bugid, bugcause, username, focus, fixed  in cursor]
        print(bugs)
        return bugs

    def get_bug_user(self, userid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT
                        bugs.bugid,
                        bugs.bugcause,
                        users.username,
                        bugs.focus,
                        bugs.fixed
                        FROM bugs
                        RIGHT JOIN users ON users.id = bugs.userid
                        WHERE bugs.userid=%s
                        ORDER BY bugs.bugid DESC, bugs.focus DESC""", (userid,))

        if cursor.rowcount==0:
            bug = Bug(99, 'No Report', 'admin', 0, 0)
            return bug

        bug = [(Bug(bugid, bugcause, username, focus, fixed))
                    for bugid, bugcause, username, focus, fixed  in cursor]
        return bug

    def add_bug(self, bug):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO BUGS (bugcause, userid)
        VALUES    (%s, %s)""",  (bug.bugcause, bug.userid))
        connection.commit()
        connection.close()

    def set_focus(self, bugid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE BUGS SET FOCUS=%s WHERE bugid=%s""", (1, bugid))
        connection.commit()
        connection.close()

    def defocus(self, bugid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE BUGS SET FOCUS=%s WHERE bugid=%s""", (0, bugid))
        connection.commit()
        connection.close()

    def getfocus(self, bugid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT FOCUS FROM BUGS WHERE bugid=%s""", (bugid,))
        focus=cursor.fetchone()
        return focus

    def setfixed(self, bugid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE BUGS SET FIXED=%s WHERE bugid=%s""", (1, bugid))
        connection.commit()
        connection.close()

    def getfixed(self, bugid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT FIXED FROM BUGS WHERE bugid=%s""", (bugid,))
        fixed=cursor.fetchone()
        return fixed

    def delete_bug(self, bugid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM BUGS WHERE bugid=%s""", (bugid,))
        connection.commit()
        connection.close()
