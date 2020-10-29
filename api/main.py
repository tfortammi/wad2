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
import uuid
import math
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

EXP_CONST = {
    "high" : 15,
    "medium" : 10,
    "low" : 5,
} 

# =========================== # 
#          TASKS              #
# =========================== # 

# Note: A task can only have one dependency but may be the pre-requisite for one or more tasks 

# Database fields: 
#    - dependency: "" (string) 
#    - assignedTo: ["", ...] (string array) 
#    - start: "10/27/20, 8:30 PM" (datetime)
#    - id: "" (string)
#    - name: "Establish Business Requirements" (string)
#    - priority: "high" (string) [OPTIONS: "high", "medium", "low"]
#    - end: "10/29/20, 8:30 PM" (datetime)
#    - category: "bugs" (string) [OPTIONS: "bug", "task", "request", "improve", "others"]
#    - status: False (boolean) 
#    - guild: "wad_guild" (string)

# Get all the tasks specific to a guild within the database - CHECKED
@app.route("/get_all_tasks")
def get_all_tasks():
    """
        Get all tasks specific to a guild within database.
        
        Expected JSON object: 
        {
            "guild" : <string: guild that task belong to>,
        }
    """
    task_ref = db.collection(u"Task")
    docs = list(task_ref.where("guild", "==", request.args.get('guild')).stream())
    
    task_list = []
    for doc in docs:
        task_list.append(doc.to_dict())
    
    try:
        return {
            "tasks": task_list
        }, 200
    except Exception as e:
        print(e)
        return {"error": "Cannot retrieve tasks"}, 500

