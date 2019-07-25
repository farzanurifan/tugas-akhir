import tensorflow_hub as hub
import tensorflow as tf
import pickle
import pandas as pd
import sys

def embed_elmo(word_to_embed):
    elmo = hub.Module("https://tfhub.dev/google/elmo/2")
    embedding_tensor = elmo(word_to_embed, as_dict=True)["elmo"]

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        embedding = sess.run(embedding_tensor)
        return embedding

def save(name, embedding):
    print(name)
    pickle_out = open("elmo_restaurant/all_terms/" + name + ".pickle","wb")
    pickle.dump(embedding, pickle_out)
    pickle_out.close()

def run(start, end):
    pickle_in = open("all_terms.pickle", "rb")
    all_terms = pickle.load(pickle_in)
    
    for index in range(int(start), int(end)):
        name = all_terms[index]
        save(str(name).replace('/', '_').replace('.','_'), embed_elmo([name])[0][0])

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    #run(*sys.argv[1:])
    run(505, 506)