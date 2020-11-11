import sqlite3
import uuid
from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect

try:
    from .models import init_dataset, Database
except (ImportError, SystemError):
    from models import init_dataset, Database


app = Flask(__name__)
# Disable Flask's default protection
# All major frameworks enforce CSRF-protection in forms by default, in all POST views.
app.config['WTF_CSRF_ENABLED'] = False

secret_code_varaiable = str(uuid.uuid4())
# the secret_code_varaiable is used for keeping a secret UUID code in the session so that
# it would be possible to check whether this coookine is sent from a user's session or from an evil's session

@app.route('/', methods=['GET'])
def main():
    return redirect(url_for('account'))


@app.route('/account', methods=['GET'])
def account():
    global secret_code_varaiable
    with Database() as db:
        db.execute("select amount from accounts where username = 'user1'")
        data = db.fetchone()
    resp = make_response(render_template('account.html', current_account=data[0]))
    secret_token = request.cookies.get('secret')
    if secret_token is None or secret_token != secret_code_varaiable:
        resp.set_cookie('secret', secret_code_varaiable)
    return resp


@app.route('/withdraw', methods=['POST'])
def withdraw():
    username = request.form.get("username")
    password = request.form.get("password")
    secret = request.cookies.get("secret")
    global secret_code_varaiable
    referrer = request.headers.get("Referer")
    if referrer != "http://127.0.0.1:5000/account":
        return redirect(url_for('account'))

    if username != 'user1' or password != 'password' or not secret:
        return redirect(url_for('account'))

    if secret != secret_code_varaiable:
        return redirect(url_for('account'))

    with Database() as db:
        db.execute("select amount from accounts where username = ?", (username, ))
        data = db.fetchone()
    
    if not data:
        return redirect(url_for('account'))
    
    if data[0] > 0:
        with Database() as db:
            db.execute("update accounts set amount = amount - 1 where username = ?", (username, ))

    return redirect(url_for('account'))


@app.route('/danger', methods=['GET'])
def danger():
    return render_template('danger.html')


if __name__ == '__main__':
    init_dataset()
    app.run(debug=True)
