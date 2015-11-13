#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.httpauth import HTTPBasicAuth
import pymongo
import json
import os
from bson import json_util
from bson import objectid

app = Flask(__name__, static_url_path = "")
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

records = [
#    {
#        'steam_id' : '58169609',
#        'hero'  : 11,
#        'time'  : 150,
#        'leveling' : 'l',
#        'typescore' : 'c',
#        'value' : 100
#    },
#    {
#        'steam_id' : '58169608',
#        'hero'  : 106,
#        'time'  : 150,
#        'leveling' : 1,
#        'typescore' : 'cs',
#        'value' : 5
#    },
#    {
#        'steam_id' : '58169609',
#        'hero'  : 106,
#        'time'  : 150,
#        'leveling' : 1,
#        'typescore' : 'lh',
#        'value' : 5
#    },
#    {
#        'steam_id' : '58169609',
#        'hero'  : 106,
#        'time'  : 150,
#        'leveling' : 1,
#        'typescore' : 'dn',
#        'value' : 5
#    }
]

@app.route('/records', methods = ['GET'])
def get_records():
    print 'GET RECORDS'
    #get the request parameters
    steam_id = request.args.get('steam_id')
    api_key = request.args.get('api_key')    
    #if steam_id != None:
    #    steam_id_records = []
    #    for record in records:
    #        if steam_id == record['steam_id']:
    #            steam_id_records.append(record)
    #    data = {"api_key" : api_key, "steam_id" : steam_id, "data" : steam_id_records}
    #    return jsonify({'data' : data})
    #else:
    #    return jsonify({'data' : records})

    #setup the connection
    conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]
    #conn = pymongo.MongoClient()
    #db = conn.lasthitchallengedb

    steam_id_records = []
    #query the DB for all the parkpoints
    result = db.records.find({'steam_id' : steam_id})
    for rec in result:
        steam_id_records.append({'hero' : rec['hero'], 'time' : rec['time'], 'leveling' : rec['leveling'], 'typescore' : rec['typescore'],'value' : rec['value']})

    data = {"api_key" : api_key, "steam_id" : steam_id, "data" : steam_id_records}

    return jsonify({'data' : data})
    #Now turn the results into valid JSON
    #return str(json.dumps({'data':list(result)},default=json_util.default))

@app.route('/allrecords', methods = ['GET'])
def all_records():
    print 'ALL RECORDS'
    key = request.args.get('key')

    if key == '17354443':
        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
        db = conn[os.environ['OPENSHIFT_APP_NAME']]
        #conn = pymongo.MongoClient()
        #db = conn.lasthitchallengedb

        steam_id_records = []
        #query the DB for all the parkpoints
        result = db.records.find()
        for rec in result:
            steam_id_records.append({'steam_id' : rec['steam_id'], 'hero' : rec['hero'], 'time' : rec['time'], 'leveling' : rec['leveling'], 'typescore' : rec['typescore'],'value' : rec['value']})

        data = {"data" : steam_id_records}
        return jsonify({'data' : data})
        #return 'shit'
    else:
        return jsonify({'data' : 'nothing to see here'})

@app.route('/leaderboard', methods = ['GET'])
def get_leaders():
    print 'LEADERBOARD'
    steam_id = request.args.get('steam_id')
    api_key = request.args.get('api_key')
    hero = request.args.get('hero')
    time = request.args.get('time')
    api_key = request.args.get('time')
    leveling = request.args.get('leveling')
    typescore = request.args.get('typescore')

    conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]
    #conn = pymongo.MongoClient()
    #db = conn.lasthitchallengedb

    table = []
    result = db.records.find({'hero' : int(hero), 'time' : int(time), 'leveling' : leveling, 'typescore' : typescore}).sort('value', -1).limit(100)
    for rec in result:
        pos = {'steam_id' : rec['steam_id'], 'value' : rec['value']}
        table.append(pos)
    data = {'steam_id' : steam_id, 'api_key' : api_key, 'data' : table}
    return jsonify({'data' : data})

@app.route('/clear', methods = ['GET'])
def clear_records():
    print 'CLEAR'
    key = request.args.get('key')

    if key == '17354443':
        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
        db = conn[os.environ['OPENSHIFT_APP_NAME']]
        #conn = pymongo.MongoClient()
        #db = conn.lasthitchallengedb

        db.records.remove({})

        return jsonify({'data' : 'data cleared'})
    else:
        return jsonify({'data' : 'nothing to see here'})


