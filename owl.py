import urllib
import os
import json, csv, collections
import argparse

class OwlData:

    def __init__ (self):
        self.teamdata = {}
        self.playerdata = {}
        self.table = [{}]
        self.schedule = []
        self.stage = ""
        self.week = ""


    def to_dict(self):
        teams = []
        for i in range(len(self.teamdata["data"])):
            temp = {}
            temp["name"] = self.teamdata["data"][i]["name"]
            temp["abbr"] = self.teamdata["data"][i]["abbreviatedName"]
            temp["matchWin"] = self.teamdata["data"][i]["league"]["matchWin"]
            temp["matchLoss"] = self.teamdata["data"][i]["league"]["matchLoss"]
            temp["matchDraw"] = self.teamdata["data"][i]["league"]["matchDraw"]
            temp["gameWin"] = self.teamdata["data"][i]["league"]["gameWin"]
            temp["gameLoss"] = self.teamdata["data"][i]["league"]["gameLoss"]
            temp["gameTie"] = self.teamdata["data"][i]["league"]["gameTie"]
            
            temp["dpsK/D"] = self.playerdata[int(self.teamdata["data"][i]["id"])]["offense"][0] / self.playerdata[int(self.teamdata["data"][i]["id"])]["offense"][1]
            temp["dpsUlt/10mins"] = self.playerdata[int(self.teamdata["data"][i]["id"])]["offense"][3] / self.playerdata[int(self.teamdata["data"][i]["id"])]["offense"][4]
            temp["tankK/D"] = self.playerdata[int(self.teamdata["data"][i]["id"])]["tank"][0] / self.playerdata[int(self.teamdata["data"][i]["id"])]["tank"][1]
            temp["tankUlt/10mins"] = self.playerdata[int(self.teamdata["data"][i]["id"])]["tank"][3] / self.playerdata[int(self.teamdata["data"][i]["id"])]["tank"][4]
            temp["supportHealing"] = self.playerdata[int(self.teamdata["data"][i]["id"])]["support"][2] / self.playerdata[int(self.teamdata["data"][i]["id"])]["support"][4]
            temp["supportUlt/10mins"] = self.playerdata[int(self.teamdata["data"][i]["id"])]["support"][3] / self.playerdata[int(self.teamdata["data"][i]["id"])]["support"][4]
            
            teams.append(temp)
        self.table = teams


    def get_teamdata(self):
        url = urllib.urlopen("https://api.overwatchleague.com/v2/standings?locale=en_US")
        teamdata = json.loads(url.read().decode())
        self.teamdata = teamdata


    def get_playerdata(self):
        url = urllib.urlopen("https://api.overwatchleague.com/stats/players?stage_id=regular_season")
        data = json.loads(url.read().decode())
        hashmap = {}
        for i in range(len(data["data"])):
            if not data["data"][i]["teamId"] in hashmap:
                hashmap[data["data"][i]["teamId"]] = {}
            if not data["data"][i]["role"] in hashmap[data["data"][i]["teamId"]]:
                hashmap[data["data"][i]["teamId"]][data["data"][i]["role"]] = [0,0,0,0,0]
            
            hashmap[data["data"][i]["teamId"]][data["data"][i]["role"]][0] += data["data"][i]["eliminations_avg_per_10m"]
            hashmap[data["data"][i]["teamId"]][data["data"][i]["role"]][1] += data["data"][i]["deaths_avg_per_10m"]
            hashmap[data["data"][i]["teamId"]][data["data"][i]["role"]][2] += data["data"][i]["healing_avg_per_10m"]
            hashmap[data["data"][i]["teamId"]][data["data"][i]["role"]][3] += data["data"][i]["ultimates_earned_avg_per_10m"]
            #total player count
            if data["data"][i]["eliminations_avg_per_10m"]:
                hashmap[data["data"][i]["teamId"]][data["data"][i]["role"]][4] += 1
        self.playerdata = hashmap


    def get_schedule(self,curr_stage = -1, curr_week = -1):

        url = urllib.urlopen("https://api.overwatchleague.com/schedule")
        schedule = json.loads(url.read())
        
        if curr_stage == -1:
            curr_stage = len(schedule["data"]["stages"])-1
            while curr_stage >= 0:
                if len(schedule["data"]["stages"][curr_stage]["matches"]) > 0 and schedule["data"]["stages"][curr_stage]["matches"][-1]["state"] != "CONCLUDED":
                    if curr_stage <= 0 or schedule["data"]["stages"][curr_stage-1]["matches"][-1]["state"] == "CONCLUDED":
                        break
                curr_stage -= 1

        if curr_week == -1:
            curr_week = len(schedule["data"]["stages"][curr_stage]["weeks"])-1
            while curr_week >= 0:
                if len(schedule["data"]["stages"][curr_stage]["weeks"][curr_week]["matches"]) > 0 and schedule["data"]["stages"][curr_stage]["weeks"][curr_week]["matches"][-1]["state"] != "CONCLUDED":
                    if curr_week <= 0 or schedule["data"]["stages"][curr_stage]["weeks"][curr_week-1]["matches"][-1]["state"] == "CONCLUDED":
                        break
                curr_week -= 1

        self.stage = schedule["data"]["stages"][curr_stage]["name"].replace(" ","")
        self.week = schedule["data"]["stages"][curr_stage]["weeks"][curr_week]["name"].replace(" ","")
        self.schedule = [(d["competitors"][0]["name"],d["competitors"][1]["name"],str(d["scores"][0]["value"])+"-"+str(d["scores"][1]["value"])) for d in schedule["data"]["stages"][curr_stage]["weeks"][curr_week]["matches"] if d["competitors"][0]]

    def check_schedule(self,stg,wk):
        url = urllib.urlopen("https://api.overwatchleague.com/schedule")
        schedule = json.loads(url.read())
    
        return [str(d["scores"][0]["value"])+"-"+str(d["scores"][1]["value"]) for d in schedule["data"]["stages"][stg]["weeks"][wk]["matches"] if d["competitors"][0]]

    def save_to_file(self,fileName):
        colname = self.table[0].keys()
        with open(fileName, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, colname)
            dict_writer.writeheader()
            dict_writer.writerows(self.table)


    def read_from_file(self,fileName):
        with open(fileName) as f:
            content = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]
        self.table = content



