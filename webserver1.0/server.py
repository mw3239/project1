#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Columbia W4111 Intro to databases
Project 1: Real World Database Application
- Michael Wiley, James Wong
- Japanese Learning Application

To run locally

    python server.py

Go to http://localhost:8111 in your browser

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, session, abort, flash
from statistics import mean
from datetime import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail

DB_USER = "mw3239"
DB_PASSWORD = "vfd41n26"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

# This line creates a database engine that knows how to connect to the URI above

engine = create_engine(DATABASEURI)

# Here we create a test table and insert some values in it

engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
	id serial,
	name text
	);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

@app.before_request
def before_request():
     """
     This function is run at the beginning of every web request
     (every time you enter an address in the web browser).
     We use it to setup a database connection that can be used throughout the request

     The variable g is globally accessible
     """
     try:
         g.conn = engine.connect()
     except:
         print "uh oh, problem connecting to database"
         import traceback; traceback.print_exc()
         g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass

# Web Application
# Home Page
@app.route("/")
def home():
    # DEBUG: this is debugging code to see what request looks like
    print request.args
    return render_template("index.html")

# Global Variables
maxkanji = ''
maxcountk = 0
maxword = ''
maxcountw = 0
readlvl = 0
rarest_char = ""
rarest_rank = 0
diff_kanji = ""
diff_strokes = 0
maxpos = ""

username = ""
url = ""

# Reset global variables
def reset():
    global maxkanji, maxcountk, maxword, maxcountw, readlvl, rarest_char, rarest_rank, diff_kanji, diff_strokes, maxpos, url
    maxkanji = ''
    maxcountk = 0
    maxword = ''
    maxcountw = 0
    readlvl = 0
    rarest_char = ""
    rarest_rank = 0
    diff_kanji = ""
    diff_strokes = 0
    maxpos = ""
    url = ""

