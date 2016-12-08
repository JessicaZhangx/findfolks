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
                       password='root',
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
    query = 'SELECT title, description, start_time, end_time, location_name, zipcode FROM `an_event` WHERE start_time <= DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 3 DAY)'
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
  return flask.redirect('/')

#Jessica
@app.route('/upcomingEvents', methods = ['GET', 'POST'])
def upcomingEvents():
  return flask.render_template('upcomingEvents.html')
#Jessica
@app.route('/signup', methods = ['GET', 'POST'])
def signUp():
  return flask.render_template('signUp.html')
#Jessica
@app.route('/search', methods = ['GET', 'POST'])
def search():
  return flask.render_template('search.html')
#Jessica
@app.route('/createEvent', methods = ['GET', 'POST'])
def createEvent():
  return flask.render_template('createEvent.html')
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

