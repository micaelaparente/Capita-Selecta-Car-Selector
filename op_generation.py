import pandas as pd
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import spacy


df_clean = pd.read_csv("output/preprocessed.csv")

# initiate dictionary for adjectices and antonyms
adj_ant = {}

for i in wn.all_synsets():
    if i.pos() in ['a', 's']: # If synset is adj or satelite-adj.
        for j in i.lemmas(): # Iterating through lemmas for each synset.
            if j.antonyms(): # If adj has antonym.
                # Populate dictionary with adjectives and antonyms
                adj_ant[j.name()] = j.antonyms()[0].name()


op = pd.DataFrame(columns=["id_review", "id_sentence", "term", "modifier", "rule"])

# PAIRS

# 1. amod(noun, adj) -> <noun, adj>
amod_na = df_clean[df_clean["concat"] == "amod(noun, adj)"].filter(items = ["id_review", "id_sentence", "head", "word"]).reset_index(drop=True)
amod_na["rule"] = "rule1"
op = pd.concat([op, amod_na.rename(columns={'head':'term', 'word':'modifier'})], ignore_index=True)

# 2. acomp(verb, adj) + nsubj(verb, noun) -> <noun, adj>
acomp_va = df_clean[df_clean["concat"] == "acomp(verb, adj)"].rename(columns = {"head":"verb", "word":"adj"}).filter(items = ["id_review", "id_sentence", "verb", "adj"]).reset_index(drop=True)
nsubj_vn = df_clean[df_clean["concat"] == "nsubj(verb, noun)"].rename(columns = {"head":"verb", "word":"noun"}).filter(items = ["id_review", "id_sentence", "verb", "noun"]).reset_index(drop=True)
rule2 = nsubj_vn.merge(acomp_va, on=["id_review", "id_sentence", "verb"]).filter(items = ["id_review", "id_sentence", "noun", "adj"])
rule2["rule"] = "rule2"
op = pd.concat([op,rule2.rename(columns={'noun':'term', 'adj':'modifier'})], ignore_index=True).reset_index(drop=True)

# 3. conj(adj, verb) + nsubj(adj, noun) -> <noun, adj>
conj_av = df_clean[df_clean["concat"] == "conj(adj, verb)"].rename(columns = {"head":"adj", "word":"verb"}).filter(items = ["id_review", "id_sentence", "adj", "verb"]).reset_index(drop=True)
nsubj_an = df_clean[df_clean["concat"] == "nsubj(adj, noun)"].rename(columns = {"head":"adj", "word":"noun"}).filter(items = ["id_review", "id_sentence", "adj", "noun"]).reset_index(drop=True)
rule3 = nsubj_an.merge(conj_av, on=["id_review", "id_sentence", "adj"]).filter(items = ["id_review", "id_sentence", "noun", "adj"])
rule3["rule"] = "rule3"
op = pd.concat([op,rule3.rename(columns={'noun':'term', 'adj':'modifier'})], ignore_index=True).reset_index(drop=True)

# 4. dobj(verb, noun1) + nsubj(verb, noun2) -> <noun, verb>
dobj_vn = df_clean[df_clean["concat"] == "dobj(verb, noun)"].rename(columns = {"head":"verb", "word":"noun"}).filter(items = ["id_review", "id_sentence", "verb", "noun"]).reset_index(drop=True)
rule4 = dobj_vn.merge(nsubj_vn, on=["id_review", "id_sentence", "verb"]).filter(items = ["id_review", "id_sentence", "noun_x", "verb"])
rule4["rule"] = "rule4"
op = pd.concat([op,rule4.rename(columns={'noun_x':'term', 'verb':'modifier'})], ignore_index=True).reset_index(drop=True)

# 5 <term1, modifier > +conj and(noun /term1, noun/head2) -> <head2, modifier>
conj_nn = df_clean[df_clean["concat"] == "conj(noun, noun)"].rename(columns = {"head":"term", "word":"noun2"}).filter(items = ["id_review", "id_sentence", "term", "noun2"]).reset_index(drop=True)
rule5 = conj_nn.merge(op, on=["id_review", "id_sentence", "term"]).filter(items = ["id_review", "id_sentence", "noun2", "modifier"])
rule5["rule"] = "rule5"
op = pd.concat([op,rule5.rename(columns={'noun2':'term'})], ignore_index=True).reset_index(drop=True)

# 6 <term, modifier1 > +conj and(adj /modifier1, adj/modifier2) -> <term, modifier2>
conj_aa = df_clean[df_clean["concat"] == "conj(adj, adj)"].filter(items = ["id_review", "id_sentence", "head", "word"]).rename(columns={'head':'modifier', 'word':'modifier2'}).reset_index(drop=True)
rule6 = conj_aa.merge(op, on=["id_review", "id_sentence", "modifier"]).filter(items = ["id_review", "id_sentence", "term", "modifier2"])
rule6["rule"] = "rule6"
op = pd.concat([op,rule6.rename(columns={'modifier2':'modifier'})], ignore_index=True).reset_index(drop=True)

