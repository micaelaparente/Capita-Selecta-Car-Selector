import pandas as pd
import json

phrases = pd.read_csv("output/final_opinion_phrases.csv")

with open('data/categories.json') as json_data:
    categories = json.load(json_data)
    for category in categories:
        phrases [category] = 0

def tagger (opinion, category):
    tags = []
    words = categories[category]
    for word in words:
        if word in opinion:
            tags.append(category)
    if len(tags) > 0:
        return 1
    else:
        return 0

for category in categories:    
    phrases[category] = phrases.opinion.map(lambda x: tagger(x, category))
    
phrases = phrases.groupby("brand_model_year").sum()

df = phrases.apply(lambda x: x/x.max(), axis=1).dropna()

df.index = df.index.map(lambda x: x.replace("_", " ").upper())

df.to_csv("app/tagged_op.csv")