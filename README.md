# Overwatch League Score Predictor

A custom bayesian network model for predictions.

Predicts past and future matches based on the data parsed from the official overwatch league api (api.overwatchleague.com/).


Currect Prediction Accuracy (OWL 2019 Stage 2): 

   - Win/Lose Accuracy - 68% 
   - Match Score Accuracy - 39.8%

Environment: 

    Python 2.x

Usage: 

    python owl.py
   
  Options:
  -c --collect     Collect new data from OWL api.
  -m --manual      Run a single match prediction with maunal inputs.
  -a --all         Batch run match predictions with inputs based on match schedule.
  -s --show        Display a list of team names and abbrs.


Sample Output:
   
   Boston Uprising         |   Los Angeles Gladiators  |  Score: 0-0  |  Prediction: 1-3 
   

Model:
   
  (Graph N/A) 

