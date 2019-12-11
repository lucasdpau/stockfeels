import time, os
from flask import abort, Flask, render_template, request, session, redirect
#typing in functions.login_required breaks the @decorator
from functions import login_required
import functions

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
#secret key for sessions. we need a more secure way of doing this than storing in source code
app.secret_key = "nzxcz,m,as123a"

# API Key is pk_c141e91a6055420ca2726bedc1f590b5

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
            #test_str = functions.test_db_get_regusers()
            return render_template('index.html')     
        
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


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

@app.route("/registererror", methods=["GET"])
def registry_error():
    return "There's an error in your form."

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    #shows when the user logs in. Has all their info, shows a list of their entries
    user_transactions = functions.get_users_transactions(session['user_id'])
    user_transactions.reverse()
    #user_transactions is a list of row objects from the sqlite db. it should be reversed so that the most recent entry is on 
    #top when the program iterates over the list.
    #if this list isnt empty, get the keys from the first row object
    number_of_entries = len(user_transactions)
    key_list = []
    if number_of_entries > 0:
        key_list = user_transactions[0].keys()
    
    #paginate the entries so that they aren't all on one page. also default to page 1 if invalid query string
    requested_page = request.args.get('p','')
    try:
        current_profile_page = int(requested_page)
    except:
        current_profile_page = 1
    entries_per_page = 4
    total_pages = int(number_of_entries/entries_per_page) + 1
    #'shorten' the list of user transactions to only contain the content in the "current page"
    user_transactions = user_transactions[(entries_per_page * (current_profile_page-1)):(entries_per_page * current_profile_page)]
        
    stock_info_dict = {}
    for transaction in user_transactions:
        #shorten comments for preview
        stock_info_dict[transaction] = {}
        if len(transaction['comment']) > 10:
            preview_comment = transaction['comment'][:10] + ". . ."
        else:
            preview_comment = transaction['comment']
        stock_info_dict[transaction]["preview_comment"] = preview_comment
        
        #if an invalid symbol is in the transaction, its an error. set price to 0.
        if functions.get_stock_quote_as_plaintext(transaction["stock_name"]) == "Unknown symbol":
            stock_info_dict[transaction]["current_price"] = 0
            stock_info_dict[transaction]["is_profitable"] = False
        else:
            stock_info_dict[transaction]["current_price"] = float(functions.get_stock_quote_as_plaintext(transaction["stock_name"]))
            if stock_info_dict[transaction]["current_price"] > transaction["price"]:
                stock_info_dict[transaction]["is_profitable"] = True
            else:
                stock_info_dict[transaction]["is_profitable"] = False
            # For selling transactions, reverse the colors
            if transaction["buysell"] == '1':
                stock_info_dict[transaction]["is_profitable"] = not stock_info_dict[transaction]["is_profitable"]
        
    return render_template('profile.html', user_transactions=user_transactions, key_list=key_list, stock_info_dict=stock_info_dict, current_profile_page=current_profile_page,
                           total_pages=total_pages)

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
        #submit changes to the database and then return to the user's profile page
        functions.enter_transaction(userid, trans_datetime, stock_name, buysell, price, quantity, comment, emotion)
        return redirect("/profile")
        
    else:
        return render_template('entry.html')

@app.route("/details", methods=["GET","POST"])
@login_required
def details():
    userid = session["user_id"]
    #gets the query string and stores it.
    trans_id = request.args.get("transactionid")

    #Users are only allowed to view their own transactions. This checks to make sure the current user is the one who made the entry
    if request.method == "GET":
        #we need trans_id as int type for the check to work
        try:
            trans_id_int = int(trans_id)
        except:
            abort(404)  
        #check if the transactionid belongs to the userid
        user_permission = functions.check_if_transid_belongs_to_user(userid, trans_id_int)
        transaction_details_row_object = functions.get_single_transaction(trans_id)
        transaction_details_dict = {}
        #row_object can't be manipulated like a dict, so create a dict with the same keys/values that we can use
        for key in transaction_details_row_object.keys():
            transaction_details_dict[key] = transaction_details_row_object[key]    
        if user_permission:
            if functions.get_stock_quote_as_plaintext(transaction_details_dict["stock_name"]) != "Unknown symbol":
                current_price = float(functions.get_stock_quote_as_plaintext(transaction_details_dict["stock_name"]))
                price_difference = round(current_price - transaction_details_row_object["price"], 2)
            else:
                current_price = 0
                price_difference = 0
            transaction_details_dict["current_price"] = current_price
            transaction_details_dict["price_difference"] = price_difference
            transaction_details_dict["total_current_price"] = round(current_price * transaction_details_dict["quantity"], 2)
            transaction_details_dict["total_price_difference"] = round(price_difference * transaction_details_dict["quantity"], 2)
            
            return render_template("details.html", transaction_details_dict=transaction_details_dict)
        else:
            #return 403 if user is sneaky and edits query string to see other transactions
            abort(403)
    
    elif request.method == "POST":
        trans_id = request.form.get("transactionid")
        stock_name = functions.get_single_transaction(trans_id)["stock_name"]
        #if an invalid stock symbol was entered
        try:
            current_price = functions.get_stock_quote_as_plaintext(stock_name)
        except:
            return "Invalid stock name"
        return current_price   

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    Flask.run(app, debug=True, host="0.0.0.0", port=port)
      
#add forgetting password/email
#hide transaction/userid