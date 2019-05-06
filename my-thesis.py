import itertools, nltk, string 
from pycorenlp import StanfordCoreNLP
import requests
import re

reviews = [
    'The bowl of squid eyeball stew is hot and delicious',
    'i bought my canon g3 about a month ago and i have to say i am very satisfied',
    'the flower is very beautiful'
]

nlp = StanfordCoreNLP('http://localhost:9000')
dependency_parser = nlp.annotate

def pos_tag(sentence):
    result = dependency_parser(sentence, properties={"outputFormat": "json", "annotators": "pos"})['sentences'][0]['tokens']
    res = []
    for pos in result:
        res.append((pos['word'], pos['pos']))
    return res

grammar_np = 'NP: {<DT|PRP.*>? <NN.*|JJ|IN>+? <NN.*>}'
grammar_adjp = 'ADJP: {<RB>?<JJ>}'
grammar_vp = 'VP: {<VB.*>?<VB.*>?<VB.*><RP>?}'
grammar_pp = 'PP: {<IN|TO> <(?!CC).*>+? <NN.*|PRP>}'
grammar_advp = '''ADVP: {<IN|RB><(?!CC).*>+?<NN.*>}
                        {<IN|RB><(?!CC).*>+?<RB>}
               '''

#extract noun phrases
def extract_phrases(text, type):
   
    # tokenize, POS-tag, and chunk using regular expressions
    if(type == 'NP'):
        grammar = grammar_np
    elif(type == 'ADJP'):
        grammar = grammar_adjp
    elif(type == 'VP'):
        grammar = grammar_vp
    elif(type == 'PP'):
        grammar = grammar_pp
    elif(type == 'ADVP'):
        grammar = grammar_advp
    else:
        grammar = ''

    chunker = nltk.chunk.regexp.RegexpParser(grammar)

    all_chunks = list(itertools.chain.from_iterable([nltk.chunk.tree2conlltags(chunker.parse(pos_tag(text)))]))
    # join constituent chunk words into a single chunked phrase
    candidates = [(' '.join(word for word, pos, chunk in group).lower(), type)
                  for key, group in itertools.groupby(all_chunks, lambda chunk: chunk[2] != 'O') if key]
    if(len(candidates) > 0):
        return candidates[0]
    else:
        return ('', '')
    
  
def get_all_phrases(sent):
    np = extract_phrases(sent, 'NP')
    vp = extract_phrases(sent, 'VP')
    advp = extract_phrases(sent, 'ADVP')
    adjp = extract_phrases(sent, 'ADJP')
    pp = extract_phrases(sent, 'PP')

    phrases = []

    tokens_tagged = pos_tag(sent)
    index = 0
    '''while index < len(tokens_tagged):
        print(tokens_tagged[index][0].lower())
        if tokens_tagged[index][0].lower() in np[0]:
            print('masuk np')
            phrases.append(np)
            index += len(np[0].split())
        elif tokens_tagged[index][0].lower() in vp[0]:
            print('masuk vp')
            
            phrases.append(vp)
            index += len(vp[0].split())
        elif tokens_tagged[index][0].lower() in adjp[0]:
            print('masuk adjp')
            
            phrases.append(adjp)
            index += len(adjp[0].split())
        elif tokens_tagged[index][0].lower() in advp[0]:
            print('masuk advp')
            
            phrases.append(advp)
            index += len(advp[0].split())
        elif tokens_tagged[index][0].lower() in pp[0]:
            print('masuk pp')
            
            phrases.append(pp)
            index += len(pp[0].split())
        else:
            phrases.append((tokens_tagged[index][0].lower(), tokens_tagged[index][1]))
            index += 1
'''
    #for word in nltk.word_tokenize(sent):
    #    print(word.lower() in np[0])

    print(np)
    isFinish = False

    while not isFinish:
        
        if np and np not in phrases:
            phrases.append(np)

        if vp and vp not in phrases:
            phrases.append(vp)
       
    return phrases

'''
aspects = []
for sent in reviews:
    candidate_aspects = []
    aspect_pair = []
    print(sent)

    for phrase in get_all_phrases(sent):
        print(phrase)
        if phrase[1] == 'NP' or phrase[1] == 'NN' or phrase[1] == 'NNS':
            candidate_aspects.append(phrase[0])
        elif phrase[1] == 'ADJP' or phrase[1] == 'JJ':
            print('vvvvv')
            print(phrase)
            print(candidate_aspects, aspect_pair)
            print('vvvvv')
            if(len(candidate_aspects) > 0):
                aspect_pair.append((candidate_aspects.pop(), phrase[0]))
            else:
                aspect_pair.append((aspect_pair[0][0], phrase[0]))

    aspects.append(aspect_pair)

print(aspects)
'''

#print(get_all_phrases('The staff was very courteous upon check-in'))
#print(extract_phrases('the man who wear black coat is very handsome', 'NP'))

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
 #   p_wh = r'(?<=WHADVP).*?(?=\))'
 #   p_wh2 = r'(?<=WHNP).*?(?=\))'
    pattern = r'(?<= )[a-zA-Z].*?(?=\))'
    replaced = s.replace('\r\n', '')
  #  wh = re.findall(p_wh, replaced)
  #  wh2 = re.findall(p_wh2, replaced)
  #  for x in wh:
  #      replaced = replaced.replace(x, '')
  #  for x in wh2:
  #      replaced = replaced.replace(x, '')
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


print(get_phrases('The staff was very courteous upon check-in', 'S < NP'))