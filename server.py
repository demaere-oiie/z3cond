from datetime import datetime
from flask import Flask, request, send_from_directory
from markupsafe import escape
from z3 import *

app = Flask(__name__)

def mkstate(name,args,clauses):
    return "::".join([name,args]+clauses)

n, m = Ints('n m')

table = {
"n>=m": n >= m,
"n>m":  n > m,
"n<m": n < m,
"m>=n": m >= n,
"m>n":  m > n,
"n==m": n == m,
"n<=m": m >= n,
"n>0":  n > 0,
"n==0": n==0,
"n>=0": n>=0,
"n<=0": n<=0,
"True": True,
"n==n": True,
"m==m": True,
}

def clausetoz3(c):
    cond = c.split(" ⟼  ")[0]
    return table[cond]

def checkshadow(*cs):
    s = Solver()
    for c in cs:
        s.push()
        s.add(c)
        if s.check() == unsat:
            return False
        s.pop()
        s.add(Not(c))
    return True

def complete(clauses):
    v = [clausetoz3(c) for c in clauses]
    return not checkshadow(*v+[True])

def subsumes(a,b):
    s = Solver()
    s.add(And(a, Not(b)))
    return s.check() == unsat

def eq(a,b):
    return subsumes(a,b) and subsumes(b,a)

def simplicial(clauses):
    v = [clausetoz3(c) for c in clauses]
    for i,x in enumerate(v):
      for j,y in enumerate(v):
        if i>=j: continue
        w = And(x,y)
        if not any(eq(w,z) for z in v):
            return False
    return True

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
        ''.join(f'<li>{escape(c)}' for c in clauses)+
        f'''</ul>
        <hr>
        {(not complete(clauses))*"incomplete"}
        {(not simplicial(clauses))*"overlapping"}
        <form action="/fn" method=post>
            <input type=hidden name=state value="{mkstate(
                name, args, clauses)}">
            <input type=text name=cond>
            <input type=text name=val>
            <input type=submit value=Define>
        </form>
        <br/>
        <form action="/bfn/0" method=post>
            <input type=hidden name=state value="{mkstate(
                name, args, clauses)}">
            <input type=submit value=Browse>
        </form>
        ''')

def color(i,cid,vs):
    cs = [clausetoz3(c) for c in vs]
    c = vs[i]
    if eq(cs[i],cs[cid]):
        return f'<div style="background-color:yellow">{escape(c)}</div>'
    elif subsumes(cs[cid],cs[i]):
        return f'<div style="background-color:lightblue">{escape(c)}</div>'
    elif subsumes(cs[i],cs[cid]):
        return f'<div style="background-color:pink">{escape(c)}</div>'
    else:
        return escape(c)

@app.post('/bfn/<int:clauseid>')
def bfunction(clauseid):
    vs = request.form['state'].split('::')
    name, args = vs[:2]
    clauses = vs[2:]
    nextid = clauseid+1
    if nextid >= len(clauses): nextid=0
    previd = clauseid-1
    if previd < 0: previd = len(clauses)-1
    return (f'''
    <!doctype html>
    <hr>
    {name}({args})
    <ul>'''+
    ''.join(f'<li>{color(i,clauseid,clauses)}' for i,c in enumerate(clauses))+
    f'''</ul>
    <hr>
    <form action="/bfn/{nextid}" method=post>
            <input type=hidden name=state value="{mkstate(
                name, args, clauses)}">
            <input type=submit value="+">
    </form>
    <form action="/bfn/{previd}" method=post>
            <input type=hidden name=state value="{mkstate(
                name, args, clauses)}">
            <input type=submit value="-">
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
