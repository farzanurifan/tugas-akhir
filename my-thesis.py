import itertools, nltk, string 
import requests, re
from nltk import Tree, ParentedTree

reviews = [
    'The bowl of squid eyeball stew is hot and delicious',
    'i bought my canon g3 about a month ago and i have to say i am very satisfied',
    'the flower is very beautiful',
    'The staff was very courteous upon check-in',
    'the man who wear black coat is very handsome',
    'If they try to change nature,  she will swiftly destroy them, but if they relax and accept the bounty of nature, they will be taken care of'
]

def pos_tag(sentence):
    url = "http://localhost:9000"
    request_params = {"annotators": "pos"}
    r = requests.post(url, data=sentence, params=request_params, timeout=120)
    try:
        results = r.json()['sentences'][0]['tokens']
        res = []
        for pos in results:
            res.append((pos['word'], pos['pos']))
        return res
    except Exception as e:
        print(e)
        return []

def get_tregex(text, tregex):
    url = "http://localhost:9000/tregex"
    request_params = {"pattern": tregex}
    r = requests.post(url, data=text, params=request_params, timeout=120)
    try:
        return r.json()['sentences'][0]
    except:
        return []

def sentence_from_tree(s):
    pattern = r'(?<= )[a-zA-Z].*?(?=\))'
    replaced = s.replace('\r\n', '')
    res = ' '.join(re.findall(pattern, replaced))
    return res

def traverse_tree(t, chunking):
    if t.height() == 2: 
        data = (' '.join(t.parent().leaves()), t.parent().label())
        if data not in chunking:
            if(len(chunking) > 0):
                 if(data[1] != chunking[len(chunking) -1][1]):
                     chunking.append(data)
            else:
                chunking.append(data)
        return 
    else:
        for child in t:
            traverse_tree(child, chunking)
    
def get_phrases(sentences):
    chunking_temp = []
    chunking = []
   
    res = get_tregex(sentences, 'ROOT')
    if(res):
        tree = ParentedTree.fromstring(res['0']['match'])
    
        print(tree.pretty_print())
        list_removed = []

        traverse_tree(tree, chunking_temp)
        #fix overlap string
        for x in range(0, len(chunking_temp)):    
            p_x,tagged_x = chunking_temp[x]
            for y in range(x + 1, len(chunking_temp)):
                p_y = chunking_temp[y][0]
            
                if( tagged_x == 'VP' or tagged_x == 'S' or tagged_x == 'SBAR'):
                    #do intersection
                    p_x = p_x.replace(p_y, '').strip()
                else:
                    if p_y in p_x and p_y not in list_removed:
                        list_removed.append(p_y)

            #chunking_temp[x][0] = re.sub(r"  ", " ", chunking_temp[x][0])
            #if(chunking_temp[x][0] != ''):
            if (p_x not in list_removed and p_x != ''):
                chunking.append( (p_x, tagged_x) )
    return chunking
    
    

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
    clauses = get_clauses(r)
    for clause in clauses:
        sentence = clause[0]
        phrases = get_phrases(sentence)
        print(phrases)