#coll.update(key, data, {upsert:true});

##@app.route('/records', methods = ['POST'])
##def add_records():
##    print 'ADD RECORDS'
##    if request.form:
##        result = dict((key, request.form.getlist(key) if len(request.form.getlist(key)) > 1 else request.form.getlist(key)[0]) for key in request.form.keys())
##        steam_id = result.get('steam_id')
##        api_key = result.get('api_key')
##        data = json.loads(result.get('data'))
##        new_records = []
##
##        #conn = pymongo.MongoClient()
##        #db = conn.lasthitchallengedb
##        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
##        db = conn[os.environ['OPENSHIFT_APP_NAME']]
##
##        for elem in data:
##            rec = db.records.find_one({'steam_id' : steam_id, 'hero' : int(elem['hero']), 'time' : int(elem['time']), 'leveling' : elem['leveling'], 'typescore' : elem['typescore']})
##            if rec != None:
##                if rec['value'] < int(elem['value']):
##                    rec['value'] = int(elem['value'])
##                    db.records.save(rec)
##                else:
##                    print 'do nothing'
##            else:
##                new_records.append({'steam_id' : steam_id, 'hero' : int(elem['hero']), 'time' : int(elem['time']), 'leveling' : elem['leveling'], 'typescore' : elem['typescore'], 'value' : int(elem['value'])})
##        if len(new_records) > 0:
##            db.records.insert(new_records)
##        return jsonify({'data' : 'OK'}), 201

@app.route('/clearduplicates', methods = ['GET'])
def clear_duplicates():
    print 'CLEAR DUPLICATES'
    key = request.args.get('key')
    heroid = request.args.get('heroid')

    if key == '17354443':
        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
        db = conn[os.environ['OPENSHIFT_APP_NAME']]
        #conn = pymongo.MongoClient()
        #db = conn.lasthitchallengedb

        #heroes = ["102","73","68","1","2","3","65","38","4","62","78","99","61","96","81","66","56","51","5","55","50","43","87","69","49","6","107","7","103","106","58","33","41","72","59","74","91","64","8","90","23","104","52","31","54","25","26","80","48","77","97","94","82","9","10","89","53","36","60","88","84","57","111","76","44","12","110","13","14","45","39","15","32","86","16","105","79","11","27","75","101","28","93","35","67","71","17","18","46","109","29","98","34","19","83","95","100","85","70","20","40","47","92","37","63","21","112","30","42"]
        #heroes = [102,73,68,1,2,3,65,38,4,62,78,99,61,96,81,66,56,51,5,55,50,43,87,69,49,6,107,7,103,106,58,33,41,72,59,74,91,64,8,90,23,104,52,31,54,25,26,80,48,77,97,94,82,9,10,89,53,36,60,88,84,57,111,76,44,12,110,13,14,45,39,15,32,86,16,105,79,11,27,75,101,28,93,35,67,71,17,18,46,109,29,98,34,19,83,95,100,85,70,20,40,47,92,37,63,21,112,30,42]
        res = []
        #for h in heroes:
        steam_id = "-1"
        hero = -1
        time = -1
        typescore = "-1"
        leveling = "-1"
        print "PRE SORT"
        result = db.records.find({'hero' : int(heroid)}).sort({'steam_id' : 1, 'time' : 1, 'typescore' : 1, 'leveling' : 1})
        print "POST SORT"
        print("records count = " + str(result.count()))
        for r in result:
            #print ("steam_id = " + str(steam_id) + " hero = " + str(hero) + " time = " + str(time) + " typescore = " + typescore + " leveling = " + leveling)
            if (steam_id == r['steam_id'] and hero == r['hero'] and time == r['time'] and typescore == r['typescore'] and leveling == r['leveling']):
                print "DUPLICATE!"
                res.append({'steam_id' : r['steam_id'], 'hero' : r['hero']})
                db.records.remove(r)
            else: 
                steam_id = r['steam_id']
                hero = r['hero'] 
                time = r['time'] 
                typescore = r['typescore']
                leveling = r['leveling']
        return jsonify({'data' : res})
    else:
        return jsonify({'data' : 'nothing to see here'})

