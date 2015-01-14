#!/usr/local/bin/python3

from flask import Flask, jsonify, abort, request, g
import sqlite3

DATABASE = './bdd/voitures.db'

application = Flask(__name__)

@application.route('/api/v1.0/voitures', methods=['GET'])
def get_voitures():
    sql = 'SELECT * FROM voitures'
    check = False
    args = ['annee', 'marque', 'modele', 'cnit', 'mine', 'carb', 'cv', 'puiss', 'bv', 'urb', 'exurb', 'mixte', 'co2']
    #print(request.args.items())
    for key, val in request.args.items():
        
        if key not in args:
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
    #print(sql)
    return jsonify({'voitures': voitures})


@application.route('/api/v1.0/voitures/<string:voiture_id>', methods=['GET'])
def get_voiture(voiture_id):

    voiture = query_db('select * from voitures where rowid=\''+voiture_id+'\'')
    print(voiture)
    return jsonify(voiture[0])

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