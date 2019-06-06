# Overwatch League Score Predictor

A custom bayesian network model for predictions.

Predicts past and future matches based on the data parsed from the official overwatch league api (api.overwatchleague.com/).


Prediction Accuracy on OWL 2019 Stage 2 Games: 

   - Average Win/Lose Accuracy - 74% 
   - Average Match Score Accuracy - 42%

Environment: 

    Python 2.x

Usage: 

    python predict.py
   
    Options:
     -c  --collect     Collect new data from OWL api.
     -m  --manual      Run a single match prediction with maunal inputs.
     -n  --new         Batch run match predictions on a future week's schedule.
     -s  --show        Display a list of team names and abbrs.


Sample Output:
   
   Boston Uprising         |   Los Angeles Gladiators  |  Score: 0-0  |  Prediction: 1-3 
   

Model:
   
  (Graph N/A) 