# Add a tasks into the database - CHECKED
@app.route("/add_task", methods=["POST"])
def add_task():
    """
        Add a new task into database with a random id.

        Note: Datetime expected to be in YYYY-MM-DDTHH:MM format (24 hour format). E.g. 2020-12-01T08:30 
        
        Expected JSON object:
        {
            "dependency" : <string: task's dependencies>,
            "assignedTo" : <array: task's assigned to members>,
            "start" : <datetime: task's start datetime>,
            "end" : <datetime: task's end datetime>,
            "priority" : <string: task's priority>,
            "category" : <string: task's priority>,
            "name" : <string: task's name>,
            "guild" : <string: which project task belong to>
        }
    """

    try:
        request.json["id"] = str(uuid.uuid4())
        request.json["status"] = False
        request.json["start"] = datetime.strptime(request.json["start"], "%m/%d/%Y")
        request.json["end"] = datetime.strptime(request.json["end"], "%m/%d/%Y")

        task_ref = db.collection(u"Task")
        docs = task_ref.stream()

        task_ref.document().set(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return {"error": "Cannot add task"}, 500

# Remove task based on id from database - CHECKED 
@app.route("/remove_task", methods=["POST"])
def remove_task():
    """
        Remove task based on id and remove any traces of it being a dependency for another task.
        
        Expected JSON object:
        {
            "id" : <string: task's id>,
        }
    """
    try:
        task_ref = db.collection(u"Task")
        docs = task_ref.stream()
        id_to_remove = ""

        for doc in docs:
            if doc.to_dict()["dependency"] == request.json["id"]:
                task_ref.document(doc.id).update({u"dependency": ""})
            if doc.to_dict()["id"] == request.json["id"]:
                id_to_remove = doc.id
        
        task_ref.document(id_to_remove).delete()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return {"error": "Cannot remove task"}, 500

# Get task information based on id from the database - CHECKED
@app.route('/get_task')
def get_task():
    """
        Get task information based on id.
        
        Expected JSON object:
        {
            "id" : <string: task's id>,
        }
    """
    try:
        task_ref = db.collection(u"Task")
        doc_dict = list(task_ref.where("id", "==", request.args.get('id')).stream())[0].to_dict()

        return jsonify(doc_dict), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot get specified task"}, 500

# Convert tasks id into their respective name - CHECKED
@app.route("/convert_ids_to_names", methods=["POST"])
def convert_ids_to_names():
    """
        Convert and return an array of task names from an array of task ids. 
        
        Expected JSON object:
        {
            "ids" : <array: array of task's ids>,
        }
    """
    try:
        task_ref = db.collection(u"Task")

        name_list = []
        for id in request.json["ids"]:
            doc_dict = list(task_ref.where("id", "==", id).stream())[0].to_dict()
            name_list.append(doc_dict["name"])

        return {
            "names": name_list
        }, 200

    except Exception as e:
        print(e)
        return {"error": "Cannot convert tasks ids to names"}, 500

# Get completed/incomplete tasks - CHECKED
@app.route("/get_tasks/<string:status>", methods=["POST"])
def get_tasks(status):
    """
        Get all completed/incomplete tasks specific to a guild within database.
        
        Expected JSON object: 
        {
            "guild" : <string: guild that task belong to>,
        }

        Example use of URL: POST JSON object { "guild" : "wad_guild" } to http://0.0.0.0:5001/get_tasks/true to get all the completed tasks by the guild - "wad_guild" 

        Example use of URL: POST JSON object { "guild" : "wad_guild" } to http://0.0.0.0:5001/get_tasks/false to get all the incomplete tasks by the guild - "wad_guild" 

    """
    try:
        status = False if status.lower() == "false" else True
        task_ref = db.collection(u"Task")
        doc_dict = [doc.to_dict() for doc in list(task_ref.where("guild", "==", request.json["guild"]).where("status", "==", status).stream())]

        return {
            "tasks" : doc_dict
        }, 200

    except Exception as e:
        print(e)
        return {"error": "Cannot get requested tasks."}, 500

# Modify task specifications - CHECKED
@app.route("/modify_task", methods=["POST"])
def modify_task():
    """
        Modify task settings in the database.
        
        Expected JSON object (NOTE: If the value is empty, function will take as there are no changes required/Can pass in only key-value pairs that require modification, meaning you don't have to pass in the exact JSON object below BUT id is a mandatory field and it CANNOT be modified):
        {
            "id" : <string: task's id> --> *MANDATORY*
            "dependency" : <string: task's dependency>,
            "assignedTo" : <array: array of user emails>,
            "start" : <datetime: task's start datetime>,
            "end" : <datetime: task's end datetime>,
            "name" : <string: task's name>,
            "priority" : <string: task's priority>,
            "category" : <string: task's category>, 
            "guild" : <string: guild that task belong to>,
            "status" : <boolean: completion status of the task>
        }

    """
    try:
        processed_json = { k: v for k, v in request.json.items() if v }
        if bool(processed_json):
            task_ref = db.collection(u"Task")
            doc_id = list(task_ref.where("id", "==", request.json["id"]).stream())[0].id

            processed_json.pop("id", None)
            task_ref.document(doc_id).update(processed_json)

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        print(e)
        return {
            "error": "Cannot modify task."
        }, 500

# =========================== # 
#           GUILD             #
# =========================== # 

# Database fields: 
#    - name: "wad2_guild" (string)
#    - streak: 0 (int)
#    - r_name: "repo_name" (string)
#    - r_desc: "This is the repository description." (string)
#    - r_access: true (boolean) [OPTIONS: true (public repo), false (private repo)]

# Get all the guilds within the database - CHECKED
@app.route("/get_all_guilds")
def get_all_guilds():
    """
        Get all guilds and their respective information.
        
        Expected JSON object: N/A
    """
    guild_ref = db.collection(u"Guild")
    docs = guild_ref.stream()

    guild_list = []
    for doc in docs:
        guild_list.append(doc.to_dict())
    
    try:
        return {
            'guilds': guild_list
        }, 200
    except Exception as e:
        print(e)
        return {"error": "Cannot retrieve tasks"}, 500

# Add a new guild into the database - CHECKED
@app.route('/add_guild', methods=['POST'])
def add_guild():
    """
        Add a new guild based on json inputs.
        
        Expected JSON object:
        {
            "name" : <string: guild's name>,
            "r_name" : <string: guild's repository name>,
            "r_desc" : <string: guild's repository description>,
            "r_access" : <string: guild's repository access status>,
        }
    """
    guild_ref = db.collection(u"Guild")
    docs = guild_ref.stream()

    request.json["streak"] = 0

    try:
        guild_ref.document().set(request.json)
        return jsonify({
            "success": request.json["name"]
        }), 200

    except Exception as e:
        print(e)
        return {
            "error": "Cannot add task"
        }, 500

# Remove a guild based on name from database - CHECKED
@app.route("/remove_guild", methods=["POST"])
def remove_guild():
    """
        Remove guild based on name from database. NOTE: Guild with existing users cannot be deleted!
        
        Expected JSON object:
        {
            "name" : <string: guild's name>,
        }
    """
    try:
        user_ref = db.collection(u"User")
        docs = list(user_ref.where("guild", "==", request.json["name"]).stream())

        if len(docs) == 0:
            guild_ref = db.collection(u"Guild")
            guild_id = list(guild_ref.where("name", "==", request.json["name"]).stream())[0].id
            guild_ref.document(guild_id).delete()
        else:
            return jsonify({"error": "Cannot remove guild with members."}), 404

        return jsonify({"success": True}), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot remove guild"}, 500    

# Get guild information based on guild name from the database - CHECKED
@app.route('/get_guild')
def get_guild():
    """
        Get guild information based on guild name.
        
        Expected GET params:
            - "name" = <string: guild's name>
    """
    try:
        guild_ref = db.collection(u"Guild")
        doc_dict = list(guild_ref.where("name", "==", request.args.get('name')).stream())[0].to_dict()

        return jsonify(doc_dict), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot get specified guild"}, 500

# Update guild streak using action flag (inc/del)
@app.route('/update_guild_streak/<string:action>', methods=['POST'])
def update_guild_streak(action):
    """
        Update the guild streak according to the action flag set. 
        
        Expected JSON object:
        {
            "name" : <string: guild's name>,
            "toAdd" : <int: streak to be added>,
        }

        Example use of URL: POST JSON object { "name" : "magicians", "toAdd" : 3} to http://0.0.0.0:5001/update_guild_streak/inc to increase their streak by 3.
        Example use of URL: POST JSON object { "name" : "magicians" } to http://0.0.0.0:5001/update_guild_streak/del to reset their streak.
    """
    try:
        guild_ref = db.collection(u"Guild")
        doc = list(guild_ref.where("name", "==", request.json["name"]).stream())[0]

        if action == "inc":
            guild_ref.document(doc.id).update({u'streak': doc.to_dict()["streak"] + request.json["toAdd"]})
        else:
            guild_ref.document(doc.id).update({u'streak': 0})

        return jsonify({"success": True}), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot update guild streak"}, 500

# =========================== # 
#           USER              #
# =========================== # 
# Database fields: 
#    - class: "magician" (string) [OPTIONS: "magician", "knight", "dragon", "elf"]
#    - damage: 10 (int) 
#    - email: "kakashi@wad2.co" (string)
#    - password: "password" (string)
#    - name: "Kakashi Hatake" (string)
#    - role: "Senior Developer" (string)
#    - guild: "wad2_guild" (string)
#    - exp: 0 (int) 
#    - hp: 100 (int) 
#    - level: 1 (int) 
#    - git_token: "QWERTYUIO" (string)

# Get all the users from the database - CHECKED
@app.route("/get_all_users")
def get_all_users():
    """
        Get all users and their respective information.
        
        Expected JSON object: N/A
    """
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

# Add a user into the database / Register a user into the database - CHECKED
@app.route('/add_user', methods=['POST'])
def add_user():
    """
        Adds a new user to the database.
        
        Expected JSON object:
        {
            "class" : <string: user's class>,
            "email" : <string: user's email>,
            "password" : <string: user's password>,
            "name" : <string: user's name>,
            "role" : <string: user's role>,
            "guild" : <string: user's guild>,
            "git_token" : <string: user's git access token>
        }
    """

    try:

        user_ref = db.collection(u"User")
        email_verification = list(user_ref.where("email", "==", request.json["email"]).stream())

        if len(email_verification) > 0:
            return jsonify({
                "error": "Email already exists."
            }), 200

        request.json["damage"] = 10
        request.json["multiplier"] = 1
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

# Get user information based on email from the database - CHECKED
@app.route('/get_user')
def get_user():
    """
        Get user information based on user's email.
        
        Expected GET params:
            - "email" = <string: user's email>

        Example Output: 
        {
            "class": "knight",
            "damage": 10,
            "email": "kakashi@wad2.co",
            "exp": 0,
            "git_token": "QWERTYUIOP",
            "hp": 100,
            "level": 1,
            "name": "Kakashi Hatake",
            "password": "password",
            "role": "Team Lead",
            "guild": "wad2_guild"
        }
    """
    try:
        user_ref = db.collection(u"User")
        print(request.json)
        doc_dict = list(user_ref.where("email", "==", request.args.get('email')).stream())[0].to_dict()

        return jsonify(doc_dict), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot get specified user"}, 500

# Get users from the specified guild - CHECKED
@app.route('/get_users_in_guild')
def get_users_in_guild():
    """
        Get all user who belong in specified guild name and their respective information.
        
        Expected GET params:
            - "name" = <string: guild name>

        Example Output: 
        {
            "users": [
                {
                "class": "magician",
                "damage": 10,
                "email": "sasuke@wad2.co",
                "exp": 0,
                "git_token": "QWERTYUIOP",
                "guild": "wad2_guild",
                "hp": 100,
                "level": 1,
                "name": "Sasuke Uchiha",
                "password": "password",
                "role": "Backend Developer"
                },
                {
                "class": "magician",
                "damage": 10,
                "email": "sai@wad2.co",
                "exp": 0,
                "git_token": "QWERTYUIOP",
                "guild": "wad2_guild",
                "hp": 100,
                "level": 1,
                "name": "Sai Yamanaka",
                "password": "password",
                "role": "SQL Developer"
                },
            ...
            ]
        }
    """
    try:
        user_ref = db.collection(u"User")
        docs = user_ref.where("guild", "==", request.args.get('name')).stream()

        user_list = []
        for doc in docs:
            user_list.append(doc.to_dict())
    
        return {
            'users': user_list
        }, 200

    except Exception as e:
        print(e)
        return {"error": "Cannot retrieve users"}, 500

# Get users from the specified guild in arrays of arrays - CHECKED
@app.route('/get_users_aoa_in_guild')
def get_users_aoa_in_guild():
    """
        Get all user who belong in specified guild name and their respective information in specific arrays of arrays format.
        
        Expected GET params:
            - "name" = <string: guild name>

        Example Output: 
        {
            "user_aoa": [
                ["Kakashi Hatake", "knight", "wad_guild", "1", "1"],
                ["Naruto Uzumaki", "dragon", "wad_guild", "1", "1"],
                ...
            ]
        }
    """
    try:
        user_ref = db.collection(u"User")
        docs = user_ref.where("guild", "==", request.args.get('name')).stream()

        user_aoa = []
        for doc in docs:
            user_aoa.append([doc.to_dict()["name"], doc.to_dict()["class"], doc.to_dict()["guild"], doc.to_dict()["level"], doc.to_dict()["multiplier"]])
    
        return {
            'user_aoa': user_aoa
        }, 200

    except Exception as e:
        print(e)
        return {"error": "Cannot retrieve users."}, 500

# Modify user settings - CHECKED
@app.route("/modify_user", methods=["POST"])
def modify_user():
    """
        Modify user settings in the database.
        
        Expected JSON object (NOTE: If the value is empty, function will take as there are no changes required/Can pass in only key-value pairs that require modification, meaning you don't have to pass in the exact JSON object below BUT email is a mandatory field even if there are no changes to it):
        {
            "class" : <string: user's class>,
            "email" : <string: user's old email>, --> *MANDATORY*
            "new_email" : <string: user's new email>, 
            "password" : <string: user's password>,
            "name" : <string: user's name>,
            "role" : <string: user's role>,
            "guild" : <string: user's guild>,
            "git_token" : <string: user's git access token>,
            "multiplier" : <int: user's multiplier>
        }

        Should you require to change the email, specify it as the value for the new_email key and include the old email as the value for the email key
    """
    try:

        processed_json = { k: v for k, v in request.json.items() if v }
        if bool(processed_json):
            user_ref = db.collection(u"User")
            doc_id = list(user_ref.where("email", "==", request.json["email"]).stream())[0].id

            if "new_email" in processed_json:
                processed_json["email"] = processed_json["new_email"]
                processed_json.pop('new_email', None)

            user_ref.document(doc_id).update(processed_json)

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        print(e)
        return {
            "error": "Cannot modify user"
        }, 500

# Update user exp + level (inc/dec) - CHECKED
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
        # Get the user object
        user_ref = db.collection(u"User")
        doc = list(user_ref.where("email", "==", request.json["email"]).stream())[0]

        # Check if the user is trying to add or delete exp from the user object
        if action == "inc":

            # Multiply the current exp by the user's multiplier 
            exp_to_add = request.json["exp"] * doc.to_dict()["multiplier"]

            print(doc.to_dict()["exp"] + exp_to_add)
            
            # Check if the amount of exp is above the bare minimum to increase one level
            if (doc.to_dict()["exp"] + exp_to_add) > 100:

                # Check if there is more than one level increase 
                level_inc = (doc.to_dict()["exp"] + exp_to_add) // 100

                # Obtain the new exp 
                new_exp = doc.to_dict()["exp"] + exp_to_add - (100 * level_inc)

                # Update the new exp and level
                user_ref.document(doc.id).update({u'exp': new_exp, u'level': doc.to_dict()["level"] + level_inc})

            else:
                # If there is no increase across levels, just add the exp to user's original exp 
                user_ref.document(doc.id).update({u'exp': doc.to_dict()["exp"] + exp_to_add})

        else:
            # Check if the user has to be de-leveled when the exp is minus off
            if doc.to_dict()["exp"] - request.json["exp"] < 0:
                # Check if the user is level one (minimum level)
                if doc.to_dict()["level"] == 1:
                    # Ensure that the user does not go below level 1 and 0 exp 
                    new_level = 1
                    new_exp = 0
                else:
                    # If user is above level 1, then proceed to deduct one level and the necessary exp
                    new_level = doc.to_dict()["level"] - 1
                    new_exp = 100 + doc.to_dict()["exp"] - request.json["exp"]
                
                # Update the new values 
                user_ref.document(doc.id).update({u'exp': new_exp, u'level': new_level})
            
            # If there is no decrease across levels, just deduct the exp from the user's original exp 
            else:
                user_ref.document(doc.id).update({u'exp': doc.to_dict()["exp"] - request.json["exp"]})
        
        # Get updated copy of the document to return the new values 
        updated_doc = user_ref.document(doc.id).get().to_dict()

        return jsonify({
            "new_level" : updated_doc["level"], 
            "new_exp" : updated_doc["exp"]
        }), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot update user statistics."}, 500

# Login function 
@app.route('/login', methods=['POST'])
def login():
    """
        Authenticate the user and return their email address to be used as session token.
        
        Expected JSON object:
        {
            "email" : <string: user's email>,
            "password" : <int: user's password>,
        }
    """
    try:
        user_ref = db.collection(u"User")
        
        email_verification = list(user_ref.where("email", "==", request.json["email"]).stream())

        if len(email_verification) > 0:
            if email_verification[0].to_dict()["password"] == request.json["password"]:
                return {
                    "email" : request.json["password"]
                }, 200
            else:
                return {
                    "error" : "Password incorrect."
                }, 401
        else:
            return {
                "error" : "Email does not exist."
            }, 401

    except Exception as e:
        print(e)
        return {"error": "Cannot authenticate specified user."}, 500

# =========================== # 
#      HYBRID FUNCTIONS       #
# =========================== # 
# Functions that require the accessing of various collections and mostly rely on other functions.

# Update multiplier for specified user 
@app.route("/update_multiplier", methods=["POST"])
def update_multiplier():
    """
        Function used to update the user's multiplier. 
        
        Expected JSON object:
        {
            "email" : <string: user's email>
        }

        Multiplier function: [(streak/10) * level] 
        - But if streak is found to be 0, then multiplier will automatically be 1
    """
    try: 
        # Get the user object
        res_user = requests.get("http://0.0.0.0:5001/get_user?email=" + request.json["email"])

        # Get the guild object 
        res_guild = requests.get("http://0.0.0.0:5001/get_guild?name=" + res_user.json()["guild"])

        # Recalculate multiplier - Check if streak is 0 and return a 1 for new multiplier 
        if res_guild.json()["streak"] == 0:
            multiplier = 1
        else:
            multiplier = math.ceil(res_guild.json()["streak"] / 10 * res_user.json()["level"])
        
        # Update multiplier 
        requests.post("http://0.0.0.0:5001/modify_user", json = {"email" : request.json["email"], "multiplier" : multiplier})

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        print(e)
        return {"error": "Cannot update multiplier."}, 500

# Complete tasks function 
@app.route("/complete_task", methods=["POST"])
def complete_task():
    """
        Function used to mark task as complete and update the associated users exp and guild streak accordingly. 
        
        Expected JSON object:
        {
            "id" : <string: task's name>,
            "email" : <string: email address of the user who hit complete>
        }
    """
    try:
        # Get the task object using /get_task function 
        response = requests.get("http://0.0.0.0:5001/get_task?id=" + request.json["id"])

        # Initialize the necessary variables 
        end = response.json()["end"]
        users = response.json()["assignedTo"]
        guild = response.json()["guild"]

        # Get the corresponding exp based on task priority
        exp = EXP_CONST[response.json()["priority"]]

        # Check if the current datetime is more than the end datetime == means that the task is overdue
        if datetime.now() > datetime.strptime(end, "%a, %d %b %Y %H:%M:%S GMT"):

            # Delete those exp from the user 
            for user in users:
                res_update = requests.post("http://0.0.0.0:5001/update_user_stats/del", json = {"email" : user, "exp" : exp})
                # Check if the user being updated is the one who "completes" the project
                if user == request.json["email"]:
                    user_stats = res_update.json()
            
            # Remove the guild's streak
            requests.post("http://0.0.0.0:5001/update_guild_streak/del", json = {"name" : guild})
        
        # When task is not overdue...
        else:

            # Increase exp for the user 
            for user in users:
                res_update = requests.post("http://0.0.0.0:5001/update_user_stats/inc", json = {"email" : user, "exp" : exp})
                # Check if the user being updated is the one who "completes" the project
                if user == request.json["email"]:
                    user_stats = res_update.json()
            
            # Add onto the guild's streak 
            requests.post("http://0.0.0.0:5001/update_guild_streak/inc", json = {"name" : guild, "toAdd": exp // 5})
        
        # Update the multiplier for every assigned user 
        for user in users:
            requests.post("http://0.0.0.0:5001/update_multiplier", json = {"email" : user})

        # Mark task as complete 
        requests.post("http://0.0.0.0:5001/modify_task", json={"id" : request.json["id"], "status" : True})
        
        return user_stats, 200

    except Exception as e:
        print(e)
        return {"error": "Cannot mark task as complete."}, 500
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)