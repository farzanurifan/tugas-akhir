import itertools, nltk, string 
import requests, re
from nltk import Tree, ParentedTree
from nltk.stem import WordNetLemmatizer
import pandas as pd
wordnet_lemmatizer = WordNetLemmatizer()
import xml.etree.ElementTree as et 

reviews = [
    'The bowl of squid eyeball stew is hot and delicious',
    'i bought my canon g3 about a month ago and i have to say i am very satisfied',
    'the flower is very beautiful',
    'The staff was very courteous upon check-in',
    'the man who wear black coat is very handsome',
    'If they try to change nature,  she will swiftly destroy them, but if they relax and accept the bounty of nature, they will be taken care of',
    'they fired away and the picture turned out quite nicely',
    'I had excellent shuttle service',
    'the camera is amazing, cool, excellent and beautiful',
    "i am easily enlarging pictures to 8 1/2 x 11 with no visable loss in picture quality and not even using the best possible setting as yet ( super fine ) ",
    'bottom line , well made camera , easy to use , very flexible and powerful features to include the ability to use external flash and lense / filters choices .',
    'It gives me everything I need from a computer and with the long lasting battery, it also gives me mobility.',
    'Judging from previous posts this used to be a good place, but not any longer.'
]

linking_verbs = [
    'is',
    'are',
    'am',
    'was',
    'were',
    'can be',
    'could be',
    'will be',
    'would be',
    'shall be',
    'should be',
    'may be',
    'might be',
    'must be',
    'has been',
    'have been',
    'had been',
    'feel',
    'look',
    'smell',
    'sound',
    'taste',
    'act',
    'appear',
    'become',
    'get',
    'grow',
    'prove',
    'remain', 
    'seem',
    'stay',
    'turn'
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
    
def get_phrases(sentence):
    chunking_temp = []
    chunking = []
    sent_tagged = pos_tag(sentence)

    res = get_tregex(sentence, 'ROOT')
    if(res):
        tree = ParentedTree.fromstring(res['0']['match'])
    
        print(tree.pretty_print())
        list_removed = []

        traverse_tree(tree, chunking_temp)
        print(chunking_temp)
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
                tags  = []
                for s in sent_tagged:
                    if s[0] in p_x:
                        tags.append(s[1])                    
                chunking.append( (p_x, tagged_x, ' '.join(tags)) )
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

def aspect_extraction(phrases, tagged):
    print(phrases, tagged)

def sentence_type(clauses):
    IC = 0
    DC = 0
    for clause in clauses:
        if(clause[1] == 'IC'):
            IC += 1
        elif(clause[1] == 'DC'):
            DC += 1

    if IC == 1 and DC == 0:
        return 'simple_sentence'
    elif IC >= 2 and DC == 0:
        return 'compound_sentence'
    elif IC ==1 and DC >= 1:
        return 'complex_sentence'
    else:
        return 'compound_complex_sentence'
   
#for r in reviews:
'''
clauses = get_clauses(reviews[-1])
print(clauses)
sentence_type = sentence_type(clauses)
aspects = []
if sentence_type == 'simple_sentence':
    for clause in clauses:
        sentence = clause[0]
        phrases = get_phrases(sentence)
        print(phrases)
        candidate_aspects = []
        is_finish = False;
        index_word = 0
        while not is_finish:
            phrase = phrases[index_word]
            next_phrase = phrases[index_word + 1] if index_word != len(phrases) else ('.', 'END', '.')
            print(phrase)
            if phrase[1] == 'VP' and next_phrase[1] != 'PRT':
                #check linking verb
                lemma = wordnet_lemmatizer.lemmatize(phrase[0])
                if lemma in linking_verbs and next_phrase[1] != 'NP':
                    #aspect in subject, opinion in object
                    print('masuk')
                    #find aspect
                    for i in range(0, index_word):
                        p = phrases[i]
                        if p[1] == 'NP':
                            candidate_aspects.append(p)
                    
                    #find opinion
                    for i in range(index_word+1, len(phrases)):
                        p = phrases[i]
                        print(p)
                      
                        #check opinion in adjective
                        if p[1] == 'ADJP':
                            aspect = candidate_aspects.pop()
                            aspects.append((aspect, p))

                        #check opinion in adverb
                        if p[1] == 'ADVP':
                            pass

                        #check opinion in pp ad adjective
                        if p[1] == 'PP':
                            pass
                
                    
                else:
                    #find aspect and opinion in object

                    #check opinion in verb
                    
                    pass
                
                is_finish = True
            else:
                if index_word < len(phrases):
                    index_word += 1
       
                    
print(aspects)

data = pd.read_csv('./restaurant-dataset.csv')

print(data.head())
'''

def parse_restaurant(isMultipleCategories=False, dataset="ABSA15_RestaurantsTrain/explicit.xml"):
    df_cols = ["reviewID", "sentenceID", "review", "category", "polarity"]
    out_df = pd.DataFrame(columns = df_cols)

    xtree_train = et.parse(dataset)
    xroot_train = xtree_train.getroot()

    for node in xroot_train: 
        rid = node.attrib.get('rid')
        sentences = node.find('sentences') if node is not None else None
        for sentence in sentences:
            sid = sentence.attrib.get('id')
            text = sentence.find('text').text if sentence is not None else None
            opinions = sentence.find('Opinions') if sentence is not None else []
            if opinions is not None:
                categories = []
                polarities = []
                for opinion in opinions:
                    categories.append(opinion.attrib.get('category'))
                    polarities.append(opinion.attrib.get('polarity'))
                if not isMultipleCategories:
                    out_df = out_df.append(pd.Series([rid, sid, text, categories[0], polarities[0]], 
                                        index = df_cols), 
                            ignore_index = True)
                else:
                    out_df = out_df.append(pd.Series([rid, sid, text, ','.join(categories), ','.join(polarities)], 
                                        index = df_cols), 
                            ignore_index = True)

    return out_df


def parse_laptop(isMultipleCategories=False):
    df_cols = ["reviewID", "sentenceID", "review", "category", "polarity"]
    out_df = pd.DataFrame(columns = df_cols)

    xtree_train = et.parse("ABSA15_LaptopsTrain/ABSA-15_Laptops_Train_Data.xml")
    xroot_train = xtree_train.getroot()

    for node in xroot_train: 
        rid = node.attrib.get('rid')
        sentences = node.find('sentences') if node is not None else None
        for sentence in sentences:
            sid = sentence.attrib.get('id')
            text = sentence.find('text').text if sentence is not None else None
            opinions = sentence.find('Opinions') if sentence is not None else []
            if opinions is not None:
                categories = []
                polarities = []
                for opinion in opinions:
                    categories.append(opinion.attrib.get('category'))
                    polarities.append(opinion.attrib.get('polarity'))
                if not isMultipleCategories:
                    out_df = out_df.append(pd.Series([rid, sid, text, categories[0], polarities[0]], 
                                        index = df_cols), 
                            ignore_index = True)
                else:
                    out_df = out_df.append(pd.Series([rid, sid, text, ','.join(categories), ','.join(polarities)], 
                                        index = df_cols), 
                            ignore_index = True)

    return out_df
                



res_df_single = parse_restaurant()
res_df_multiple = parse_restaurant(True)
res_df_multiple_price = parse_restaurant(True, "ABSA15_RestaurantsTrain/price.xml")


res_df_single.to_csv('restaurant-single-categories.csv', index=False)
res_df_multiple.to_csv('restaurant-multiple-categories.csv', index=False)
res_df_multiple_price.to_csv('restaurant-multiple-prices.csv', index=False)

res_df_laptop_single = parse_laptop()
res_df_laptop_multiple = parse_laptop(True)

res_df_laptop_single.to_csv('laptop-single-categories.csv', index=False)
res_df_laptop_multiple.to_csv('laptop-multiple-categories.csv', index=False)

food_quality = [
    "QUALITY for  opinions  focusing  on  the  taste, the freshness, the texture, the consistency, the temperature, the preparation, the authenticity,the cooking  or general quality of the food and thedrinks served in the restaurant e.g. Example: Salads are a delicious way to begin the meal, Steamed fresh so brought hot hot hot to your table. Their bagels are fine, but they are a little overcooked, and not really a 'special' bagel experience., No gimmicks here --the food speaks for itself in its freshness and preparation., The pizza was great., The  drinks  are  amazing  and  half  off  till  8pm."
]

restaurant_general = [
    "RESTAURANT for opinions evaluating the restaurant as whole not focusing on any of the above five entity types e.g. Saul   is   the   best   restaurant   on   Smith   Street   and   in   Brooklyn., It’s a little out of the way if you don't live in the neighborhood, but definitely worth the trip from wherever you are., Please take my advice, go and try this place.",
    "This attribute label is assigned to sentences that express general positive or negative sentiment about an entity type e.g. My husband and I thoughtit would be great to go to the Jekyll and Hyde Pub   for   our   anniversary,   and   to   our   surprise   it   was   fantastic., I received prompt service with a smile, LOVE the atmosphere -felt like I was in Paris, The location is perfect."
]

service_general = [
    "for  opinions  focusing  on  the (customer/kitchen/counter) service, onthe promptness and quality of the restaurant’sservicein general, the food preparation,the staff’s attitude and professionalism, the wait  time,the  options  offered  (e.g. takeout), etc. Below are some examples: The  food  here  is  rather  good,  but only  if  you  like  to  wait  for  it, The hostess is rude to the point of being offensive., The takeout is great too since they give high quality tupperware as well., I  had  a  huge  group  for  my  birthday  and  we  were  well  taken  care  of. ",
    "This attribute label is assigned to sentences that express general positive or negative sentiment about an entity type e.g. My husband and I thoughtit would be great to go to the Jekyll and Hyde Pub   for   our   anniversary,   and   to   our   surprise   it   was   fantastic., I received prompt service with a smile, LOVE the atmosphere -felt like I was in Paris, The location is perfect."
]

ambience_general = [
    "for  opinions  focusing  on the atmosphere  or  the  environment  of  the restaurant’s  interior or  exterior space(e.g.  terrace,  yard,  garden),  the décor, entertainment options, etc. Here are some examples: Very cozy and warm inside, I  highly  recommendCafe  St.  Bart's  for  their  food,  the  ambience  and wonderful service., The  dining  room  is  quietly  elegant  with  no  music  to  shout  over --how refreshing!, Our family never expected such incredible entertainment in a restaurant., When  you're  sitting  in  their  main  dining  room  (which  has  a  spectacular, hand-painted high ceiling) you'd neverknow there was a world outside.",
    "This attribute label is assigned to sentences that express general positive or negative sentiment about an entity type e.g. My husband and I thoughtit would be great to go to the Jekyll and Hyde Pub   for   our   anniversary,   and   to   our   surprise   it   was   fantastic., I received prompt service with a smile, LOVE the atmosphere -felt like I was in Paris, The location is perfect."
]

food_style_options = [
    'FOOD for opinions focusing on the food in  general or in terms of specific dishes, dining options etc. Below are some examples: Our food was great too!, The menu is very limited -Ithink we counted 4 or 5 entrees, The food was pretty traditional but it was hot and good with large portions, The pizza was great, The dinner was ok, nothing I would have again, They have authentic Indian at amazing prices, The lobster sandwich is good and the spaghetti with Scallops and Shrimp is great. ',
    "for  opinions  referring  to  the  presentation, the serving  style, the portions  size, the food/menu  options  or  variety  (e.g.  innovative  dishes/drinks, vegetarian options) of the food and of the drinks served in the restaurant e.g. The   menu   is   very   limited -Ithink   we   counted   4   or   5   entrees., The portions are small but being that the food was so good makes up for that., Not enough wines by the glass either."
]

restaurant_miscellaneous = [
  "RESTAURANT for opinions evaluating the restaurant as whole not focusing on any of the above five entity types e.g. Saul   is   the   best   restaurant   on   Smith   Street   and   in   Brooklyn., It’s a little out of the way if you don't live in the neighborhood, but definitely worth the trip from wherever you are., Please take my advice, go and try this place.",
  "for attributes that do not fall intoany of the aforementioned cases. Below are some examples: Not a great place for family or general dining., Open  late  (well  as  late  as  I  ever  got  there  and  I'm  a  night  person)"
]

restaurant_prices = [
      "RESTAURANT for opinions evaluating the restaurant as whole not focusing on any of the above five entity types e.g. Saul   is   the   best   restaurant   on   Smith   Street   and   in   Brooklyn., It’s a little out of the way if you don't live in the neighborhood, but definitely worth the trip from wherever you are., Please take my advice, go and try this place.",
  "for opinions that refer to the prices of the food, the drinks or the restaurant in general e.g. But the pizza is way tooexpensive."
]

drinks_quality = [
    "for opinions focusing on the drinksin general or in terms ofspecific drinks, drinkingoptions etc. Below are some examples:Wonderful strawberry daiquirisas well!,The  food  is  good,  especially  their  more  basic  dishes,  and  the  drinks  are delicious.,The wine list is extensive and impressive,Not enough wines by the glass either.,The cream cheeses are out of this world and I love that coffee!!",
    "QUALITY for  opinions  focusing  on  the  taste, the freshness, the texture, the consistency, the temperature, the preparation, the authenticity,the cooking  or general quality of the food and thedrinks served in the restaurant e.g. Example: Salads are a delicious way to begin the meal, Steamed fresh so brought hot hot hot to your table. Their bagels are fine, but they are a little overcooked, and not really a 'special' bagel experience., No gimmicks here --the food speaks for itself in its freshness and preparation., The pizza was great., The  drinks  are  amazing  and  half  off  till  8pm."
]

food_prices = [
    'FOOD for opinions focusing on the food in  general or in terms of specific dishes, dining options etc. Below are some examples: Our food was great too!, The menu is very limited -Ithink we counted 4 or 5 entrees, The food was pretty traditional but it was hot and good with large portions, The pizza was great, The dinner was ok, nothing I would have again, They have authentic Indian at amazing prices, The lobster sandwich is good and the spaghetti with Scallops and Shrimp is great. ',
    "for opinions that refer to the prices of the food, the drinks or the restaurant in general e.g. But the pizza is way tooexpensive."
]

drinks_style_options = [
 "for opinions focusing on the drinksin general or in terms ofspecific drinks, drinkingoptions etc. Below are some examples:Wonderful strawberry daiquirisas well!,The  food  is  good,  especially  their  more  basic  dishes,  and  the  drinks  are delicious.,The wine list is extensive and impressive,Not enough wines by the glass either.,The cream cheeses are out of this world and I love that coffee!!",
   "for  opinions  referring  to  the  presentation, the serving  style, the portions  size, the food/menu  options  or  variety  (e.g.  innovative  dishes/drinks, vegetarian options) of the food and of the drinks served in the restaurant e.g. The   menu   is   very   limited -Ithink   we   counted   4   or   5   entrees., The portions are small but being that the food was so good makes up for that., Not enough wines by the glass either."
]

location_general = [
    "for opinions focusing on the location of the reviewed restaurantin terms of its position, the surroundings, the view, etc. Below are some examples:Conveniently located too, being right on Bedford ave,The view is spectacular, and the food is great",
    "This attribute label is assigned to sentences that express general positive or negative sentiment about an entity type e.g. My husband and I thoughtit would be great to go to the Jekyll and Hyde Pub   for   our   anniversary,   and   to   our   surprise   it   was   fantastic., I received prompt service with a smile, LOVE the atmosphere -felt like I was in Paris, The location is perfect."
]

drinks_prices = [
"for opinions focusing on the drinksin general or in terms ofspecific drinks, drinkingoptions etc. Below are some examples:Wonderful strawberry daiquirisas well!,The  food  is  good,  especially  their  more  basic  dishes,  and  the  drinks  are delicious.,The wine list is extensive and impressive,Not enough wines by the glass either.,The cream cheeses are out of this world and I love that coffee!!",
"for opinions that refer to the prices of the food, the drinks or the restaurant in general e.g. But the pizza is way tooexpensive."
]