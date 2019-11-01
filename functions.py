import time, os, sqlite3, hashlib
from flask import Flask, redirect, render_template, request, session
from functools import wraps 

DATABASE = 'database.db'
SALT = 'FKY7'
#we will salt passwords and hash with MD5. this is not the most secure way but for this small project it will do for now.

'''
#To use the module, you must first create a Connection object that represents the database
connection = sqlite3.connect('database.db')
#Once you have a Connection, you can create a Cursor object and call its execute() method to perform SQL commands:
db = connection.cursor()


# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

# we can use the builtin Row object/class to access columns by name/key instead of index
>>> conn.row_factory = sqlite3.Row
>>> c = conn.cursor()
>>> c.execute('select * from stocks')
<sqlite3.Cursor object at 0x7f4e7dd8fa80>
>>> r = c.fetchone()
>>> type(r)
<class 'sqlite3.Row'>
>>> tuple(r)
('2006-01-05', 'BUY', 'RHAT', 100.0, 35.14)
>>> len(r)
5
>>> r[2]
'RHAT'
>>> r.keys()
['date', 'trans', 'symbol', 'qty', 'price']
>>> r['qty']
100.0
>>> for member in r:
...     print(member)
...
2006-01-05
BUY
RHAT
100.0
35.14
'''

#TODO: all the sql functions have redundancies: sqlite3.connect(), connect.cursor(),  cursor.close(), and connection.commit().
#perhaps we could reduce redundancy using python decorators?

def password_hash(password):
    salt_pass = password + SALT
    hashed_pass = hashlib.md5(salt_pass.encode())
    return hashed_pass.hexdigest()

def login_required(function):
    #wrapper to make a function require that the user is logged in 
    @wraps(function)
    def decorated_func(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return function(*args, **kwargs)
    return decorated_func

def register(username, password):
    #returns false if unable to register due to duplicate username
    hashed_pass = password_hash(password)
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor() 
    #CHECKs IF USERNAME IS TAKEN
    db.execute("SELECT username FROM regusers WHERE username =?", (username,))
    check_duplicate_username = db.fetchall()
    if len(check_duplicate_username) > 0:
        return False
    else:
        db.execute("INSERT INTO regusers (username, password) VALUES (?,?)", (username, hashed_pass))
    db.close()
    connect.commit()
    return True
    
def login(username, password):
    #hash password, goto regusers table and see if username matches hash. if so return True
    hashed_pass = password_hash(password)
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT userid, username, password FROM regusers WHERE username =?", (username,))
    user_info_from_db = db.fetchall()
    db.close()
    connect.commit()    
    for returned_entries in user_info_from_db:
        if hashed_pass in returned_entries:
            user_id = returned_entries[0]
            return True
        else:
            return False

def get_user_id(username):
    #get the unique user_id number from the database for a given username
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT userid FROM regusers WHERE username =?", (username,))
    userid_from_db = db.fetchall()
    db.close()
    connect.commit()    
    for returned_entries in userid_from_db:
        return returned_entries[0]
            
def get_entry_datetime():
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT strftime('%Y-%m-%dT%H:%M:%S')")
    time_string = db.fetchone()[0]
    db.close()
    connect.commit()
    return time_string

def enter_transaction(userid, trans_datetime, stock_name, buysell, price, quantity, comment, emotion):
    entry_datetime = get_entry_datetime()
    #get the time of the user entering the data
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("INSERT INTO transactions (userid, trans_datetime, entry_datetime, stock_name, buysell, price, quantity, comment, emotion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (userid, trans_datetime, entry_datetime, 
                                                                                                                                                                             stock_name, buysell, price, quantity, comment, emotion))
    db.close()
    connect.commit()  
    return True 

def get_single_transaction(trans_id):
    #trans_id works if either int or str. returns a row obj contianing all the info in the transaction
    connect = sqlite3.connect(DATABASE)
    #using rows we can store the column names of the database as keys. and access values thru both keys or index
    connect.row_factory = sqlite3.Row
    db = connect.cursor()
    db.execute("SELECT * FROM transactions WHERE transaction_id =?", (trans_id,))
    transaction_tuple = db.fetchone()
    db.close()
    connect.commit() 
    return transaction_tuple
    
def get_users_transactions(userid):
    #takes either str or int for userid. returns a list of Row objects, each representing a transaction made by specified user.
    connect = sqlite3.connect(DATABASE)
    #using rows we can store the column names of the database as keys. and access values thru both keys or index
    connect.row_factory = sqlite3.Row
    db = connect.cursor()
    db.execute("SELECT * FROM transactions WHERE userid =?", (userid,))
    user_transactions = db.fetchall()
    db.close()
    connect.commit()
    return user_transactions

def check_if_transid_belongs_to_user(userid, transid):
    #transid must be an int
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT transaction_id FROM transactions WHERE userid =?", (userid,))
    transactions = db.fetchall()
    #transactions will be in the format [(1,), (2,), (3,), (4,), (5,)]
    db.close()
    connect.commit()
    for trans_id_tuples in transactions:
        if transid in trans_id_tuples:
            return True
    return False
    

# TEST FUNCTIONS #################

def test_db_get_regusers():
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT * FROM regusers")
    selection = db.fetchall()
    db.close()
    connect.commit()
    return selection

#using rows we can store the column names of the database as keys.
def test_get_users_transactions(userid):
    connect = sqlite3.connect(DATABASE)
    connect.row_factory = sqlite3.Row
    db = connect.cursor()
    db.execute("SELECT * FROM transactions WHERE userid =?", (userid,))
    transaction = db.fetchall()
    #a list of all transaction in row objects. row.keys() returns list of keys
    db.close()
    connect.commit() 
    return transaction
