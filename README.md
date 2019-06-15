# Overwatch League Score Predictor

A custom bayesian network model for predictions.

Predicts past and future matches based on the data parsed from the official overwatch league api (api.overwatchleague.com/).


**Prediction Accuracy on OWL 2019 Stage 2 Games:** 

   - Average Win/Lose Accuracy - 74% 
   - Average Match Score Accuracy - 42%


**Requirement:** 

    Python: Python 2.x
    Packages: Numpy, Pillow
    
    pip install -r requirements.txt


**Usage:** 

    python predict.py
   
    Options:
    
     -c  --collect     Collect new data from OWL api
     -l  --list        Display a list of team names and abbrs
     
     -m  --manual      Run a single match prediction with maunal inputs
     -n  --new         Batch run match predictions on a future week's schedule
     -s  --stage       Specify Stage
     -w  --week        Specify Week
     
     -e  --eval        Evaluate output results
     -i  --image       Enable image output



**Sample Output:**
   
   * Text:
   
      <img src="https://github.com/TianyangZhan/OverwatchLeaguePredictor/blob/master/TextOutput.jpg" width="500">
   * Image:
   
      <img src="https://github.com/TianyangZhan/OverwatchLeaguePredictor/blob/master/image_results/Stage3_Week1.jpg" width="500">
   



**Bayesian Network Model:**
   
![Alt text](https://github.com/TianyangZhan/OverwatchLeaguePredictor/blob/master/Model.jpg?raw=true "Title")