# Search Functionality
@app.route("/send", methods=['GET', 'POST'])
def send():
    global maxkanji, maxcountk, maxword, maxcountw, readlvl, rarest_char, rarest_rank, diff_kanji, diff_strokes, maxpos, username, url
    # reset global variables
    reset()  
    # Check search request and its length
    if request.method == 'POST' and len(request.form['url']) != 0:
        url = request.form['url']	

	# If a user is logged in, add search request to search history
	if len(username) != 0:
		uidcursor = g.conn.execute("SELECT user_id FROM accounts WHERE username = '" + username + "'")
		user_id = 0
		for result in uidcursor:
			user_id = result['user_id']
		uidcursor.close()
		insert = "INSERT INTO history(user_id, search) VALUES ("+str(user_id)+", '"+url.encode('utf-8')+"')"
		g.conn.execute(insert)	

	# Search for Kanji Characters
	kanji_headers = ['Character', 'Strokes', 'Grade', 'jlpt', 'reading', 'translation', 'freq', 'rank']
	kanji_headers = [s + ": " for s in kanji_headers]
	kanji = []	
	encounteredk = []
	enclvl = []
	for i in range(len(url)):
		cursor = g.conn.execute("SELECT * FROM kanji WHERE character = '" + url[i] + "'")
	       	character = []

		# Define a list here that will contain all kanji already seen
	        for result in cursor:
        		character.append(result['character'])
			character.append(result['strokes'])
			character.append(result['grade'])
			character.append(result['jlpt'])
			character.append(result['reading'])
			character.append(result['translation'])
			character.append(result['freq'])
			character.append(result['rank'])
			encounteredk.append(result['character'])
			enclvl.append(result['jlpt'])
		cursor.close()

			# Check if the number of number of times that the character is in the list is 1
		if len(character) != 0 and encounteredk.count(character[0]) == 1:
			kanji.append(character)
	
	# Search for Words
	dict_headers = ['Word', 'Reading', 'Definition', 'jlpt', 'Pos']
	dict_headers = [s + ": " for s in dict_headers]

	wordlist = g.conn.execute("SELECT word FROM dictionary")

	dictionary = []	
	encounteredw = []
	encpos = []
	for entry in wordlist:
		if entry['word'] in url:
			cursor2 = g.conn.execute("SELECT * FROM dictionary WHERE word = '" + entry['word'] + "'")
			word = []
			for result in cursor2:
				word.append(result['word'])
				word.append(result['reading'])
				word.append(result['def'])
				word.append(result['jlpt'])
				word.append(result['pos'])
				encounteredw.append(result['word'])
				encpos.append(result['pos'])
			cursor2.close()
			if encounteredw.count(word[0]) == 1:
				dictionary.append(word)

	# If no kanji characters were found return input
	if len(encounteredk) == 0 and len(encounteredw) == 0:
        	return render_template('index.html', input=url)
	

	# Find rarest kanji character
	rarest_query = "SELECT character, rank FROM kanji WHERE character IN ('" +  "', '".join(encounteredk) + "') ORDER BY rank DESC LIMIT 1"
	rarest = g.conn.execute(rarest_query)
	for result in rarest:
		rarest_char = result['character']
		rarest_rank = result['rank']
	rarest.close()	
	
	# Most difficult to write kanji
	diff_query = "SELECT character, strokes FROM kanji WHERE character IN ('" + "', '".join(encounteredk) + "') ORDER BY strokes DESC LIMIT 1"
	diff = g.conn.execute(diff_query)
	for result in diff:
		diff_kanji = result['character']
		diff_strokes = result['strokes']
	diff.close()
	
	if len(encounteredk) != 0:	
		maxkanji = max(set(encounteredk), key=encounteredk.count)
		enclvl = [int(x) for x in enclvl]
		readlvl = round(mean(enclvl))
	maxcountk = encounteredk.count(maxkanji)
	if len(encounteredw) != 0:
		maxword = max(set(encounteredw), key=encounteredw.count)
		maxcountw = encounteredw.count(maxword)
		maxpos = max(set(encpos),key=encpos.count)

        return render_template('index.html', input=url, kanji_headers=kanji_headers, kanji=kanji, dict_headers=dict_headers, dictionary=dictionary, zip=zip)

    else:
    	return render_template('index.html')

# About Page
@app.route("/about")
def about():
    return render_template('about.html', title='About')

# Analysis Page
@app.route("/analysis")
def analysis():
    global maxkanji, maxcountk, maxword, maxcountw, readlvl, rarest_char, rarest_rank, diff_kanji, diff_stroke, maxpos
    
    return render_template('analysis.html', title='Analysis', maxkanji = maxkanji, maxcountk = maxcountk, maxword = maxword, maxcountw = maxcountw, readlvl = readlvl, rarest_char = rarest_char, rarest_rank = rarest_rank, diff_kanji = diff_kanji, diff_strokes = diff_strokes, maxpos = maxpos)

# Accounts Page
@app.route("/accounts")
def accounts():
    global username, url
    # Check if user is logged in
    if len(username) != 0:
	# Get userid from username
	uidcursor = g.conn.execute("SELECT user_id FROM accounts WHERE username = '" + username + "'")
	uid = 0
	for result in uidcursor:
		uid = result['user_id']
	uidcursor.close()
	# Get search history
	cursor = g.conn.execute("SELECT search FROM history WHERE user_id =" + str(uid))
	history = []
	for result in cursor:
		history.append(result['search'])
	cursor.close()
	return render_template('accounts.html', title='Accounts', history=history, enumerate=enumerate)

    else:
    	return render_template('accounts.html', title='Accounts')