# 7 <term, modifier> + neg(modifier, not) -> <term, not + modifier>
neg = df_clean[(df_clean["concat"] == "neg(adj, adv)") & (df_clean["word"] == "not")].filter(items = ["id_review", "id_sentence", "head", "word"]).rename(columns={'head':'modifier', "word": "not"}).reset_index(drop=True)
rule7 = neg.merge(op, on=["id_review", "id_sentence", "modifier"]).filter(items=["id_review", "id_sentence", "term", "modifier"])
op = pd.concat([op, rule7], ignore_index=True).drop_duplicates(keep=False)

def get_antonyms (x):
    if(adj_ant.get(str(x)) == None):
        return "not " + x
    else:
        return adj_ant.get(str(x))

rule7["modifier"].map(get_antonyms)
rule7["rule"] = "rule7"

op = pd.concat([op, rule7], ignore_index=True).reset_index(drop=True)

# 8 <term, modifier > + compound(term, noun) -> <noun + term, modifier>
compound_nn = df_clean[df_clean["concat"] == "compound(noun, noun)"].filter(items = ["id_review", "id_sentence", "head", "word"]).rename(columns={'head':'term', "word": "noun"})
rule8 = compound_nn.merge(op, on=["id_review", "id_sentence", "term"])
rule8_remove = rule8.filter(items=["id_review", "id_sentence", "term", "modifier"])
op = pd.concat([op, rule8_remove], ignore_index=True).drop_duplicates(keep=False)
rule8.term = rule8.noun + " " + rule8.term
rule8 = rule8.filter(items=["id_review", "id_sentence", "term", "modifier"])
rule8["rule"] = "rule8"
op = pd.concat([op, rule8], ignore_index=True).reset_index(drop=True)

# 9. <term, modifier> + compound(noun, term) -> < term + noun, modifier >
compound_nn = df_clean[df_clean["concat"] == "compound(noun, noun)"].filter(items = ["id_review", "id_sentence", "head", "word"]).rename(columns={'head':'noun', "word": "term"})
rule9 = compound_nn.merge(op, on=["id_review", "id_sentence", "term"])
rule9_remove = rule9.filter(items=["id_review", "id_sentence", "term", "modifier"])
op = pd.concat([op, rule9_remove], ignore_index=True).drop_duplicates(keep=False)
rule9.term = rule9.term + " " + rule9.noun
rule9 = rule9.filter(items=["id_review", "id_sentence", "term", "modifier"])
rule9["rule"] = "rule9"
op = pd.concat([op, rule9], ignore_index=True).reset_index(drop=True)


op["term"] = op.term.map(lambda x: x.strip())
op["modifier"] = op.modifier.map(lambda x: x.strip())
op["id_review"] = op.id_review.map(lambda x: int(x))
op["id_sentence"] = op.id_sentence.map(lambda x: int(x))
raw_op = op

#######


nlp = spacy.load("en")
stop = set(stopwords.words('english'))
extra_stop = ["next", "previous", "one", "first", "last", "back", "rear", "front", "upper", "lower", "mid", "less", "more", "major", "middle", "single", "thing", "time", "something", "anything", "everything" "due", "much", "many", "well", "right", "left", "option", "several", "issue", "review", "choice"]

# remove stop words from terms and modifiers
clean_op = raw_op[~raw_op["term"].isin(stop)]
clean_op = clean_op[~raw_op["term"].isin(extra_stop)]
clean_op = clean_op[~raw_op["modifier"].isin(extra_stop)]
clean_op = clean_op[~raw_op["modifier"].isin(stop)]
clean_op.reset_index(drop=True)

# lemmatize modifier if it is an adjective
def mod_lemmatizer(row):
    modifier = nlp(row)
    if (modifier.__len__() == 1):
        if (modifier[0].pos_ == "VERB"):
            if (modifier[0].text[-1] == "s"):
                return str(modifier[0].lemma_)
            else:
                return modifier.text
        else:
            return str(modifier[0].lemma_)
    else:
        return str(modifier[0].lemma_ + " " +  modifier[1].lemma_)

clean_op.modifier = clean_op.modifier.map(lambda x: mod_lemmatizer(x))

# lemmatize term
def term_lemmatizer(row):
    term = nlp(row)
    if (term.__len__() == 1):
        return term[0].lemma_
    else:
        if (term[1].text[-1] == "s"):
            return str(term[0].text + " " + term[1].lemma_)
        else:
            return (term.text)
        
clean_op.term = clean_op.term.map(lambda x: term_lemmatizer(x))

clean_op.term = [w.replace('vehicle', 'car') for w in clean_op.term]


clean_op = clean_op.reset_index(drop=True)

####

# load data with car models identification
df = pd.read_csv("data/2016_2017_Edmunds_cust_reviews_26032017.csv", sep=";")

# grab brand, model, year
df["id_review"] = list(range(1,8750))
df = df.filter(items=["id_review", "brand_model_year"])

# attach brand, model, year to final dataset with opinion phrases
final_op = clean_op.merge(df, on="id_review", how="left").filter(items=["brand_model_year", "id_review", "id_sentence", "term", "modifier"])
final_op["opinion"] = final_op.modifier + " " + final_op.term

final_op = final_op.filter(items=["brand_model_year", "opinion"])

final_op.to_csv("output/final_opinion_phrases.csv", index=False)





