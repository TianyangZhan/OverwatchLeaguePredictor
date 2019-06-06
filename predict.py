import urllib
import os, time
import json, csv, collections
import argparse
from owl import OwlData


def naive_bayesian(teamData, teamA, teamB, flip):

    flipped = flip

    # bayesian network settings
    offensePlay = [0.2,0.4,0.5,0.7,0.5,0.6,0.7,0.9] # P(offensePlay | dpsBetter, tankBetter, supportBetter), [FFF,FFT,FTF,FTT,TFF,TFT,TTF,TTT]
    defensePlay = [0.3,0.4,0.6,0.6,0.3,0.5,0.6,0.9] # P(dffensePlay | dpsBetter, tankBetter, supportBetter), [FFF,FFT,FTF,FTT,TFF,TFT,TTF,TTT]
    winOD = [0.8, 0.7, 0.6, 0.35] # P(win | offensePlay, defensePlay), [TT, TF, FT, FF]

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
    
    index = (4*dpsBetter+2*tankBetter+supportBetter)
    if index <= 0:
        index += 4*(AWinRate[0] > BWinRate[0]) + (AWinRate[1] > BWinRate[1])
    index = int(min(max(0,index),7))

    try:
        win = winOD[0]*offensePlay[index]*defensePlay[index] + winOD[1]*(1-offensePlay[index])*defensePlay[index] + winOD[2]*offensePlay[index]*(1-defensePlay[index]) + winOD[3]*(1-offensePlay[index])*(1-defensePlay[index])
        lose = (1-winOD[0])*offensePlay[index]*defensePlay[index] + (1-winOD[1])*(1-offensePlay[index])*defensePlay[index] + (1-winOD[2])*offensePlay[index]*(1-defensePlay[index]) + (1-winOD[3])*(1-offensePlay[index])*(1-defensePlay[index])
    except:
        print index

    win /= (win+lose)
    return win, flipped

def collectdata(owl):
    owl.get_playerdata()
    owl.get_teamdata()
    owl.to_dict()
    owl.save_to_file("OWL.csv")
    owl.read_from_file("OWL.csv")

def predict(owl,A,B):
    try:
        win,flp = naive_bayesian(owl.table,A,B,0)
    except:
        print "Error when accessing team data, please check input team names"

    score = ""
    if win > 0.63:
        score = " 4-0 "
    elif win > 0.53:
        score = " 3-1 "
    else:
        score = " 3-2 "

    if flp == 1:
        score = score[::-1]
    return [A,score,B]

def predictAll(owl):
    owl.get_schedule()
    filename = "./results/"+owl.stage+"_"+owl.week+"_"+time.strftime("%Y%m%d")+".txt"
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
        f.write("{:<22}".format(A)+"  |   "+"{:<22}".format(B)+"     Score: "+S+" Prediction: "+P+" \n\n")
    f.close()

    if count != 0:
        print(str(correct*100/count)+"% total score accuracy, ("+str(int(correct))+" / "+str(int(count))+")")
        print(str(c*100/count)+"% total win accuracy, ("+str(int(c))+" / "+str(int(count))+")")

def inputpredict(owl,list):
    print("\n Enter \\ to show team list \n")
    while True:
        A = raw_input("Team A name/abbr: ").strip()
        if A == "\\":
            print '\n'.join(list)
            print "\n"
            continue
        B = raw_input("Team B name/abbr: ").strip()
        if B =="\\":
            print '\n'.join(list)
            print "\n"
            continue
        if A == B:
            print("Please Enter two different teams")
            continue
        res = predict(owl,A,B)
        if res :
            return res
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--collect', '-c',action='store_true', help="collect new data from OWL api")
    parser.add_argument('--manual', '-m',action='store_true', help="run a single match prediction with maunal inputs")
    parser.add_argument('--new', '-n',action='store_true', help="run a batch match predictions on a future week's schedule")
    parser.add_argument('--show', '-s',action='store_true', help="display a list of team names and abbrs")
    args = parser.parse_args()
    
    
    owl = OwlData()
    try:
        owl.read_from_file("OWL.csv")
    except IOError:
        collectdata(owl)
        owl.read_from_file("OWL.csv")
    list = ["{:<22}".format(d["name"])+"  |  " + "{:<5}".format(d["abbr"]) for d in owl.table]

    if args.show:
        print '\n'.join(list)
    if args.collect:
        collectdata(owl)
    if args.manual:
        print inputpredict(owl,list)
    elif args.new:
        predictAll(owl)


if __name__ == "__main__":
    main()


