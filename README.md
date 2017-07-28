# Car Selector

This is an [academic project](https://github.com/micaelaparente/Capita-Selecta-Car-Selector/blob/master/Capita%20Selecta%20Report.pdf) I developed for the course "Capita Selecta", as part of my Master's in Business Informatics at Utrecht University.
It takes as input user reviews of cars from 2016 and 2017, extracted from Edmunds.com, and outputs tagged cars according to their qualitative properties, such as "Affordable car", or "Sexy car".
Additionally, it also comprises a Shiny app ([see it live](https://mparente.shinyapps.io/car-selector/)) to play with different tags and see suggestions of cars.

## Getting Started

These instructions will get a copy of the project up and running on your local machine for testing purposes.

### Prerequisites

To run the car tagger, you will need:
```
Python 3
spaCy >= 1.8.2
Pandas >= 0.20.1
NLTK >= 3.2.3
```

If you also want to run the Shiny app, please install R libraries Shiny, dplyr, and readr. You can easily do it from R Studio's console:
```
install.packages("dplyr")
install.packages("shiny")
install.packages("readr")
```


## Running the car tagger (Python):

1. Download (or clone) the project
2. Run "preprocessing.py"
3. Run "op_generation.py"
4. Run "tagging.py"

After these steps, a CSV of tagged cars will be generated in "app" folder. The most exciting way to visualize it is to run the Shiny app on the same folder.

## Running the app (R):

1. Open "app.R" on R Studio
2. Click on "Run app", or simply run the file. This should run a local version of the app.

