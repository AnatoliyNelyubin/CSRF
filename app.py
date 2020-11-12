import sqlite3
import uuid
from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect

try:
    from .models import init_dataset, Database
except (ImportError, SystemError):
    from models import init_dataset, Database

secret_code_variable = str(uuid.uuid4())

app = Flask(__name__)
# Disable Flask's default protection
# All major frameworks enforce CSRF-protection in forms by default, in all POST views.
app.config['WTF_CSRF_ENABLED'] = False

# the secret_code_varaiable is used for keeping a secret UUID code in the session so that
# it would be possible to check whether this cookie is sent from a user's session or from an evil's session

@app.route('/', methods=['GET'])
def main():
    return redirect(url_for('account'))


@app.route('/account', methods=['GET'])
def account():
    global secret_code_variable
    with Database() as db:
        db.execute("select amount from accounts where username = 'user1'")
        data = db.fetchone()
    resp = make_response(render_template('account.html', current_account=data[0], csrf_token=secret_code_variable))
    return resp


@app.route('/withdraw', methods=['POST'])
def withdraw():
    html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }
    username = "".join([html_escape_table.get(x,x) for x in request.form.get("username")])
    password = "".join([html_escape_table.get(x,x) for x in request.form.get("password")])
    csrf_token = request.form.get("csrf_token")
    global secret_code_variable

    if username != 'user1' or password != 'password' or not csrf_token:
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
