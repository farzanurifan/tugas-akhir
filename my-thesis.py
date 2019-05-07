import itertools, nltk, string 
from pycorenlp import StanfordCoreNLP
import requests
import re

reviews = [
    'The bowl of squid eyeball stew is hot and delicious',
    'i bought my canon g3 about a month ago and i have to say i am very satisfied',
    'the flower is very beautiful',
    'The staff was very courteous upon check-in',
    'the man who wear black coat is very handsome',
    'If they try to change nature,  she will swiftly destroy them, but if they relax and accept the bounty of nature, they will be taken care of'
]

nlp = StanfordCoreNLP('http://localhost:9000')
dependency_parser = nlp.annotate

def pos_tag(sentence):
    result = dependency_parser(sentence, properties={"outputFormat": "json", "annotators": "pos"})['sentences'][0]['tokens']
    res = []
    for pos in result:
        res.append((pos['word'], pos['pos']))
    return res


def get_tregex(text, tregex):
    url = "http://localhost:9000/tregex"
    request_params = {"pattern": tregex}
    r = requests.post(url, data=text, params=request_params, timeout=120)
    print(r)
    try:
        return r.json()['sentences'][0]
    except:
        return []

def sentence_from_tree(s):
    pattern = r'(?<= )[a-zA-Z].*?(?=\))'
    replaced = s.replace('\r\n', '')
    res = ' '.join(re.findall(pattern, replaced))
    return res

def get_phrases(sentences, tregex):
    phrases = []
    res = get_tregex(sentences, tregex)
    length = len(res)
    for x in range(0, length):
        phrases.append(sentence_from_tree(res[str(x)]['match']))
    if length > 1:
        for x in range(0, length - 1):
            phrases[x] = phrases[x].replace(phrases[x+1], '')
    return phrases


def get_clauses(sentence):
    temp = []
    clauses = []
    res_all_clauses = get_tregex(sentence, 'S < (NP $ VP)')
    res_sbar_clause = get_tregex(sentence, 'SBAR < S')
    #filter clauses with dependency clauses
    for x in range(0, len(res_all_clauses)):
        s = sentence_from_tree(res_all_clauses[str(x)]['match'])
        ic = True    
        for y in range(0, len(res_sbar_clause)):
            sbar = sentence_from_tree(res_sbar_clause[str(y)]['match'])            
            if sbar in s and sbar != s:
                s = s.replace(sbar, '')
                if(len(res_sbar_clause) == 1):
                    temp.append([sbar.strip(), 'DC'])
            elif s in sbar:
                ic = False
                temp.append( [sbar.strip(), 'DC'])
        if ic:
            temp.append( [s.strip(), 'IC'] )
    #overwrite sentence that already exist in list
    len_clause = len(temp)
    for x in range(0, len_clause):
        for y in range(x + 1, len_clause):
            temp[x][0] = temp[x][0].replace(temp[y][0], '').strip()
        
        temp[x][0] = re.sub(r"  ", " ", temp[x][0])
        clauses.append( tuple(temp[x]) )
    #sorted by index sentence
    return sorted(clauses, key=lambda clause: 999 if sentence.find(clause[0]) == -1 else sentence.find(clause[0]))


for r in reviews:
    print(get_clauses(r))