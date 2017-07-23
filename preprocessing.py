import spacy
import pandas as pd

# load data
data = pd.read_csv("data/2016_2017_Edmunds_cust_reviews_26032017.csv", sep=";")
docs = list(data.review[0:8749])

# load english
nlp = spacy.load("en")

# parse reviews
parsed = []
for doc in docs:
    parsed.append(nlp(doc))

# parse dependencies
dependency_parsed = []
id_review = 1
for review in parsed:
    sentences = review.sents
    id_sentence = 1
    for sentence in sentences:
        for word in sentence:
            dependency_parsed.append([id_review, id_sentence, word.dep_, word.head.pos_, word.pos_, word.head.text, word.text, word.dep_ + "(" + word.head.pos_ + ", " + word.pos_ + ")"])
        id_sentence = id_sentence +1    
    id_review = id_review + 1

# insert headers
dependency_parsed.insert(0, ["id_review", "id_sentence", "dependency", "POS head", "POS word", "head", "word", "concat"])

# create dataframe with parsed dependencies
df_dep = pd.DataFrame.from_records(dependency_parsed)
df_dep.columns = df_dep.iloc[0]
df_dep = df_dep[1:] #take the data less the header row

# convert all to lower case
df = df_dep[["id_review", "id_sentence", "concat", "head", "word"]].copy()
df = df.apply(lambda x: x.astype(str).str.lower())

# list of patterns that will be needed for generating opinion phrases
patterns = [
    "amod(noun, adj)",
    "acomp(verb, adj)",
    "nsubj(verb, noun)",
    "relcl(noun, verb)",
    "neg(adj, adv)",
    "compound(noun, noun)",
    "nsubj(adj, noun)",
    "conj(adj, verb)",
    "dobj(verb, noun)",
    "conj(adj, adj)",
    "conj(noun, noun)",
    "xcomp(noun, verb)"]

# filters dataframe based on list of patterns
df_clean = df.loc[df['concat'].isin(patterns)]

df_clean.to_csv("output/preprocessed.csv")