# Register Page
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
	try:
    		# Get max user id
		username = request.form['username']
		cursor = g.conn.execute("SELECT user_id FROM accounts ORDER BY user_id DESC LIMIT 1 OFFSET 2")
		max_uid = 0
		for result in cursor:
			max_uid = result['user_id']
		cursor.close()
		max_uid += 1
	
		# Add new user to accounts
		cmd = "INSERT INTO accounts(user_id, username) VALUES (" + str(max_uid) + ", '" + username + "')"
    		g.conn.execute(cmd)
	except:
		return render_template('register.html', title='Register', fail='An error occurred, possibily because username is already in use.')
	return render_template('register.html', title='Register', fail='Successfully registered user account.')
    else:
	return render_template('register.html', title='Register')

# Comments Page
@app.route("/comments", methods=[ 'GET', 'POST' ])
def comments():
    global username
    
    # Look up all existing comments
    cursor = g.conn.execute("SELECT cid, text, date, username FROM comments, accounts WHERE user_id = uid ORDER BY date DESC, cid DESC")
    comments = []
    dates = []
    usernames = []
    for result in cursor:
	comments.append(result['text'])
	dates.append(result['date'])
	usernames.append(result['username'])
    cursor.close()
   
    # Check if new comment was submitted 
    if request.method == 'POST':
	text = request.form['comment']
	# Return if comment is empty
	if len(text) == 0:
		return render_template('comments.html', title='Comments', fail="You can't submit an empty comment.", comments=comments, dates=dates, usernames=usernames, zip=zip)
	else:	
		# Get max cid
		cidcursor = g.conn.execute("SELECT cid FROM comments ORDER BY cid DESC LIMIT 1")
		max_cid = 0
		for result in cidcursor:
			max_cid = result['cid']
		cidcursor.close()
		max_cid += 1
	
		# Anonymous uid
		uid = 42069
		# If a user logged in, replace uid
		if len(username) != 0:
			uidcursor = g.conn.execute("SELECT user_id FROM accounts WHERE username = '" + username + "'")
			for result in uidcursor:
				uid = result['user_id']
			uidcursor.close()
		# Get current date
		dt = datetime.now().strftime('%Y-%m-%d')
		# Insert new comment into comments table
		cmd = "INSERT INTO comments(cid, text, date, uid) VALUES (" +str(max_cid)+ ", '" +text+ "', '" +dt+"', " +str(uid)+ ")"
		g.conn.execute(cmd)	  	
 
		# Look up updated comments
    		cursor = g.conn.execute("SELECT cid, text, date, username FROM comments, accounts WHERE user_id = uid ORDER BY date DESC")
    		comments = []
    		dates = []
    		usernames = []
    		for result in cursor:
			comments.append(result['text'])
			dates.append(result['date'])
			usernames.append(result['username'])
		cursor.close()

		return render_template('comments.html', title='Comments', comments=comments, dates=dates, usernames=usernames, zip=zip)

    else:
	return render_template('comments.html', title='Comments', comments=comments, dates=dates, usernames=usernames, zip=zip)	

# Login Page
@app.route("/login", methods=[ 'GET', 'POST' ])
def login():
    global username
    # Check if user is logged in
    if 'username' in session:
        return render_template('login.html', title='Login')
    # Check if user requested log in
    elif request.method == 'POST':
        username = request.form['username']
	if len(username) == 0:
		return render_template('login.html', title='Login', fail="No username was specified")
	else:
		# If username is not emtpy, look up all usernames
		cursor = g.conn.execute("SELECT DISTINCT username FROM accounts")
		usernames = []
		for result in cursor:
			usernames.append(result['username'])
		cursor.close()
		# If username is in database, authorize
		if username in usernames:
	        	session['username'] = username
	        	session['logged_in'] = True
	        	return render_template('login.html', title='Login')
		else:
			return render_template('login.html', title='Login', fail="Need to register username first")
    else:
        return render_template('login.html', title='Login')

# Logout Page
@app.route("/logout")
def logout():
    global username
    session['logged_in'] = False
    session.pop('username', None)
    username = ""
    return login()


# Main function
if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)    
    def run(debug, threaded, host, port):

	HOST, PORT = host, port
	print "running on %s:%d" % (HOST, PORT)
	app.secret_key = os.urandom(12)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
    run()
