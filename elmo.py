import tensorflow_hub as hub
import tensorflow as tf

def embed_elmo(word_to_embed):
    elmo = hub.Module("https://tfhub.dev/google/elmo/2")
    embedding_tensor = elmo(word_to_embed, as_dict=True)["elmo"]

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        embedding = sess.run(embedding_tensor)
        return embedding

import pickle

def save(name, embedding):
    pickle_out = open("elmo_restaurant/" + name + ".pickle","wb")
    pickle.dump(embedding, pickle_out)
    pickle_out.close()

import pandas as pd

df = pd.read_csv('res_mul_all.csv')

def run(start, end):
    for index in range(start, end):
        id_name = df['id'][index]
        sentence = df['review'][index]
        try:
            save(str(id_name), embed_elmo([sentence]))
            print(id_name, index)
        except:
            print("error on :", id_name, index)

run(240, 250)
run(250, 260)