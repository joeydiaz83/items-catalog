from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, json
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from itemsCatalogDBsetup import Base, Category, Item


# Google Auth imports
from flask import session as login_session
import random, string


# oauth imports
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


engine = create_engine('sqlite:///itemsCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Fake Categories and items
# category = {
#     'name': 'Soccer',
#     'id': '1'
# }

# categories = [
#     {
#         'name': 'Soccer',
#         'id': '1'
#     },
#     {
#         'name': 'Basquetball',
#         'id': '2'
#     }
# ]

# items = [
#     {
#         'name': 'Soccer ball',
#         'description': 'A ball to play soccer',
#         'id': '1',
#         'category_id': '1'
#     },
#     {
#         'name': 'Soccer shoes',
#         'description': 'Shoes to play soccer',
#         'id': '2',
#         'category_id': '1'
#     },
#     {
#         'name': 'Basquetball ball',
#         'description': 'A ball to play basquetball',
#         'id': '3',
#         'category_id': '2'
#     },
#     {
#         'name': 'Basquetball shoes',
#         'description': 'Shoes to play basquetball',
#         'id': '4',
#         'category_id': '2'
#     },
# ]

# Create anti-forgery state token
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dump(resul.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store only the access_token
    login_session['credentials'] = credentials.access_token
    # return credential object
    credentials = AccessTokenCredentials(login_session['credentials'], 'user-agent-value')
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

#DISCONNECT - Revoke a current user's token and reset their login-session
@app.route('/gdisconnect/')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token.
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' %access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For watever reason, the give token was invalid
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response






@app.route('/')  # http://localhost:5000/
def showAllCategoriesAndItems():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('showAllCategoriesAndItems.html', categories=categories, items=items)

# Create a new Category
@app.route('/catalog/newCategory/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login/')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showAllCategoriesAndItems'))
    else:
        return render_template('newCategory.html')

# Edit existing category
@app.route('/catalog/<int:category_id>/editCategory/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(id = category_id).one()
    # print('EditedCategory is:{}'.format(editedCategory.name))
    if 'username' not in login_session:
        return redirect('/login/')
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        return redirect(url_for('showAllCategoriesAndItems'))
    else:
        return render_template('editCategory.html', editedCategory=editedCategory)

# Delete existing category    
@app.route('/catalog/<int:category_id>/deleteCategory/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id = category_id).one()
    # print('EditedCategory is:{}'.format(editedCategory.name))
    if 'username' not in login_session:
        return redirect('/login/')
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('showAllCategoriesAndItems'))
    else:
        return render_template('deleteCategory.html', categoryToDelete=categoryToDelete) 
####################################################################################################################

# Create a new Item
@app.route('/catalog/<int:category_id>/newItem/', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login/')
    if request.method == 'POST':
        itemToAdd = Item(name=request.form['name'], description=request.form['description'], category_id=category_id)
        session.add(itemToAdd)
        session.commit()
        return redirect(url_for('showAllCategoriesAndItems'))
    else:
        itemCategory = session.query(Category).filter_by(id = category_id).one()
        return render_template('newItem.html', category_id=category_id, itemCategory=itemCategory)

# Edit Item
@app.route('/catalog/<int:category_id>/<int:item_id>/editItem/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    editedItem = session.query(Item).filter_by(id = item_id).one()
    if 'username' not in login_session:
        return redirect('/login/')
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']    
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showAllCategoriesAndItems'))
    else:
        return render_template('editItem.html', category_id = category_id, item_id = item_id, editedItem = editedItem)

# Delete item
@app.route('/catalog/<int:category_id>/<int:item_id>/deleteItem/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    itemToDelete = session.query(Item).filter_by(id =item_id).one()
    if 'username' not in login_session:
        return redirect('/login/')
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showAllCategoriesAndItems'))
    else:
        return render_template('deleteItem.html', category_id = category_id, item_id = item_id, itemToDelete = itemToDelete)


# Making API Endpoint (GET Request)

# Get all categories in JSON
@app.route('/catalog/allCategories/JSON')
def allCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[category.serializeCategories for category in categories])

# Get all items in JSON
@app.route('/catalog/allItems/JSON')
def allItemsJSON():
    items = session.query(Item).all()
    return jsonify(Items=[item.serializeItems for item in items])


@app.route('/catalog/allCategoriesAndItems/JSON')
def allCategoriesAndItemsJSON():

    categories = session.query(Category).all()
    items = session.query(Item).all()

    catsList = []
    categoriesDict = {'allCategoriesAndItems': []}

    for category in categories:
        itemsList = []
        for item in items:
            if item.category_id==category.id:
                itemsDict = {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description
                }
                itemsList.append(itemsDict)

        catsDict = {
            'id': category.id,
            'category_name': category.name,
            'items': itemsList
        }
        catsList.append(catsDict)
        
    categoriesDict['allCategoriesAndItems'] = catsList           

    return jsonify(categoriesDict)

@app.route('/catalog/category/<int:category_id>/all-items/JSON')
def allItemsForCategory(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    print category.name
    

    itemsList = []
    for item in items:
        itemsDict = {
            'id': item.id,
            'name': item.name,
            'description': item.description
        }
        itemsList.append(itemsDict)



    categoryItems = { 
        'category':{
            'id': category.id,
            'name': category.name
        }, 'items': itemsList
    }
    
    
    

    # return jsonify(ItemsFromCategory=[item.serializeItems for item in items])
    return jsonify(categoryItems)







if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)


 