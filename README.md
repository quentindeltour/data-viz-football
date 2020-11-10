# data-viz-football

This repo presents the code for an app of datavisualisation of football Data using Dash. 

## Actual app

The data are gathered on [this site](https://www.football-data.co.uk/). It provides extensive access to match history in major (and alos minor, but I have not considered them) european football leagues, such as Premier League (England), Bundesliga (Germany), Ligue 1 (France), Liga (Spain) and Serie A (Italy). 

This histories are updated frequently. 

The app was created using Dash and Dash bootstrap component for the css styles and components. It has be hosted on Heroku.

It is available at the following link : https://resultats-football-app.herokuapp.com/Home

You can select one of the ten supported championships on the navigation bar (top right).

The app is then composed of 4 different pages : 

- `HomePage` presents the current ranking for the ongoing season on the selected championship
- `Statistiques Championnats` shows some stats on the championship : best attacks and defense, aswell as plotting the repartition of scores (Home, Away or Draw) and the repartition of goals (Home vs Away & First Half vs Second Half). 
- `Statistiques par équipes` shows more advanced statistics on teams : the number of shots, shots on target, goals, yellow cards and red cards. 
- `Face à Face` is the page where you can compare the opposition of two different teams. You will get access to some statistics (shots, goals, cards etc. ) and the last confrontations between both teams. 

## In development : 

Another page showing statistics for a specific team (last matches results and statistics). 

