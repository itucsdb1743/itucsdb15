from flask import current_app
import psycopg2 as dbapi2
from flask_login import current_user
from poll import Poll

class ListOfPolls:
    def __init__(self,name):
        self.name=name
        return
    def addPoll(self,poll):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        username=current_user.username
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(username,))
        temp=cursor.fetchone()
        userid=temp[0]
        cursor.execute("""INSERT INTO POLLS (POLLQUESTION,CREATORID) VALUES (%s, %s)""", (poll.question,userid))
        connection.commit()
        cursor.close()
        connection.close()
        return

    def deletePoll(self,pollquestion,pollcreatorname):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(pollcreatorname,))
        temp=cursor.fetchone()
        creatorid=temp[0]
        cursor.execute("""DELETE FROM POLLS WHERE POLLQUESTION=%s AND CREATORID=%s """,(pollquestion,creatorid))
        connection.commit()
        cursor.close()
        connection.close()
        return

    def getPoll(self,pollquestion,creatorname):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""",(creatorname,))
        temp=cursor.fetchone()
        creatorid=temp
        cursor.execute("""SELECT VOTENUMBER,CHOICENUMBER FROM POLLS WHERE POLLQUESTION=%s AND CREATORID=%s""",(pollquestion,creatorid))
        poll=Poll(pollquestion,creatorname)
        array=[(temp2[0],temp2[1]) for temp2 in cursor]
        for votenumber,choicenumber in array:
            poll.votenumber=votenumber
            poll.choicenumber=choicenumber
        cursor.close()
        connection.close()
        return poll

    def getAPoll(self,pollquestion):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT VOTENUMBER,CHOICENUMBER FROM POLLS WHERE POLLQUESTION=%s""",(pollquestion,))
        temp2=cursor.fetchone()
        votenumber=temp2[0]
        choicenumber=temp2[1]
        poll=Poll(pollquestion,creatorname)
        poll.votenumber=votenumber
        poll.choicenumber=choicenumber
        return poll


    def updateQuestionOfAPoll(self,pollquestion,newquestion):
        poll=Poll(pollquestion,current_user.username)
        poll.updateQuestion(newquestion)
        return

    def getAllPolls(self):
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT POLLQUESTION,USERNAME FROM POLLS JOIN USERS ON USERS.ID=POLLS.CREATORID ORDER BY POLLID""")
        polls=[(temp[0],temp[1]) for temp in cursor]
        connection.commit()
        cursor.close()
        connection.close()
        return polls

