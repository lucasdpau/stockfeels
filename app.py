import time, os
from flask import Flask, render_template, request, session, redirect
#typing in functions.login_required breaks the @decorator
from functions import login_required
import functions

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
#secret key for sessions. we need a more secure way of doing this than storing in source code
app.secret_key = "nzxcz,m,as123a"

@app.after_request
def after_request(response):
    #Disable caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/test", methods=["GET"])
def test():
    return render_template("test.html")

@app.route('/', methods=['GET', 'POST'])
def get_index():
    if request.method == 'POST':
        if not request.form.get("username"):
            return 'Please provide a username'
        elif not request.form.get("password"):
            return 'Please provide a password'
            #return apology("must provide password", 403)  
            
        submitted_username, submitted_pass = request.form.get("username"), request.form.get("password")
        if functions.login(submitted_username, submitted_pass):
            #setup the session dictionary/object if user successfully logs in
            session["user_id"] = str(functions.get_user_id(submitted_username))
            session["username"] = submitted_username
            return redirect('/')            
        else:
            return "Incorrect username or password"

    elif request.method == 'GET':
        #checks to see if there are entries in the session object. if yes, then a user has been logged in
        if 'user_id' in session:
            #render a "logged in" front page
            return redirect("/profile")
        
        else:
            #render a "logged out" front page
            test_str = functions.test_db_get_regusers()
            return render_template('index.html', test_str=test_str)     


@app.route('/register', methods=['GET', 'POST'])
def get_register():
    #logout of any session first
    if not session.get("user_id") == None:
        session.clear()
    if request.method == 'GET':
        return render_template('register.html')
    
    elif request.method == 'POST':
        if not request.form.get("username"):
            return "You did not enter a username"
        elif not request.form.get("password"):
            return "You did not enter a password"
        elif not request.form.get("confirm_password"):
            return "You did not re-enter a password"
        
        if not request.form.get("password") == request.form.get("confirm_password"):
            return "Passwords did not match"
        submitted_username, submitted_pass = request.form.get("username"), request.form.get("password")
        #register functions returns bool depending on if theres a duplicate username, so True if name is available
        if functions.register(submitted_username, submitted_pass):
            #auto login after registering
            session["user_id"] = str(functions.get_user_id(submitted_username))
            session["username"] = submitted_username            
            return redirect('/')
        else:
            return "Account name is taken"


@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    #shows when the user logs in. Has all their info, shows a list of their entries
    user_transactions = functions.get_users_transactions(session['user_id'])
    return render_template('profile.html', user_transactions=user_transactions)

@app.route('/entry', methods=['GET', 'POST'])
@login_required
def entry():
    #entry page. Lets the user enter more entries/
    if request.method == 'POST':
        userid = session["user_id"]
        if not request.form.get("stock"):
            return "No stock name given"
        elif not request.form.get("trans_datetime"):
            return "Select time of transaction"
        elif not request.form.get("buysell"):
            return "Buy or sell?"
        elif not request.form.get("price"):
            return "Price?"
        elif not request.form.get("quantity"):
            return "Quantity?"
        elif not request.form.get("comment"):
            return "Comments?"
        elif not request.form.get("emotion"):
            return "Feels?"

        trans_datetime = request.form.get("trans_datetime")
        stock_name = request.form.get("stock")
        buysell = request.form.get("buysell")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        comment = request.form.get("comment")
        emotion = request.form.get("emotion")
        
        functions.enter_transaction(userid, trans_datetime, stock_name, buysell, price, quantity, comment, emotion)
        return redirect("/profile")
        
    else:
        return render_template('entry.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    Flask.run(app, debug=True, host="0.0.0.0", port=port)