from flask import Flask, request
from flask_cors import CORS, cross_origin
# psycopg2 is for database
import psycopg2
import json
import os

DATABASE_URL = os.environ['DATABASE_URL']
app = Flask(__name__)
CORS(app)

@app.route('/<id>/')
def send_dict(id):
    return get_dict(id)

@app.route('/rm/<id>/<name>/<start>/<end>/', methods=['POST'])
def remove(id, name, start, end):
    start=int(start)
    end=int(end)
    if request.method=='POST':
        # If given time is not in database, do nothing
        times_dict = get_dict(id)
        if name in times_dict and [start,end] in times_dict[name]:
            times_dict[name].remove([start,end])
            if len(times_dict[name])==0:
                del times_dict[name]
        update_dict(id, times_dict)
        return get_dict(id)

@app.route('/add/<id>/<name>/<start>/<end>/', methods=['POST'])
def add(id, name, start, end):
    start=int(start)
    end=int(end)
    if request.method=='POST':
        times_dict = get_dict(id)
        if(name in times_dict):
            times_dict[name].append([start,end])
            times_dict[name].sort()
        else:
            times_dict[name]=[[start,end]]
        update_dict(id, times_dict)
        return get_dict(id)

def update_dict(id, times_dict):
    with get_db() as connection:
        with connection.cursor() as cur:
            cur.execute("UPDATE grouptimes SET TIMES='"+json.dumps(times_dict)+"' WHERE ID = '"+id+"'")

def get_dict(id):
    with get_db() as connection:
        with connection.cursor() as cur:
            cur.execute("SELECT times FROM grouptimes WHERE ID='"+id+"'")
            times_dict = cur.fetchone()
            if times_dict!=None:
                times = times_dict[0]
            else:
                new = dict()
                cur.execute("INSERT INTO grouptimes (ID, TIMES) VALUES ('"+id+"', '"+json.dumps(new)+"')")
                times = new
    return times

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')
