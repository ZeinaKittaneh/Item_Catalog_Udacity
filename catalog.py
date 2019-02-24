import os
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
import urllib2
import datetime
from flask import session as login_session
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import string
from functools import wraps

engine = create_engine('sqlite:///categories.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "catalog app"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # NOQA
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then
        we split it on colons to pull out the actual token value and replace
        the remaining quotes with nothing so that it can be used directly
        in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    flash("you have been logged out")


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
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
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


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
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
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                 'Failed to revoke token for given user.', 400)
                                 )
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON Endpoints:
# Display all categories in json:
@app.route('/catalog/json')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


# Display information about a category_all items
@app.route('/catalog/<string:category_name>/items/json')
def categoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CategoryItem).filter_by(
        category_id=category.id).all()
    return jsonify(CategoryItems=[i.serialize for i in items])


# Display information about an item
@app.route('/catalog/<string:item_name>/json')
def itemJSON(item_name):
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    return jsonify(item=item.serialize)


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return func(*args, **kwargs)
        else:
            flash("Please login in order to modify items")
            return redirect('/login')
    return decorated_function


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).all()
    latest_items = session.query(CategoryItem).order_by(
        CategoryItem.created_at.desc()).limit(10).all()
    # return "This page will show all my categories"
    return render_template('allCategories.html', categories=categories,
                           latest_items=latest_items)


# Show a category items
@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def showItems(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(
        name=urllib2.unquote(category_name)).one()
    items = session.query(CategoryItem).filter_by(
        category_id=category.id).all()
    return render_template('category-items.html', items=items,
                           categories=categories, category=category)


# Show item description
@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    item = session.query(CategoryItem).filter_by(
        name=urllib2.unquote(item_name)).one()
    category = session.query(Category).filter_by(
        id=item.category_id).one()
    return render_template('item-description.html', item=item,
                           category_name=category.name)


# Create a new category item
@app.route('/catalog/new', methods=['GET', 'POST'])
@login_required
def newCategoryItem():
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'],
                               description=request.form['description'],
                               category_id=request.form['category_id'],
                               created_at=datetime.datetime.now(),
                               user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        category = session.query(Category).filter_by(
            id=newItem.category_id).one()
        return redirect(url_for('showItems', category_name=category.name))
    else:
        categories = session.query(Category).all()
        return render_template('add-item.html', categories=categories)


# Edit a category item
@app.route('/catalog/<string:category_name>/items/<string:item_name>/edit',
           methods=['GET', 'POST'])
@login_required
def editCategoryItem(category_name, item_name):
    editedItem = session.query(CategoryItem).filter_by(
        name=urllib2.unquote(item_name)).one()

    # only the user who created an item can edit it
    if editedItem.user_id != login_session['user_id']:
        flash("You are not authorized to edit this item!")
        return redirect(url_for('showItems', category_name=category_name))

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category_id']:
            category_selected = session.query(Category).filter_by(
                id=urllib2.unquote(request.form['category_id'])).one()
            editedItem.category_id = category_selected.id
        session.add(editedItem)
        session.commit()

        return redirect(url_for('showItem',
                        category_name=category_selected.name,
                        item_name=editedItem.name))
    else:
        categories = session.query(Category).all()
        return render_template('edit-item.html',
                               category_id=editedItem.category_id,
                               categories=categories, item=editedItem)

    # return 'This page is for editing item %s' % item_id


# Delete a menu item
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
@login_required
def deleteCategoryItem(item_name):
    itemToDelete = session.query(CategoryItem).filter_by(
        name=urllib2.unquote(item_name)).one()
    category = session.query(Category).filter_by(
        id=itemToDelete.category_id).one()

    # only the user who created an item can delete it
    if itemToDelete.user_id != login_session['user_id']:
        flash("You are not authorized to delete this item!")
        return redirect(url_for('showItems', category_name=category.name))

    if request.method == 'POST':
        category = session.query(Category).filter_by(
            id=itemToDelete.category_id).one()
        session.delete(itemToDelete)
        session.commit()

        return redirect(url_for('showItems', category_name=category.name))
    else:
        return render_template('delete-item.html', itemToDelete=itemToDelete)
    # return "This page is for deleting item %s" % item_id


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = False
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
