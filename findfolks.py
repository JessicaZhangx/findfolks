# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 22:22:51 2016

@author: Jessica
"""
#import flask library
import flask 
import pymysql.cursors

#initialize the app from flask
app = flask.Flask(__name__)

#configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='cha3uvaf',
                       db='findfolks',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
                       
#define route to home function                    
@app.route('/')
def index():
    
    if ('error' in flask.session):
      error = flask.session['error']
      flask.session.pop('error')
    else:
      error = None
    #cursor used to send queries
    cursor = conn.cursor()
    query = 'SELECT title, description, start_time, end_time, location_name, zipcode FROM `an_event` WHERE start_time <= DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 3 DAY) AND start_time >= CURRENT_TIMESTAMP ORDER BY an_event.start_time ASC'
    cursor.execute(query)
    eventData = cursor.fetchall()

    interests = 'SELECT * FROM interest'
    cursor.execute(interests)
    interestData = cursor.fetchall()
    cursor.close()
    return flask.render_template('index.html', events = eventData, interests = interestData, error = error)

@app.route('/register')
def register():
    return flask.render_template('register.html')
    
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    firstName = flask.request.form['firstName']
    lastName = flask.request.form['lastName']
    email = flask.request.form['email']
    zipcode = flask.request.form['zipcode']
    username = flask.request.form['username']
    password = flask.request.form['password']

    cursor = conn.cursor()
    
    query = 'SELECT * FROM member WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    error = None
    if(data):
      error = "This user already exists"
      return flask.render_template('register.html', error = error)
    else:
      ins = 'INSERT INTO member VALUES(%s, md5(%s), %s, %s, %s, %s)'
      cursor.execute(ins, (username, password, firstName, lastName, email, zipcode))
      conn.commit()
      cursor.close()
      flask.session['username'] = username
      return flask.redirect(flask.url_for('home'))
@app.route('/login')
def login():
  return flask.render_template('login.html')

@app.route('/loginAuth', methods = ['GET', 'POST'])
def loginAuth():
  username = flask.request.form['username']
  password = flask.request.form['password']
  
  cursor = conn.cursor()
  
  query = 'SELECT * FROM member WHERE username = %s and password = md5(%s)'
  cursor.execute(query, (username, password))

  data = cursor.fetchone()

  cursor.close()
  error = None
  if(data):
    flask.session['username'] = username
    return flask.redirect(flask.url_for('home'))
  else:
    error = 'Invalid login or username'
    return flask.render_template('login.html', error = error)
@app.route('/interest', methods = ['GET', 'POST'])
def interest():
    interest = flask.request.form['interest']
    interest = interest.split(', ')
    category = interest[0]
    keyword = interest[1]
    cursor = conn.cursor()
    query = 'SELECT group_name, description FROM about NATURAL JOIN a_group WHERE category = %s AND keyword = %s'
    cursor.execute(query, (category, keyword))
    groups = cursor.fetchall()
    cursor.close()
    error = None
    if(groups):
      return flask.render_template('interest.html', groups = groups)
    else:
      error = "No groups with your interest, choose again!"
      flask.session['error']= error
      return flask.redirect(flask.url_for('index'))
@app.route('/home')
def home():
  username = flask.session['username']
  return flask.render_template('home.html', username = username)

@app.route('/logout')
def logout():
  flask.session.pop('username')
  return flask.redirect('/login')

#Jessica
@app.route('/upcomingEvents', methods = ['GET', 'POST'])
def upcomingEvents():
  username = flask.session['username']
  cursor = conn.cursor()
  threeDay = 'SELECT title, description, start_time, end_time, location_name, zipcode FROM sign_up NATURAL JOIN an_event WHERE username = %s AND start_time >= DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY) AND start_time <= DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY)  ORDER BY an_event.start_time ASC'
  cursor.execute(threeDay,(username))
  threeDayEvents = cursor.fetchall()
  currentDay = 'SELECT title, description, start_time, end_time, location_name, zipcode FROM sign_up NATURAL JOIN an_event WHERE username = %s AND DATE(start_time) = CURRENT_DATE() ORDER BY an_event.start_time ASC'
  cursor.execute(currentDay, (username))
  currentDayEvents = cursor.fetchall()
  cursor.close()
  return flask.render_template('upcomingEvents.html', threeDayEvents = threeDayEvents, currentDayEvents = currentDayEvents)

#Jessica
@app.route('/signup', methods = ['GET', 'POST'])
def signUp():
  username = flask.session['username']
  event = flask.request.form['event']
  cursor = conn.cursor()
  query = 'INSERT INTO sign_up (event_id, username) VALUES (%s, %s)'
  cursor.execute(query, (event, username))
  conn.commit()
  cursor.close()
  success = "You have signed up for this event!"
  flask.session['success'] = success
  return flask.redirect(flask.url_for('search', success = success))

#Jessica
@app.route('/search', methods = ['GET', 'POST'])
def search():
  if('success' in flask.session):
  	success = flask.session['success']
  	flask.session.pop('success')
  else:
  	success = None
  username = flask.session['username']
  cursor = conn.cursor()
  query = 'SELECT * FROM about NATURAL JOIN organize NATURAL JOIN an_event WHERE (category, keyword) IN (SELECT category, keyword FROM interested_in WHERE username = %s) AND event_id NOT IN (SELECT event_id FROM sign_up WHERE username = %s)'
  cursor.execute(query, (username, username))
  events = cursor.fetchall()
  cursor.close()
  return flask.render_template('search.html', events = events, success =success)
#Jessica
@app.route('/createEvent', methods = ['GET', 'POST'])
def createEvent():
  if('success' in flask.session):
    success = flask.session['success']
    flask.session.pop('success')
  else:
    success = None
  username = flask.session['username']
  cursor = conn.cursor()
  query = 'SELECT * FROM belongs_to NATURAL JOIN a_group WHERE username = %s AND authorized = 1'
  cursor.execute(query, (username))
  groups = cursor.fetchall()
  cursor.close()
  return flask.render_template('createEvent.html', groups = groups, success = success)
@app.route('/createEventForm', methods = ['GET', 'POST'])
def createEventForm():
  group_id = flask.request.form['group']
  flask.session['group'] = group_id
  return flask.render_template('createEventForm.html')
@app.route('/createEventAuth', methods = ['GET', 'POST'])
def createEventAuth():
  group_id = flask.session['group']
  username = flask.session['username']
  title = flask.request.form['title']
  description = flask.request.form['description']
  start_time = flask.request.form['start_time']
  end_time = flask.request.form['end_time']
  location_name = flask.request.form['location_name']
  zipcode = flask.request.form['zipcode']
  cursor = conn.cursor()
  query = 'INSERT INTO an_event (title, description, start_time, end_time, location_name, zipcode) VALUES (%s, %s, %s, %s, %s, %s)'
  cursor.execute(query, (title, description, start_time, end_time, location_name, zipcode))
  last_id = cursor.lastrowid
  insertOrganize = 'INSERT INTO organize (event_id, group_id) VALUES (%s, %s)'
  cursor.execute(insertOrganize, (last_id, group_id))
  insertSignUp = 'INSERT INTO sign_up (event_id, username) VALUES (%s, %s)'
  cursor.execute(insertSignUp, (last_id, username))
  conn.commit()
  cursor.close()
  flask.session.pop('group')
  flask.session['success'] = "Successfully created the event!"
  return flask.redirect(flask.url_for('createEvent'))
#Kristen
@app.route('/rateEvent', methods = ['GET', 'POST'])
def rateEvent():
  return flask.render_template('rateEvent.html')
#kristen
@app.route('/averageRatings', methods = ['GET', 'POST'])
def averageRatings():
  return flask.render_template('averageRatings.html')
#Kristen
@app.route('/friendsEvent', methods = ['GET', 'POST'])
def friendsEvent():
  return flask.render_template('friendsEvent.html')
#Kristen
@app.route('/postInEvent', methods = ['GET', 'POST'])
def postInEvent():
  return flask.render_template('postInEvent.html')
#Mali
@app.route('/makeFriends', methods = ['GET', 'POST'])
def makeFriends():
  return flask.render_template('makeFriends.html')
#Mali
@app.route('/joinGroup', methods = ['GET', 'POST'])
def joinGroup():
  return flask.render_template('joinGroup.html')
#Mali
@app.route('/createGroup', methods = ['GET', 'POST'])
def createGroup():
  return flask.render_template('createGroup.html')
#Mali
@app.route('/grantAccess', methods = ['GET', 'POST'])
def grantAccess():
  return flask.render_template('grantAccess.html')


app.secret_key = 'SECRETOFTHESECRETKEY'
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)

