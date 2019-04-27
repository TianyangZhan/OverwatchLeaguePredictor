import urllib
import os, time
import json, csv, collections

class OwlData:

    def __init__ (self, stage):
        self.teamdata = {}
        self.playerdata = {}
        self.table = [{}]
        self.schedule = []
        self.stage = stage-1

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

    def get_schedule(self):
        url = urllib.urlopen("https://api.overwatchleague.com/schedule")
        schedule = json.loads(url.read().decode())
        self.schedule = [(d["competitors"][0]["name"],d["competitors"][1]["name"],str(d["scores"][0]["value"])+"-"+str(d["scores"][1]["value"])) for d in schedule["data"]["stages"][self.stage]["matches"] if d["competitors"][0] != None ]

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


def naive_bayesian(teamData, teamA, teamB, flip):

    flipped = flip

    # bayesian network settings
    offensePlay = [0.2,0.4,0.5,0.7,0.5,0.6,0.7,0.9] # P(offensePlay | dpsBetter, tankBetter, supportBetter), [FFF,FFT,FTF,FTT,TFF,TFT,TTF,TTT]
    defensePlay = [0.3,0.4,0.6,0.6,0.3,0.5,0.6,0.9] # P(dffensePlay | dpsBetter, tankBetter, supportBetter), [FFF,FFT,FTF,FTT,TFF,TFT,TTF,TTT]
    winOD = [0.85, 0.6, 0.6, 0.3] # P(win | offensePlay, defensePlay), [TT, TF, FT, FF]

    # data parsing
    teamAData = [d for d in teamData if d["name"] == teamA or d["abbr"] == teamA][0]
    teamBData = [d for d in teamData if d["name"] == teamB or d["abbr"] == teamB][0]
    
    AMatchCount = int(teamAData["matchWin"]) + int(teamAData["matchLoss"])
    AWinRate = [int(teamAData["matchWin"])/float(AMatchCount), int(teamAData["matchLoss"])/float(AMatchCount)] # [win,loss], win+loss = 1
    BMatchCount = int(teamBData["matchWin"]) + int(teamBData["matchLoss"])
    BWinRate = [int(teamBData["matchWin"])/float(BMatchCount), int(teamBData["matchLoss"])/float(BMatchCount)] # [win,loss], win+loss = 1
    
    ddps = float(teamAData["dpsK/D"]) + float(teamAData["dpsUlt/10mins"]) - float(teamBData["dpsK/D"]) - float(teamBData["dpsUlt/10mins"])
    dtank = float(teamAData["tankK/D"]) + float(teamAData["tankUlt/10mins"]) - float(teamBData["tankK/D"]) - float(teamBData["tankUlt/10mins"])
    dsupport = float(teamAData["supportHealing"])/2000.0 + float(teamAData["supportUlt/10mins"]) - float(teamBData["supportHealing"])/2000.0 - float(teamBData["supportUlt/10mins"])

    if (ddps<0)+(dtank<0)+(dsupport < 0) >= 2:
        return naive_bayesian(teamData, teamB, teamA, 1)

    dpsBetter = 0
    tankBetter = 0
    supportBetter = 0
    
    if ddps > 1.1:
        dpsBetter = 1
    if dtank > 1.1:
        tankBetter = 1
    elif dtank < -1.1:
        tankBetter = -0.5
    if dsupport > 0.5:
        supportBetter = 1
    elif dsupport < -1:
        supportBetter = -1


    '''
    print("!!!!")
    print(ddps)
    print(dtank)
    print(dsupport)
    print(dpsBetter)
    print(tankBetter)
    print(supportBetter)
    '''
    
    index = (4*dpsBetter+2*tankBetter+supportBetter)
    if index == 0:
        index += 4*(AWinRate[0] > BWinRate[0]) + (AWinRate[1] > BWinRate[1])


    win = winOD[0]*offensePlay[index]*defensePlay[index] + winOD[1]*(1-offensePlay[index])*defensePlay[index] + winOD[2]*offensePlay[index]*(1-defensePlay[index]) + winOD[3]*(1-offensePlay[index])*(1-defensePlay[index])
    lose = (1-winOD[0])*offensePlay[index]*defensePlay[index] + (1-winOD[1])*(1-offensePlay[index])*defensePlay[index] + (1-winOD[2])*offensePlay[index]*(1-defensePlay[index]) + (1-winOD[3])*(1-offensePlay[index])*(1-defensePlay[index])

    win /= (win+lose)
    return win, flipped

def collectdata(owl):
    owl.get_playerdata()
    owl.get_teamdata()
    owl.to_dict()
    owl.save_to_file("OWL.csv")

def predict(owl,A,B):
    owl.read_from_file("OWL.csv")
    
    try:
        win,flp = naive_bayesian(owl.table,A,B,0)
    except Exception:
        print("Invalid Team Name")
        return []

    score = ""
    if win > 0.63:
        score = " 4-0 "
    elif win > 0.44:
        score = " 3-1 "
    else:
        score = " 3-2 "

    if flp == 1:
        score = score[::-1]
    return [A,score,B]

def predictAll(owl):
    owl.get_schedule()
    filename = "./results/prediction"+time.strftime("%Y%m%d-%H%M%S")+".txt"
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    f = open(filename, "a")
    count = 0.0
    correct = 0.0
    c = 0.0
    for (A,B,S) in owl.schedule:
        P = predict(owl,A,B)[1].strip()
        if S != "0-0":
            count += 1
            if S == P:
                correct += 1
            if P != "0-0" and (S[0] > S[2]) == (P[0] > P[2]):
                c += 1
        f.write(A+" vs "+B+"        Real Score: "+S+" Predicted Score: "+P+" \n\n")
    f.close()
    print(str(correct*100/count)+"% total score accuracy")
    print(str(c*100/count)+"% total win accuracy")

def inputpredict(owl):
    A = raw_input("Team A name/abbr: ").strip()
    B = raw_input("Team B name/abbr: ").strip()
    if A == B:
        print("Please Enter two different teams")
        return []
    return predict(owl,A,B)

def main():
    owl = OwlData(2)
    #collectdata(owl)
    predictAll(owl)
    #print(inputpredict(owl))


if __name__ == "__main__":
    main()



