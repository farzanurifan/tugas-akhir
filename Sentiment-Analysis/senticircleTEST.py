#Python Code to implement Senti Circle on a single document 
import nltk
import matplotlib.pyplot as plt
from nltk.corpus import sentiwordnet as swn
import math
from math import exp, expm1, log, log10
import numpy as np
import turtle
from nltk.wsd import lesk
from pycorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP('http://localhost:9000')
dependency_parser = nlp.annotate


def analyse_file(key):
    try:
        file = open("Sentiment.txt", 'r')
    except:
        print ('Invalid File!')
        return 'Error'  
    doc = file.read()
    lines = doc.split("\n")
    file.close()
    
    radii = get_TDOC(lines, key)    
    return (radii, lines[0])

def get_TDOC(lines, key):
    freq = {'Init': 0}              #Number of times context term occurs with key
    freq.clear()
    prohib=['you','have','a','i','am','this','will','on','me','to','all','us','has','of','99']
    for line in lines:
        words = line.split(" ")
        if key in words:
            for context in words:
                flag=0
                for i in prohib:
                    if i == context:
                        flag=1
                        break
                if flag==0 and context!=key:
                    freq.setdefault(context, 0)
                    freq[context] = freq.get(context) + 1
                                           
    N = 0                           #Total Number of terms in Document
    for line in lines:
        words = line.split(" ")
        N += len(words)

    Nci = {'Init': 0}               #Total terms that occur with context term
    Nci.clear()
    for context in freq.keys():
        for line in lines:
            words = line.split(" ")
            if context in words:
                Nci.setdefault(context, 0)
                Nci[context] += len(words)

    radii = {'Init': 0}             #Get Radius of context term with TDOC formula
    radii.clear()
    for term in freq.keys():
         radii[term] = (freq[term]*(log(N/Nci[term])))/4
    return radii                    #Returns entire set of context terms related to key

def pos_tag(sentence):
    result = dependency_parser(sentence, properties={"outputFormat": "json", "annotators": "pos"})['sentences'][0]['tokens']
    res = []
    for pos in result:
        res.append((pos['word'], pos['pos']))
    return res
    
def get_theta(key, sentence):
    text=nltk.word_tokenize(key + " ")
    pp_tagged=pos_tag(sentence)
    tagged = ''
    for p in pp_tagged:
        if p[0] == text[0]:
            tagged = p
    
    t=tagged[0]
    if 'NN' in tagged[1] :
        senti_str = lesk(text, t, 'n').name()
        Scores=swn.senti_synset(senti_str)
    elif 'NNS' in tagged[1] :
        senti_str = lesk(text, t, 'n').name()
        Scores=swn.senti_synset(senti_str)
    elif 'VB' in tagged[1] :
        senti_str = lesk(text, 'v', 'n').name()
        Scores=swn.senti_synset(senti_str)
    elif 'VBG' in tagged[1] :
        senti_str = lesk(text, 'v', 'n').name()
        Scores=swn.senti_synset(senti_str)
    elif 'JJ' in tagged[1] :
        senti_str = lesk(text, t, 'a').name()
        print(senti_str)

        Scores=swn.senti_synset(senti_str)

    elif 'RB' in tagged[0][1] :
        senti_str = lesk(text, t, 'r').name()
        Scores=swn.senti_synset(senti_str)
    else:
        return 0  
    print(Scores)
    if(Scores.pos_score()>0.0):
        return np.pi*Scores.pos_score()
    else:
        return np.pi*Scores.obj_score()*(-1)
    
if __name__=="__main__":
    print("Calculating tdoc...\nEnter key: ")
    key = input()               #Take input from console
    (radii, text) = analyse_file(key)          #radii contains set of {word (str), TDOC (float)}
    theta = {'Init': 0}
    theta.clear()
    print("Calculating Prior Sentiment...")
    for word in radii.keys():
        filter = get_theta(word, text)            #if function returns 0 word does not exist in lexicon
        if(filter != 0):
            theta[word] = get_theta(word, text)   #Store into theta set of words that exist in lexicon along with respective angle
                                            #Theta = set of {word, angle}
    print("Creating SentiCirlce...")
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot([0,0],[-1,1])
    plt.plot([-1,1],[0,0])
    plt.axis([-1,1,-1,1])
    i=0
    a=[]
    b=[]
    rad=list(radii.values())
    theta1=list(theta.values())
    while(i<len(radii)):
        try:
            print(rad[i], theta1[i], math.cos(theta1[i]), rad[i]*math.cos(theta1[i]))
            a.append(rad[i]*math.cos(theta1[i]))
            b.append(rad[i]*math.sin(theta1[i]))
        except IndexError:
            pass
        i+=1 
    plt.scatter(a,b,label="circles",color="r",marker="o",s=10)
    q = 0
    rad2=list(radii.keys())
    for i,j in zip(a,b):
        ax.annotate('%s' %rad2[q], xy=(i,j), xytext=(15,0), textcoords='offset points')
        q = q+1    
        
    ax.add_artist(plt.Circle((0,0),1.0,color='b',fill=False))
    plt.xlabel('Sentiment Strength')
    plt.ylabel('Orientation')
    plt.title(key)
    plt.savefig("graph.png")
    print("SUCCESS")
    
