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
    pickle_out = open("elmo_restaurant/absa16/" + name + ".pickle","wb")
    pickle.dump(embedding, pickle_out)
    pickle_out.close()

def run(start, end):
    df = pd.read_csv('dataset/res16.csv')
    for index in range(int(start), int(end)):
        id_name = df['sentenceID'][index].replace(':','_')
        sentence = df['review'][index]
        # try:
        save(str(id_name), embed_elmo([sentence]))
        # except:
        #     print("error on :", id_name, index)

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    run(*sys.argv[1:])