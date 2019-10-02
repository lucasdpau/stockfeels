import time, os, sqlite3, hashlib
from flask import Flask, redirect, render_template, request, session
from functools import wraps 

DATABASE = 'database.db'

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

def password_hash(password):
    #HASH THE PASSWORD HERE
    return hashed_pass

def login_required(function):
    @wraps(function)
    def decorated_func(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return function(*args, **kwargs)
    return decorated_func

def register(username, password):
    #WARNING. PASSWORDS NOT ENCRYPTED YET
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    #WARNING PLEASE SANITIZE INPUT 
    db.execute("INSERT INTO regusers (userid, username, pass) VALUES ({})".format())
    db.close()
    connect.commit()
    
def login(username, password):
    pass

def test_db():
    #WARNING. PASSWORDS NOT ENCRYPTED YET
    connect = sqlite3.connect(DATABASE)
    db = connect.cursor()
    #WARNING PLEASE SANITIZE INPUT 
    db.execute("SELECT * FROM regusers")
    stuff = db.fetchall()
    db.close()
    connect.commit()
    return stuff