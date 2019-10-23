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
            

def test_db_get_regusers():
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT * FROM regusers")
    stuff = db.fetchall()
    db.close()
    connect.commit()
    return stuff


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
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT * FROM transactions WHERE transaction_id =?", (trans_id,))
    transaction = db.fetchall()
    db.close()
    connect.commit() 
    return transaction
    
def get_users_transactions(userid):
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT * FROM transactions WHERE userid =?", (userid,))
    user_transactions = db.fetchall()
    db.close()
    connect.commit()
    return user_transactions

def get_entry_datetime():
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    db.execute("SELECT datetime('now')")
    time_string = db.fetchone()[0]
    db.close()
    connect.commit()
    return time_string
