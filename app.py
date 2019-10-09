import time, os
from flask import Flask, render_template, request, session, redirect
from functions import login_required
import functions
#from flask_session import Session

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

#Session(app)

@app.after_request
def after_request(response):
    #Disable caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#DeBUGGING PAGES
@app.route('/success', methods=['GET'])
def success():
    return render_template('test.html')

@app.route('/fail', methods=['GET'])
def fail():
    return render_template('testfail.html')


@app.route('/', methods=['GET'])
def get_index():
    test_str = functions.test_db_get_regusers()
    return render_template('index.html', test_str = test_str)


@app.route('/register', methods=['GET', 'POST'])
def get_register():
    if request.method == 'GET':
        return render_template('register.html')
    
    elif request.method == 'POST':
        submitted_username, submitted_pass = request.form.get("username"), request.form.get("password")
        #register functions returns bool depending on if theres a duplicate username
        if functions.register(submitted_username, submitted_pass):
            return render_template('register.html')
        else:
            return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    #TODO Fix commented out session functionality
    #session.clear()
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if not request.form.get("username"):
            return redirect('/fail')
        elif not request.form.get("password"):
            return redirect('/fail')
            #return apology("must provide password", 403)  
            
        submitted_username, submitted_pass = request.form.get("username"), request.form.get("password")
        if not functions.login(submitted_username, submitted_pass):
            return redirect('/fail')
        
        else:
            #session["user_id"] = functions.get_user_id(submitted_username) #this may have to be changed to the userid int, instead of username
            return redirect('/success')


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    #TODO
    return render_template('profile.html')

@app.route('/entry', methods=['GET', 'POST'])
@login_required
def entry():
    #TODO
    if request.method == 'POST':
        pass
    else:
        return render_template('entry.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    Flask.run(app, debug=True, host="0.0.0.0", port=port)
