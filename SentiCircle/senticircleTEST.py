#Python Code to implement Senti Circle on a single document 
import nltk
import matplotlib.pyplot as plt
from nltk.corpus import sentiwordnet as swn
import math
from math import exp, expm1, log, log10
import numpy as np
import turtle

def analyse_file(key):
    try:
        file = open("Sentiment.txt", 'r')
    except (BaseExceptionException,e):
        print ('Invalid File!')
        return 'Error'  
    doc = file.read()
    lines = doc.split("\n")
    file.close()
    
    radii = get_TDOC(lines, key)    
    print radii
    return radii

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
     
def get_theta(key):
    text=nltk.word_tokenize(key + " ")
    tagged=nltk.pos_tag(text)
    t=tagged[0][0]
    if 'NN' in tagged[0][1] :
        Scores=swn.senti_synset(t+'.n.01')
    elif 'NNS' in tagged[0][1] :
        Scores=swn.senti_synset(t+'.nns.01')
    elif 'VB' in tagged[0][1] :
        Scores=swn.senti_synset(t+'.v.01')	
    elif 'VBG' in tagged[0][1] :
        Scores=swn.senti_synset(t+'.v.01')
    elif 'JJ' in tagged[0][1] :
        Scores=swn.senti_synset(t+'.a.01')	
    elif 'RB' in tagged[0][1] :
        Scores=swn.senti_synset(t+'.r.01')
    else:
        return 0       
    if(Scores.pos_score()>0.0):
        return np.pi*Scores.pos_score()
    else:
        return np.pi*Scores.obj_score()*(-1)
    
if __name__=="__main__":
    print "Calculating tdoc...\nEnter key: "
    key = raw_input()               #Take input from console
    radii = analyse_file(key)          #radii contains set of {word (str), TDOC (float)}
    theta = {'Init': 0}
    theta.clear()
    print "Calculating Prior Sentiment..."
    for word in radii.keys():
        filter = get_theta(word)            #if function returns 0 word does not exist in lexicon
        if(filter != 0):
            theta[word] = get_theta(word)   #Store into theta set of words that exist in lexicon along with respective angle
                                            #Theta = set of {word, angle}
    print "Creating SentinCirlce..."
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot([0,0],[-1,1])
    plt.plot([-1,1],[0,0])
    plt.axis([-1,1,-1,1])
    i=0
    a=[]
    b=[]
    rad=radii.values()
    theta1=theta.values()
    print rad
    print theta1
    while(i<len(radii)):
        a.append(rad[i]*math.cos(theta1[i]))
        b.append(rad[i]*math.sin(theta1[i]))
        i+=1 
    plt.scatter(a,b,label="circles",color="r",marker="o",s=10)
    q = 0
    rad2=radii.keys()
    for i,j in zip(a,b):
        ax.annotate('%s' %rad2[q], xy=(i,j), xytext=(15,0), textcoords='offset points')
        q = q+1    
        
    ax.add_artist(plt.Circle((0,0),1.0,color='b',fill=False))
    plt.xlabel('Sentiment Strength')
    plt.ylabel('Orientation')
    plt.title(key)
    plt.savefig("graph.png")
    print "SUCCESS"
    
