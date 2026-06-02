from datetime import datetime
from flask import Flask, request, send_from_directory

app = Flask(__name__)

def mkstate(name,args,clauses):
    return "::".join([name,args]+clauses)


@app.post('/fn')
def dfunction():
    if 'name' in request.form:
        return f'''
        <!doctype html>
        <title>Define Function</title>
        <h1>{request.form['name']}({request.form['args']})</h1>
        <form action="/fn" method=post>
            <input type=hidden name=state value="{mkstate(
                request.form['name'], request.form['args'],[])}">
            <input type=text name=cond>
            <input type=text name=val>
            <input type=submit value=Define>
        </form>
        '''
    else:
        vs = request.form['state'].split('::')
        name, args = vs[:2]
        clauses = vs[2:]
        clauses.append(request.form['cond']+" ⟼  "+request.form['val'])
        return (f'''
        <!doctype html>
        <hr>
        {name}({args})
        <ul>'''+
        ''.join(f'<li>{c}' for c in clauses)+
        f'''</ul>
        <hr>
        <form action="/fn" method=post>
            <input type=hidden name=state value="{mkstate(
                name, args, clauses)}">
            <input type=text name=cond>
            <input type=text name=val>
            <input type=submit value=Define>
        </form>
        ''')

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
