#!/usr/local/bin/python3

from flask import Flask, jsonify, abort, request, g
from pymongo import MongoClient
import sqlite3
import time

DATABASE = './bdd/voitures.db'
ARGS = ['annee', 'marque', 'modele', 'cnit', 'mine', 'carb', 'cv', 'puiss', 'bv', 'urb', 'exurb', 'mixte', 'co2']


application = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['cloud_stats']
collection = db['requests']

@application.before_request
def log_access(): 
    args = dict(request.args)
    if request.view_args != None:
        args.update(request.view_args)
    date = time.time()
    request_stat = {"args":args, "ts":date}
    collection.insert(request_stat)

@application.route('/api/v1.0/voitures', methods=['GET'])
def get_voitures():
    sql = 'SELECT * FROM voitures'
    check = False
    for key, val in request.args.items():
        if key not in ARGS:
            abort(400)
        else:
            if request.args.get(key) != None:
                if check == True:
                    sql += ' AND '
                else:
                    sql+= ' WHERE '
                sql += 'lower('+key + ') = \'' + request.args.get(key).lower() + '\''
                check = True
    voitures = query_db(sql)
    return jsonify({'voitures': voitures})


@application.route('/api/v1.0/voitures/<int:voiture_id>', methods=['GET'])
def get_voiture(voiture_id):
    voiture = query_db('select * from voitures where rowid="{0}"'.format(voiture_id))
    print(voiture)
    return jsonify(voiture[0])

@application.route('/api/v1.0/stats/', defaults={'key':None})
@application.route('/api/v1.0/stats/<key>/')
def get_top(key):
    if key == None:
        values = {}
        result = []
        for val in ARGS :
            values[val] = collection.find({'args.{0}'.format(val):{'$exists' : 'True'}}).count()
        for val in sorted(values, key=values.get, reverse=True):
            result.append({"param" : val, "value" : values[val]})
        return jsonify({"values"  : result})
    else :
        return("TODO")

def connect_db():
    return sqlite3.connect(DATABASE)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db

@application.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
    for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

if __name__ == '__main__':
    application.run(debug=True)
