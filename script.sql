CREATE TABLE USERS(
	ID SERIAL PRIMARY KEY,
	USERNAME VARCHAR(20) UNIQUE NOT NULL,
	PASSWORD VARCHAR(150),
	JDATE DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE USERPROFILE(
	ID INTEGER PRIMARY KEY REFERENCES USERS ON DELETE CASCADE,
	USERNAME VARCHAR(20) UNIQUE NOT NULL,
	NICKNAME VARCHAR(20) NOT NULL,
	POSTS INTEGER DEFAULT 0,
	FOLLOWING INTEGER DEFAULT 0,
	FOLLOWERS INTEGER DEFAULT 0,
	LIKES INTEGER DEFAULT 0,
	BIO VARCHAR(100)
);

CREATE TABLE BUGS(
	USERID INTEGER REFERENCES USERS ON DELETE CASCADE,
	BUGID SERIAL PRIMARY KEY,
	BUGCAUSE VARCHAR(80) NOT NULL,
	FOCUS INTEGER DEFAULT 0,
	FIXED INTEGER DEFAULT 0
);

CREATE TABLE POSTS(
	POSTID SERIAL PRIMARY KEY NOT NULL,
	USERID INTEGER REFERENCES USERS(ID) ON DELETE CASCADE,
	TITLE VARCHAR(20) NOT NULL,
	CONTEXT VARCHAR(600) NOT NULL,
	PTIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	NUMBEROFLIKES INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE USERINFO(
	USERID INTEGER PRIMARY KEY NOT NULL REFERENCES USERS (ID) ON DELETE CASCADE,
	NAME VARCHAR(20) NOT NULL,
	SURNAME VARCHAR(20) NOT NULL,
	NICKNAME VARCHAR(20) NOT NULL,
	EMAIL VARCHAR(25) NOT NULL,
	LANGUAGE VARCHAR(20) NOT NULL
);

CREATE TABLE LIKES(
	USERID INTEGER NOT NULL REFERENCES USERPROFILE(ID) ON DELETE CASCADE,
	POSTID INTEGER NOT NULL REFERENCES POSTS(POSTID) ON DELETE CASCADE,
	PRIMARY KEY(USERID,POSTID),
	LikeTIME TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE POLLS(
	POLLID SERIAL PRIMARY KEY,
	CREATORID INTEGER NOT NULL REFERENCES USERPROFILE(ID) ON DELETE CASCADE,
	VOTENUMBER INTEGER NOT NULL DEFAULT 0,
	CHOICENUMBER INTEGER NOT NULL DEFAULT 0,
	POLLQUESTION VARCHAR(40) NOT NULL
);

CREATE TABLE CHOICES(
	CHOICEID SERIAL UNIQUE,
	POLLID INTEGER NOT NULL REFERENCES POLLS(POLLID) ON DELETE CASCADE,
	CONTENT VARCHAR(20) NOT NULL,
	NUMBEROFVOTES INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY (CHOICEID,POLLID,CONTENT)
);
CREATE TABLE VOTES(
	POLLID INTEGER NOT NULL REFERENCES POLLS(POLLID) ON DELETE CASCADE,
	CHOICEID INTEGER NOT NULL REFERENCES CHOICES(CHOICEID) ON DELETE CASCADE,
	USERID INTEGER NOT NULL REFERENCES USERPROFILE(ID) ON DELETE CASCADE,
	PRIMARY KEY(POLLID,CHOICEID,USERID)
);

INSERT INTO USERS (USERNAME, PASSWORD) VALUES(
	'admin',
	'$6$rounds=603422$ZgQRx3Mm/YuUaION$b/Vwzuno1Q7e1KPWehLbRdmvdf/Bjj5.4a.fvcz3TNCl.Rn2CLbQPCsGSIBarDYHMzq3jjN8KDLkBtKJzBclf0'
);

INSERT INTO USERPROFILE (ID, NICKNAME, USERNAME, BIO) VALUES(
	1,
	'admin',
	'admin',
	'Istanbul'
);

INSERT INTO POSTS (USERID, TITLE, CONTEXT) VALUES(
	1,
	'Admin POST',
	'First Post By Admins'
);

INSERT INTO BUGS (USERID, BUGCAUSE) VALUES(
	1,
	'Empty Table Give Errors'
);


INSERT INTO USERINFO (USERID, NAME, SURNAME, NICKNAME, EMAIL, LANGUAGE) VALUES(
	1,
	'admin',
	'admin',
	'admin',
	'admin@inferno.com',
	'English'
);