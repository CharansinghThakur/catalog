from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Guitars
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Guitarplay1"


# Connect to Database and create database session
engine = create_engine('sqlite:///guitardb.db')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps(' Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;height: 300px;border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
        # disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("you are logged out ")
        return redirect(url_for('showHome'))

    else:
        # If the token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/guitars/JSON')
def guitarsJSON():
    guitars = session.query(Guitars).all()
    return jsonify(guitars=[r.serialize for r in guitars])


@app.route('/guitars/<int:guitar_id>/JSON')
def guitarJSON(guitar_id):
    guitar = session.query(Guitars).filter_by(guitar_id=guitar_id).one()
    return jsonify(guitar=guitar.serialize)


# Home Page
@app.route('/')
@app.route('/home')
def showHome():
    guitars = session.query(Guitars).order_by(asc(Guitars.guitar_name))
    if 'username' not in login_session:
        return render_template('publichome.html', guitars=guitars)
    else:
        return render_template('home.html', guitars=guitars)


# Adding a new guitar
@app.route('/guitars/newGuitar/', methods=['GET', 'POST'])
def newGuitar():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGuitar = Guitars(
            guitar_name=request.form['guitar_name'],
            guitar_type=request.form['type'],
            price=request.form['price'],
            user_id=login_session['user_id'])
        session.add(newGuitar)
        flash('New guitar %s is inserted' % newGuitar.guitar_name)
        session.commit()
        return redirect(url_for('showHome'))
    else:
        return render_template('newGuitar.html')


# Editing a Guitar
@app.route('/guitars/<int:guitar_id>/editGuitar/', methods=['GET', 'POST'])
def editGuitar(guitar_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedGuitar = session.query(Guitars).filter_by(guitar_id=guitar_id).one()
    creator = getUserInfo(editedGuitar.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("only creator can edit this place-" + creator.name)
        return redirect(url_for('showHome'))
    if request.method == 'POST':
        if request.form['guitar_name']:
            editedGuitar.guitar_name = request.form['guitar_name']
        if request.form['type']:
            editedGuitar.guitar_type = request.form['type']
        if request.form['price']:
            editedGuitar.price = request.form['price']
        flash('Guitar Successfully Edited %s' % editedGuitar.guitar_name)
        return redirect(url_for('showHome'))
    else:
        return render_template('editGuitar.html', guitar=editedGuitar)


# Delete a Guitar
@app.route('/guitars/<int:guitar_id>/delete/', methods=['GET', 'POST'])
def deleteGuitar(guitar_id):
    if 'username' not in login_session:
        return redirect('/login')
    guitarToDelete = session.query(Guitars).filter_by(
        guitar_id=guitar_id).one()
    creator = getUserInfo(guitarToDelete.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("only creator can delete this guitar- " + creator.name)
        return redirect(url_for('showHome'))
    if request.method == 'POST':
        session.delete(guitarToDelete)
        flash('%s Successfully Deleted' % guitarToDelete.guitar_name)
        session.commit()
        return redirect(url_for('showHome', guitar_id=guitar_id))
    else:
        return render_template('deleteGuitar.html', guitar=guitarToDelete)


# Acoustic Guitars
@app.route('/guitars/acoustic')
def acoustic():
    if 'username' not in login_session:
        return redirect('/login')
    acoustic = session.query(Guitars).filter_by(guitar_type='Acoustic').all()
    return render_template('acoustic.html', acoustic=acoustic)


# Electric Guitars
@app.route('/guitars/electric')
def electric():
    if 'username' not in login_session:
        return redirect('/login')
    electric = session.query(Guitars).filter_by(guitar_type='Electric').all()
    return render_template('electric.html', electric=electric)


# Acoustic Electric Guitars
@app.route('/guitars/electric_acoustic')
def electric_acoustic():
    if 'username' not in login_session:
        return redirect('/login')
    electric_acoustic = session.query(Guitars).filter_by(
        guitar_type='Electric Acoustic').all()
    return render_template(
        'electric_acoustic.html', electric_acoustic=electric_acoustic)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