@app.route('/records', methods = ['POST'])
def add_records():
    print 'ADD RECORDS'
    if request.form:
        result = dict((key, request.form.getlist(key) if len(request.form.getlist(key)) > 1 else request.form.getlist(key)[0]) for key in request.form.keys())
        steam_id = result.get('steam_id')
        api_key = result.get('api_key')
        data = json.loads(result.get('data'))
        new_records = []

        #conn = pymongo.MongoClient()
        #db = conn.lasthitchallengedb
        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
        db = conn[os.environ['OPENSHIFT_APP_NAME']]

        for elem in data:
            db.records.update( { 'steam_id' : steam_id, 'hero' : int(elem['hero']), 'time' : int(elem['time']), 'leveling' : elem['leveling'], 'typescore' : elem['typescore'], 'value': { "$lte" : int(elem['value']) }},
                    { "$set" : { 'value' : int(elem['value']) }}, upsert = True);
        return jsonify({'data' : 'OK'}), 201

@app.route('/addrecord', methods = ['GET'])
def add_record():
    print 'ADD RECORDS'
    steam_id = request.args.get('steam_id')
    hero = request.args.get('hero')
    time = request.args.get('time')
    leveling = request.args.get('leveling')
    typescore = request.args.get('typescore')
    value = request.args.get('value')
    key = request.args.get('key')
    if key == '17354443':
        #conn = pymongo.MongoClient()
        #db = conn.lasthitchallengedb
        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
        db = conn[os.environ['OPENSHIFT_APP_NAME']]
        db.records.insert({ 'steam_id' : steam_id, 'hero' : int(hero), 'time' : int(time), 'leveling' : leveling, 'typescore' : typescore, 'value': int(value)})
        return jsonify({'data' : 'data inserted'})
    else:
        return jsonify({'data' : 'nothing to see here'})

@app.route('/cheaters', methods = ['POST'])
def add_cheater():
    print 'ADD CHEATERS'
    if request.form:
        result = dict((key, request.form.getlist(key) if len(request.form.getlist(key)) > 1 else request.form.getlist(key)[0]) for key in request.form.keys())
        steam_id = result.get('steam_id')
        api_key = result.get('api_key')

        #conn = pymongo.MongoClient()
        #db = conn.lasthitchallengedb
        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
        db = conn[os.environ['OPENSHIFT_APP_NAME']]
        rec = db.cheaters.find_one({'steam_id' : steam_id})
        if rec == None:
            db.cheaters.insert({'steam_id' : steam_id})

        return jsonify({'data' : 'OK'}), 201

#@app.route('/delcheaters', methods = ['GET'])
#def del_cheater():
#    print 'DEL CHEATERS'
#    #conn = pymongo.MongoClient()
#    #db = conn.lasthitchallengedb
#    conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
#    db = conn[os.environ['OPENSHIFT_APP_NAME']]
#    db.cheaters.remove({})
#    return jsonify({'data' : 'data cleared'})

@app.route('/delrecord', methods = ['GET'])
def del_cheater():
    print 'DEL RECORDS'
    steam_id = request.args.get('steam_id')
    key = request.args.get('key')
    if key == '17354443':
        #conn = pymongo.MongoClient()
        #db = conn.lasthitchallengedb
        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
        db = conn[os.environ['OPENSHIFT_APP_NAME']]
        db.records.remove({"steam_id" : steam_id})
        return jsonify({'data' : 'data cleared'})
    else:
        return jsonify({'data' : 'nothing to see here'})

@app.route('/swaprecords', methods = ['GET'])
def swap_records():
    print 'SWAP RECORDS'
    hero_from = request.args.get('hero_from')
    hero_to = request.args.get('hero_to')
    key = request.args.get('key')
    print('hero_from = ' + str(hero_from))
    print('hero_to = ' + str(hero_to))
    if key == '17354443':
        #conn = pymongo.MongoClient()
        #db = conn.lasthitchallengedb
        conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
        db = conn[os.environ['OPENSHIFT_APP_NAME']]
        db.records.update_many({'hero':int(hero_from)},{"$set":{'hero':int(hero_to)}})
        return jsonify({'data' : 'data swapped'})
    else:
        return jsonify({'data' : 'nothing to see here'})

@app.route('/cheaters', methods = ['GET'])
def get_cheaters():
    print 'GET CHEATERS'
    conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
    db = conn[os.environ['OPENSHIFT_APP_NAME']]
    #conn = pymongo.MongoClient()
    #db = conn.lasthitchallengedb
    steam_id_cheaters = []
    #query the DB for all the parkpoints
    result = db.cheaters.find()
    for rec in result:
        steam_id_cheaters.append({'steam_id' : rec['steam_id']})
    return jsonify({'data' : {'data' : steam_id_cheaters}})

if __name__ == '__main__':
    app.run(debug = True)