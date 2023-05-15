import requests
import pandas as pd
from config import token,school_link,piscine_object_name

import os

from datetime import datetime,timedelta

from pprint import pprint

#request bearer token from /api/auth/token
token_request = requests.get(school_link+"/api/auth/token",params={"token":token})
bearer_token = token_request.json()


#get list of trgeted piscine events
headers = {"Authorization":"Bearer "+bearer_token,'Content-Type': 'application/json'}
get_piscines = {"query":'''
  {event(where:{object:{name:{_eq:"%s"}}}) {
    createdAt
    endAt
    id
    object{
      id
      name
    }
  }}
'''%(piscine_object_name)}
piscines = requests.post(school_link+"/api/graphql-engine/v1/graphql",headers=headers,json=get_piscines).json()['data']['event']


d = -1
os.system('clear')

#if no piscine event exists, exit from the script. 
if len(piscines) == 0:
  print("No piscine is ascociated with object:\t%s"%piscine_object_name)
  exit()

#loop to choose the desired event
while d < 0 or d >= len(piscines):
  for i in range(len(piscines)):
    print("%d- id: %d\n\tstart:%s\n\tend:%s\n\n"%(i,piscines[i]['id'],piscines[i]['createdAt'],piscines[i]['endAt']))
  try:
    d = int(input("what piscine index you want to get data from: "))
  except:
    pass




piscine_id = piscines[d]['id']
object_id = piscines[d]["object"]["id"]



#quesry to get all needed data
get_data = {"query":'''
{progress(where:{_and:[{event:{id:{_eq:%d}}}, {object:{parents:{parent:{type:{_eq:"quest"}}}}}]},
){
    user {
      id
      firstName
      lastName
      email
      phoneNumber: attrs(path: "Phone")
    }
    userLogin
    updatedAt
    grade
    object {
      name
      parents(where:{parent:{type:{_eq:"quest"}}}) {
        parent {
          name
        }
      }
    }
  }
}
'''%(piscine_id)
}

data = requests.post(school_link+"/api/graphql-engine/v1/graphql",headers=headers,json=get_data).json()['data']

organized_data = {}

#extarct and calculate the data to put in the dictionary


for prog in data["progress"]:
  updated_at = datetime.strptime(prog["updatedAt"], '%Y-%m-%dT%H:%M:%S.%f%z')
  user_id = prog['user']['id']
  if user_id in organized_data:
    if organized_data[user_id]["last_update"] < updated_at:
      organized_data[user_id]={
        "username":prog['userLogin'],
        "firstname":prog['user']['firstName'],
        "lastname":prog['user']['lastName'],
        "email":prog['user']['email'],
        "phone_number":prog['user']['phoneNumber'],
        "last_update":updated_at,
        "exercise":prog['object']['name'],
        "quest":prog['object']['parents'][0]['parent']['name'],
        "grade":prog['grade']
      }
  else:
    organized_data[user_id]={
      "username":prog['userLogin'],
      "firstname":prog['user']['firstName'],
      "lastname":prog['user']['lastName'],
      "email":prog['user']['email'],
      "phone_number":prog['user']['phoneNumber'],
      "last_update":updated_at,
      "exercise":prog['object']['name'],
      "quest":prog['object']['parents'][0]['parent']['name'],
      "grade":prog['grade']
    }



#organise comlumns to extract as an excel file

for id in organized_data:
  organized_data[id]["last_update"] = (organized_data[id]["last_update"] + timedelta(hours=3)).strftime("%m/%d/%Y, %H:%M:%S")

data=[organized_data[id] for id in organized_data]
columns = ["username","firstname","lastname","email","phone_number","last_update","exercise","quest","grade"]

table = pd.DataFrame.from_dict(data)[columns]
pprint(table)
table.to_excel("%s_%d_last_activity_data.xlsx"%(piscine_object_name,piscine_id),freeze_panes=(1,0))
#extarct to excel file 
# table.to_excel("%s_%d.xlsx"%(piscine_object_name,piscine_id),freeze_panes=(1,0))


# #add colors to the excel file
# import openpyxl
# from openpyxl.styles import PatternFill,Border,Side

# wb = openpyxl.load_workbook("%s_%d.xlsx"%(piscine_object_name,piscine_id)) 
# ws = wb['Sheet1']

# ws.delete_cols(1)

# grey = PatternFill(patternType='solid', fgColor='4F5A5E')
# header_color = PatternFill(patternType='solid', fgColor='80B0C8')
# raid_color = PatternFill(patternType='solid', fgColor='78B7B7')
# raids_color = PatternFill(patternType='solid', fgColor='20DAA5')
# exam_color1 = PatternFill(patternType='solid', fgColor='C6DFE7')
# exam_color2 = PatternFill(patternType='solid', fgColor='0C95C8')
# login_color = PatternFill(patternType='solid', fgColor='78B7B7')
# gender_color = PatternFill(patternType='solid', fgColor='AC84E8')
# level_color = PatternFill(patternType='solid', fgColor='C2CCA6')
# xp_color = PatternFill(patternType='solid', fgColor='E59B86')
# quests_color = PatternFill(patternType='solid', fgColor='F6E5BC')

# red = PatternFill(patternType='solid', fgColor='FF0000')
# orange = PatternFill(patternType='solid', fgColor='F78C11')
# yellow  = PatternFill(patternType='solid', fgColor='fce005')
# grean = PatternFill(patternType='solid', fgColor='2FEB32')
# Blue_sky = PatternFill(patternType='solid', fgColor='2FB6EB')

# grade_colors = [red,orange,yellow,grean,Blue_sky,Blue_sky,Blue_sky]

# thin_border = Border(left=Side(style='thin'), 
#                   right=Side(style='thin'), 
#                   top=Side(style='thin'), 
#                   bottom=Side(style='thin'))


# r = 1
# for row in ws.iter_rows():
#   c = 1
#   for cell in row:
#     if cell.internal_value is None:
#       cell.fill = grey
#     elif r == 1:
#       cell.fill = header_color
#     elif c == 1:
#       cell.fill = login_color
#     elif c == 2:
#       cell.fill = gender_color
#     elif c == 3:
#       cell.fill = xp_color
#     elif c == 4:
#       cell.fill = level_color
#     elif c == 5:
#       cell.fill = quests_color
#     elif c == raid_index:
#       cell.fill = raid_color
#     elif c > raid_index and  c <= raid_index + len(raids) :
#       if cell.internal_value >= 100:
#         cell.fill = Blue_sky
#       else:
#         cell.fill = raids_color
#     elif c > raid_index + len(raids):
#       if ((c - raid_index - len(raids) - 1)//2)%2 ==0:
#         if (c - raid_index - len(raids) - 1) % 2 ==0:
#           cell.fill = grade_colors[int(cell.internal_value)//20]
#         else:
#           cell.fill = exam_color1
#       else:
#         if (c - raid_index - len(raids) - 1) % 2 ==0:
#           cell.fill = grade_colors[int(cell.internal_value)//20]
#         else:
#           cell.fill = exam_color2
#     cell.border = thin_border  
#     c+=1
#   r+=1
# ws.freeze_panes = 'B2'

# wb.save("%s__%d.xlsx"%(piscine_object_name,piscine_id))
# print("data output file name is %s"%"%s__%d.xlsx"%(piscine_object_name,piscine_id))

