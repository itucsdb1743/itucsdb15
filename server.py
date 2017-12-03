import datetime
import os
import json
import re
import psycopg2 as dbapi2
import math
import time

from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_login import LoginManager
from flask_login import current_user, login_required, login_user, logout_user
from passlib.apps import custom_app_context as pwd_context
from flask import current_app, request
from postlist import *
from buglist import *
from bug import *
from post import *
from forms import *
from user import *
from poll import Poll
from listofpolls import ListOfPolls

lm = LoginManager()
app = Flask(__name__)

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
            dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)

def create_app():
    app.config.from_object('settings')

    app.Postlist = Postlist()
    app.Buglist = Buglist()

    lm.init_app(app)
    lm.login_view='login_page'

    return app

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form=LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        user = get_user(username)
        if user is not None:
            password = form.password.data
            if pwd_context.verify(password, user.password):
                login_user(user)
                try:
                    with dbapi2.connect(app.config['dsn']) as connection:
                        with connection.cursor() as cursor:
                            cursor.execute("""SELECT * FROM USERS WHERE ID=1""")
                except:
                    return redirect(url_for('initialize_database'))
                flash('You have logged in.')
                next_page = request.args.get('next', url_for('post_page'))
                return redirect(next_page)
        flash('Invalid credentials.')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = pwd_context.encrypt(form.password.data)
        refcode = request.form['refcode']
        connection=dbapi2.connect(current_app.config['dsn'])
        cursor=connection.cursor()
        cursor.execute("""SELECT REC FROM REFCODE WHERE REFC=%s""", (refcode,))
        if cursor.rowcount==0:
            flash('No Referance Code')
            return render_template('register.html', form=form)

        try:
            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO USERS (USERNAME, PASSWORD) VALUES (%s, %s)""", (username, password))

            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    userid = get_userid(username)
                    cursor.execute("""INSERT INTO USERPROFILE (ID, NICKNAME, USERNAME, BIO) VALUES(%s, %s, %s, %s)""", (userid, username, username, 'bio'))
                    cursor.execute("""INSERT INTO USERINFO (USERID, NAME, SURNAME, NICKNAME, EMAIL, LANGUAGE) VALUES(%s, %s, %s, %s, %s, %s)""",
                                   (userid, '', '', '', '', ''))
                    cursor.execute("""INSERT INTO POINTS (USERID) VALUES(%s)""", (userid,))
                    user=get_user(username)
                    login_user(user)
                    return redirect(url_for('post_page'))
        except:
            flash('Username is already taken')

    return render_template('register.html', form=form)

@app.route('/bugreport', methods=['GET', 'POST'])
@login_required
def bugs_page():
    
    if request.method == 'GET':
        usrid=current_app.Buglist.getid()
        adminid=current_app.Buglist.getadmin()

        if usrid==adminid:
            bugs = current_app.Buglist.get_bugs()
            return render_template('bugspageadmin.html', bugs=bugs)

        else:
            return render_template('bugspageusr.html')

    else:
        bugid = 0
        bugcs = request.form['bugcs']
        usrid=current_app.Buglist.getid()
        focus = 0
        fixed = 0
        bug = Bug(bugid, bugcs, usrid, focus, fixed)
        current_app.Buglist.add_bug(bug)
        flash("Thanks For Helping Us")
        flash("Your Report Is Added To Our Issues Que")
        return redirect(url_for('bugs_page'))

@app.route('/bug/<int:bug_id>', methods=['GET', 'POST'])
@login_required
def bug_page(bug_id):
    bugid=bug_id
    usrid=current_app.Buglist.getid()
    adminid=current_app.Buglist.getadmin()

    if request.method == 'GET':

        if usrid==adminid:
            bugs = current_app.Buglist.get_bug(bugid)
            return render_template('bugpage.html', bug=bugs)

        else:
            return redirect(url_for('bugs_page'))

    else:
        postres=request.form['submit']

        if postres == 'delete':
            current_app.Buglist.delete_bug(bugid)

        elif postres == 'setfocus':
            current_app.Buglist.set_focus(bugid)

        elif postres == 'defocus':
            current_app.Buglist.defocus(bugid)

        elif postres == 'setfixed':
            current_app.Buglist.setfixed(bugid)

        return redirect(url_for('bug_page', bug_id=bugid))

@app.route('/polls',methods=['GET','POST'])
def polls_page():

    if request.method=='POST':
        if request.form['submit']=='add':
            pollquestion=request.form['pollname']
            app.polls=ListOfPolls('polls')
            temppoll=Poll(pollquestion,current_user.username)
            app.polls.addPoll(temppoll)
            polllist=app.polls.getAllPolls()

        return redirect(url_for('polls_page'))

    else:

        app.polls=ListOfPolls('polls')
        polllist=app.polls.getAllPolls()

        if current_user.is_authenticated:
            return render_template('polls.html',polllist=polllist)
        else:
            return render_template('polls_wo_login.html',polllist=polllist)

@app.route('/poll/<string:creatorname>/<string:pollquestion>',methods=['GET','POST'])
def poll_page(pollquestion,creatorname):
    user="admin"
    if request.method=='POST':
        if request.form['submit']=='update':
            current_app.tempPollList=ListOfPolls('temp')
            poll=current_app.tempPollList.getPoll(pollquestion,creatorname)
            newquestion=request.form['choiceorquestion']
            poll.updateQuestion(newquestion)
            choices=poll.getChoices()
            isVoted=poll.isVoted(user)
            return redirect(url_for('poll_page',pollquestion=newquestion,creatorname=creatorname))
        elif request.form['submit']=='delete':
            app.polls=ListOfPolls('polls')
            polllist=app.polls.getAllPolls()
            app.polls.deletePoll(pollquestion,creatorname)
            return redirect(url_for('polls_page'))
        elif request.form['submit']=='addchoice':
            current_app.tempPollList=ListOfPolls('temp')
            poll=current_app.tempPollList.getPoll(pollquestion,creatorname)
            choiceinfo=request.form['choiceorquestion']
            poll.addChoice(choiceinfo)
            choices=poll.getChoices()
            isVoted=poll.isVoted(user)
        elif request.form['submit']=='vote':
            current_app.tempPollList=ListOfPolls('temp')
            poll=current_app.tempPollList.getPoll(pollquestion,creatorname)
            choiceContent=request.form['answer']
            poll.voteforPoll(choiceContent)
            choices=poll.getChoices()
            isVoted=poll.isVoted(user)


        return redirect(url_for('poll_page',pollquestion=pollquestion,creatorname=creatorname))



    else:
        current_app.templist=ListOfPolls('temp')
        poll=current_app.templist.getPoll(pollquestion,creatorname)
        choices=poll.getChoices()
        isVoted=poll.isVoted(user)
        counter=0
        if(current_user.is_authenticated):
            if (creatorname==current_user.username):
                return render_template('pollownerperspective.html',pollquestion=pollquestion,choices=choices,isVoted=isVoted,counter=counter)
        else:
            return render_template('pollvoterperspective.html',pollquestion=pollquestion,choices=choices,isVoted=isVoted,counter=counter)

@app.route('/post', methods=['GET', 'POST'])
def post_page():
    if request.method == 'GET':
        now = datetime.datetime.now()
        posts = current_app.Postlist.get_posts()
        print(request.environ['REMOTE_ADDR'])

        if current_user.is_authenticated:
            return render_template('posts.html', posts=posts)
        else:
            return render_template('posts_wo_login.html', posts=posts)
    else:
        title = request.form['title']
        content = request.form['content']
        postid=0
        userh="NONE"
        numlike=0
        post = Post(title, content, postid, userh, numlike)
        current_app.Postlist.add_post(post)
        return redirect(url_for('post_page'))

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def posts_page(post_id):
    id_post=post_id
    holderid=current_app.Postlist.getownerid(post_id)
    post = current_app.Postlist.get_post(post_id)

    if current_user.is_authenticated:

        cduserid=current_app.Postlist.getid()
        guest=0;
        if holderid == cduserid:
            guest=0;
        else:
            guest=1;
            return render_template('post_wo_login.html', posts=post)

        if request.method == 'GET':
            if post==None:
                return(redirect(url_for('error_page')))

            return render_template('post.html', posts=post)
        else:

            if request.form['submit'] == 'delete':
                current_app.Postlist.delete_post(id_post)
                return redirect(url_for('post_page'))

            elif request.form['submit'] == 'update':
                title=request.form['title']
                context=request.form['context']
                post = current_app.Postlist.get_post(post_id)
                if title == '':#change this so it will keep its original for if left blank
                    title = post.title

                if context == '':
                   context = post.context


                numlike=post.numberoflikes
                posts = post(title, context, id_post, current_user.username, numlike)
                current_app.Postlist.update_post(id_post, posts)
                return redirect(url_for('posts_page', post_id=id_post))
    else:
        return render_template('post_wo_login.html', posts=post)


@app.route('/')
def home_page():
   return redirect(url_for('post_page'))

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have logged out.')
    return redirect(url_for('post_page'))

def main():
    app = create_app()
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant' host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)

@app.route('/initdb')
def initialize_database():
   # if not current_user.is_admin:
    #    abort(401)
    with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute(open("script.sql", "r").read())
    time.sleep(3)
    return redirect(url_for('post_page'))

if __name__ == '__main__':
    main()
