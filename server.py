from datetime import datetime
from flask import Flask, request, send_from_directory

app = Flask(__name__)

@app.post('/fn')
def dfunction():
    return f'''
    <!doctype html>
    <title>Define Function</title>
    <h1>{request.form['name']}({request.form['args']})</h1>
    '''

@app.route('/')
def homepage():
    return '''
    <!doctype html>
    <title>Define Function</title>
    <h1>Def. Fn</h1>
    <form action="/fn" method=post>
        <input type=text name=name>
        <input type=text name=args>
        <input type=submit value=Define>
    </form>
    '''

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
