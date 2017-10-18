from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from post import Post
from flask import Flask, abort, flash

class Postlist:
    def __init__(self):
        self.posts = {}
        self.last_key = 0

    def getid(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        usernum=cursor.fetchone()
        usernum = 1
        return usernum

    def getownerid(self, postid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT USERID FROM POSTS WHERE POSTID=%s""", (postid,))
        owner = cursor.fetchone()
        owner = 1
        return owner

    def add_post(self, post):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""INSERT INTO POSTS (USERID, TITLE, CONTEXT)    VALUES    (%s, %s, %s)""", (userid, post.title, post.context))
        connection.commit()
        connection.close()

    def delete_post(self, postid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM POSTS WHERE POSTID=%s""", [postid],)
        connection.commit()
        connection.close()

    def update_post(self, postid, post):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""UPDATE POSTS SET TITLE=%s, CONTEXT=%s WHERE POSTID=%s""", (post.title, post.context, postid))
        connection.commit()
        connection.close()

    def get_post(self, postid):##get one post
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        id_post = [postid]
        cursor.execute("""SELECT posts.title,
                        posts.context,
                        posts.postid,
                        users.username,
                        posts.numberoflikes
                        FROM posts
                        RIGHT JOIN users ON users.id = posts.userid
                        WHERE posts.postid = %s""", id_post,)
        title, context, postid, userhandle, numberoflikes = cursor.fetchone()
        posts=Post(title, context, postid, userhandle, numberoflikes)
        return posts

    def get_posts(self):##get all posts
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT posts.title,
                        posts.context,
                        posts.postid,
                        users.username,
                        posts.numberoflikes
                        FROM posts
                        RIGHT JOIN users ON users.id = posts.userid
                        ORDER BY POSTID DESC""")
        post = [(Post(title, context, postid, userhandle, numberoflikes))
                    for title, context, postid, userhandle, numberoflikes  in cursor]
        return post
