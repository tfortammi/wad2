# =========================== # 
#         IMPORTS             #
# =========================== # 
from flask import Flask, request, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
from os import environ
import requests
import json
import os

from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin

# =========================== # 
#     APP INITIALIZATION      #
# =========================== # 

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "wad-project-293012-d84d8e3a5ca6.json"

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    "projectId": "wad-project-293012"
})

db = firestore.client()

CORS(app)

# =========================== # 
#     VAR INITIALIZATION      #
# =========================== # 

MULTIPLIER_CONST = {
    "high" : 30,
    "medium" : 20,
    "low" : 30,
} 

# =========================== # 
#          TASKS              #
# =========================== # 

# Database fields: 
#    - dependencies: [0, ...] (int array)
#    - assignedTo: ["", ...] (string array)
#    - start: "10/27/20, 8:30 PM" (datetime)
#    - id: 1 (int)
#    - name: "Finish wireframe" (string)
#    - priority: "high" (string) [OPTIONS: "high", "medium", "low"]
#    - end: "10/29/20, 8:30 PM" (datetime)
#    - category: "bugs" (string) [OPTIONS: "bugs", "tasks", "low"]
#    - status: "new" (string) [OPTIONS: "new", "ongoing", "complete"]

# Get all the tasks within the database
@app.route("/get_all_tasks/<string:order>")
def get_all_tasks_asc(order):
    if order == "desc":
        task_ref = db.collection(u"Task")
        query = task_ref.order_by(
            u'id', direction = firestore.Query.DESCENDING)
        docs = query.stream()
    else:
        task_ref = db.collection(u"Task").order_by(u'id')
        docs = task_ref.stream()
    
    task_list = []
    for doc in docs:
        task_list.append(doc.to_dict())
    
    try:
        return {
            'tasks': task_list
        }, 200
    except Exception as e:
        print(e)
        return {"error": "Cannot retrieve tasks"}, 500

