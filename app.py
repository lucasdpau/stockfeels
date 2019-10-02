import time, os
from flask import Flask, render_template, request
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


@app.route('/', methods=['GET'])
def get_index():
    test_str = functions.test_db()
    return render_template('index.html', test_str = test_str)


@app.route('/register', methods=['GET', 'POST'])
def get_register():
    if request.method == 'GET':
        return render_template('register.html')
    
    elif request.method == 'POST':
        #TODO
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    pass

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    #TODO
    return render_template('profile.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    Flask.run(app, debug=True, host="0.0.0.0", port=port)
