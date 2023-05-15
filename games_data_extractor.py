import requests
import pandas as pd
from config import token,school_link,piscine_object_name
import numpy as np

import os

from datetime import datetime,timedelta

from pprint import pprint

#request bearer token from /api/auth/token
token_request = requests.get(school_link+"/api/auth/token",params={"token":token})
bearer_token = token_request.json()


#get list of trgeted piscine events
headers = {"Authorization":"Bearer "+bearer_token,'Content-Type': 'application/json'}
toad_session_query = {"query":'''
  {toad_sessions{
  candidate{
    id
    login
    firstName
    lastName
    email
    attrs
  }
  created_at
  updated_at
  final_score
  games{
    results(order_by:{level:desc},limit:1)
    {
      level
      result{
  			name
      }
    }
  }
}}
'''}
toad_sessions= requests.post(school_link+"/api/graphql-engine/v1/graphql",headers=headers,json=toad_session_query).json()['data']["toad_sessions"]




toad_seesion_decision_query = {"query":'''
{
  progress(where: {object: {name: {_eq: "Online Cognitive Games"}}}) {
    userId
    userLogin
    grade
  }
}
'''
}

toad_seesion_decision = requests.post(school_link+"/api/graphql-engine/v1/graphql",headers=headers,json=toad_seesion_decision_query).json()['data']["progress"]

organized_data = {}

#extarct and calculate the data to put in the dictionary


for session in toad_sessions:
    try:
        organized_data[session["candidate"]["id"]] = {
            "username" : session["candidate"]["login"],
            "firstName" : session["candidate"]["firstName"],
            "lastName" : session["candidate"]["lastName"],
            "gender" : session["candidate"]["attrs"]["gender"] ,
            "email" : session["candidate"]["email"],
            "phoneNumber" : session["candidate"]["attrs"]["Phone"] ,
            "city" : session["candidate"]["attrs"]["city"] ,
            "toad_game_score in %" : session["final_score"],
            "memory_game_lvl" : np.nan,
            "zzle_game_lvl" :np.nan,
            "started_at": datetime.strptime(session["created_at"], '%Y-%m-%dT%H:%M:%S.%f%z'),
            "last_active_time": datetime.strptime(session["updated_at"], '%Y-%m-%dT%H:%M:%S.%f%z'),
            "prgress": "in progress"
        }
        for game in session["games"]:
            try:
                if game["results"][0]["result"]["name"] == "memory":
                    organized_data[session["candidate"]["id"]]["memory_game_lvl"] = game["results"][0]["level"]
                elif game["results"][0]["result"]["name"] == "zzle":
                    organized_data[session["candidate"]["id"]]["zzle_game_lvl"] = game["results"][0]["level"]
            except:
                a=1
    except:
        a = 1


for result in toad_seesion_decision:
    grade = result["grade"]

    if grade == 0:
        organized_data[result["userId"]]["prgress"] = "rejected"
    elif grade == 1:
        organized_data[result["userId"]]["prgress"] = "accepted"
    elif grade == None and organized_data[result["userId"]]["toad_game_score in %"] != None:
        organized_data[result["userId"]]["prgress"] = "waiting for selection"
    elif grade == None:
        organized_data[result["userId"]]["prgress"] = "in progress"

    # "memory_game_lvl" : session[][][],
    # "zzl_game_lvl" : session[][][],

#organise comlumns to extract as an excel file

for id in organized_data:
  organized_data[id]["last_active_time"] = (organized_data[id]["last_active_time"] + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")
  organized_data[id]["started_at"] = (organized_data[id]["started_at"] + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")

data=[organized_data[id] for id in organized_data]
columns = [  "username",
    "firstName",
    "lastName", 
    "gender", 
    "email",
    "phoneNumber", 
    "city", 
    "toad_game_score in %", 
    "memory_game_lvl", 
    "zzle_game_lvl", 
    "started_at",
    "last_active_time",
    "prgress"]

table = pd.DataFrame.from_dict(data)[columns]
# pprint(table)
table.to_excel("toad_games_results.xlsx",freeze_panes=(1,0))
#extarct to excel file 
# table.to_excel("%s_%d.xlsx"%(piscine_object_name,piscine_id),freeze_panes=(1,0))