# Add a tasks into the database
@app.route('/add_task', methods=['POST'])
def add_task():

    response = requests.get("http://0.0.0.0:5001/get_all_tasks/desc")
    lastId = response.json()["tasks"][0]["id"]

    request.json["id"] = int(lastId) + 1
    request.json["status"] = "new"
    request.json["start"] = datetime.strptime(request.json["start"], "%Y-%m-%dT%H:%M")
    request.json["end"] = datetime.strptime(request.json["end"], "%Y-%m-%dT%H:%M")

    task_ref = db.collection(u"Task")
    docs = task_ref.stream()

    try:
        task_ref.document().set(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return {"error": "Cannot add task"}, 500

# Start on a task and update status
@app.route('/start_task', methods=['POST'])
def start_task():
    """
        Start task and update status based on id
        
        Expected JSON object:
        {
            "id" : <string: task's name>,
        }
    """
    try:
        task_ref = db.collection(u"Task")
        doc = list(task_ref.where("id", "==", request.json["id"]).stream())[0]
        task_ref.document(doc.id).update({u'status': "ongoing"})

        return jsonify({"success": True}), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot start task"}, 500

# Remove task based on id 

# Get task information based on id from the database 
@app.route('/get_task')
def get_task():
    try:
        task_ref = db.collection(u"Task")
        docDict = list(task_ref.where("id", "==", int(request.args.get('id'))).stream())[0].to_dict()

        return jsonify(docDict), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot get specified team"}, 500

# =========================== # 
#           TEAM              #
# =========================== # 

# Database fields: 
#    - name: "wad_team" (string)
#    - streak: 1 (int)

# Get all the teams within the database
@app.route("/get_all_teams")
def get_all_teams():

    team_ref = db.collection(u"Team")
    docs = team_ref.stream()

    team_list = []
    for doc in docs:
        team_list.append(doc.to_dict())
    
    try:
        return {
            'teams': team_list
        }, 200
    except Exception as e:
        print(e)
        return {"error": "Cannot retrieve tasks"}, 500

# Add a new team into the database
@app.route('/add_team', methods=['POST'])
def add_team():

    team_ref = db.collection(u"Team")
    docs = team_ref.stream()

    try:
        team_ref.document().set(request.json)
        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        print(e)
        return {
            "error": "Cannot add task"
        }, 500

# Remove a team from the database

# Get team information based on team name from the database
@app.route('/get_team')
def get_team():
    try:
        team_ref = db.collection(u"Team")
        docDict = list(team_ref.where("name", "==", request.args.get('name')).stream())[0].to_dict()

        return jsonify(docDict), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot get specified team"}, 500

# Update team streak using action flag (inc/del)
@app.route('/update_team_streak/<string:action>', methods=['POST'])
def update_team_streak(action):
    """
        Update the team streak according to the action flag set. 
        
        Expected JSON object:
        {
            "name" : <string: team's name>,
            "toAdd" : <int: streak to be added>,
        }

        Example use of URL: POST JSON object { "name" : "magicians", "toAdd" : 3} to http://0.0.0.0:5001/update_team_streak/inc to increase their streak by 3
        Example use of URL: POST JSON object { "name" : "magicians" } to http://0.0.0.0:5001/update_team_streak/del to reset their streak 
    """
    try:
        team_ref = db.collection(u"Team")
        doc = list(team_ref.where("name", "==", request.json["name"]).stream())[0]

        if action == "inc":
            team_ref.document(doc.id).update({u'streak': doc.to_dict()["streak"] + request.json["toAdd"]})
        else:
            team_ref.document(doc.id).update({u'streak': 0})

        return jsonify({"success": True}), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot update team streak"}, 500

# =========================== # 
#           USER              #
# =========================== # 

# Get all the users from the database
@app.route("/get_all_users")
def get_all_users():
    try:
        user_ref = db.collection(u"User")
        docs = user_ref.stream()

        user_list = []
        for doc in docs:
            user_list.append(doc.to_dict())

        return {
            'users': user_list
        }, 200
    except Exception as e:
        print(e)
        return {"error": "Cannot retrieve tasks"}, 500

# Add a user into the database
@app.route('/add_user', methods=['POST'])
def add_user():
    """
        Adds a new user to the database.
        
        Expected JSON object:
        {
            "class" : <string: user's class>,
            "email" : <string: user's email>,
            "name" : <string: user's name>,
            "role" : <string: user's role>,
            "team" : <string: user's team>,
        }
    """

    try:
        user_ref = db.collection(u"User")
        docs = user_ref.stream()

        request.json["damage"] = 10
        request.json["level"] = 1
        request.json["exp"] = 0
        request.json["hp"] = 100

        user_ref.document().set(request.json)
        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        print(e)
        return {
            "error": "Cannot add user"
        }, 500

# Get user information based on email from the database
@app.route('/get_user')
def get_user():
    try:
        user_ref = db.collection(u"User")
        print(request.json)
        docDict = list(user_ref.where("email", "==", request.args.get('email')).stream())[0].to_dict()

        return jsonify(docDict), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot get specified user"}, 500

# Get users from the specified team
@app.route('/get_users_in_team')
def get_users_in_team():
    try:
        user_ref = db.collection(u"User")
        docs = user_ref.where("team", "==", request.args.get('name')).stream()

        user_list = []
        for doc in docs:
            user_list.append(doc.to_dict())
    
        return {
            'users': user_list
        }, 200

    except Exception as e:
        print(e)
        return {"error": "Cannot retrieve users"}, 500

# Update user exp + level (inc/dec)
@app.route('/update_user_stats/<string:action>', methods=['POST'])
def update_user_stats(action):
    """
        Update the user's exp and level statistics.
        
        Expected JSON object:
        {
            "email" : <string: user's email>,
            "exp" : <int: to be added or deleted exp>,
        }

        Example use of URL: POST JSON object { "email" : "joe@wad.co", "exp" : 10 } to http://0.0.0.0:5001/update_user_stats/inc to increase their exp by 10 (if after increasing 10 exp, his overall exp is over 100 then increase level by 1) 
        Example use of URL: POST JSON object { "name" : "magicians" } to http://0.0.0.0:5001/update_user_stats/del to decrease their exp by 10 (if after decreasing 10 exp, his overall exp is below 0 then decrease level by 1) 
    """
    try:
        user_ref = db.collection(u"User")
        doc = list(user_ref.where("email", "==", request.json["email"]).stream())[0]

        if action == "inc":
            if doc.to_dict()["exp"] + request.json["exp"] > 100:
                user_ref.document(doc.id).update({u'exp': doc.to_dict()["exp"] + request.json["exp"] - 100, u'level': doc.to_dict()["level"] + 1})
            else:
                user_ref.document(doc.id).update({u'exp': doc.to_dict()["exp"] + request.json["exp"]})
        else:
            if doc.to_dict()["exp"] - request.json["exp"] < 0:
                user_ref.document(doc.id).update({u'exp': 100 + doc.to_dict()["exp"] - request.json["exp"], u'level': doc.to_dict()["level"] - 1})
            else:
                user_ref.document(doc.id).update({u'exp': doc.to_dict()["exp"] - request.json["exp"]})

        return jsonify({"success": True}), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot update team streak"}, 500

# =========================== # 
#      HYBRID FUNCTIONS       #
# =========================== # 
@app.route('/complete_task', methods=['POST'])
def complete_task():
    try:
        response = requests.get("http://0.0.0.0:5001/get_task?id=" + str(request.json["id"]))
        end = response.json()["end"]
        exp = MULTIPLIER_CONST[response.json()["priority"]]

        if datetime.now() > datetime.strptime(response.json()["end"], "%a, %d %b %Y %H:%M:%S GMT"):
            team_list = []
            for user in response.json()["assignedTo"]:
                requests.post("http://0.0.0.0:5001/update_user_stats/del", json = {"email" : user, "exp" : exp})
                if requests.get("http://0.0.0.0:5001/get_user?email=" + user).json()["team"] not in team_list:
                    team_list.append(requests.get("http://0.0.0.0:5001/get_user?email=" + user).json()["team"])
            
            for team in team_list:
                requests.post("http://0.0.0.0:5001/update_team_streak/del", json = {"name" : team})
        else:
            team_list = []
            for user in response.json()["assignedTo"]:
                requests.post("http://0.0.0.0:5001/update_user_stats/inc", json = {"email" : user, "exp" : exp})
                if requests.get("http://0.0.0.0:5001/get_user?email=" + user).json()["team"] not in team_list:
                    team_list.append(requests.get("http://0.0.0.0:5001/get_user?email=" + user).json()["team"])
            
            for team in team_list:
                requests.post("http://0.0.0.0:5001/update_team_streak/inc", json = {"name" : team, "toAdd": exp // 10})
        
        task_ref = db.collection(u"Task")
        doc = list(task_ref.where("id", "==", request.json["id"]).stream())[0]
        task_ref.document(doc.id).update({u'status': "completed"})

        return jsonify({"exp": exp}), 200
    except Exception as e:
        print(e)
        return {"error": "Cannot mark task as complete"}, 500
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)