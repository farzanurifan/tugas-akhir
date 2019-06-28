from __future__ import unicode_literals
from spacy.lang.en import English
from spacy.attrs import LOWER, LIKE_URL, LIKE_EMAIL
import spacy

import numpy as np

def tokenize(texts, max_length, skip=-2, attr=LOWER, merge=False, nlp=None,
             **kwargs):
    if nlp is None:
        nlp = spacy.load('en_core_web_md')
    data = np.zeros((len(texts), max_length), dtype='uint64')
    skip = np.uint64(skip)
    data[:] = skip
    bad_deps = ('amod', 'compound')
    for row, doc in enumerate(nlp.pipe(texts, **kwargs)):
        if merge:
            # from the spaCy blog, an example on how to merge
            # noun phrases into single tokens
            for phrase in doc.noun_chunks:
                # Only keep adjectives and nouns, e.g. "good ideas"
                while len(phrase) > 1 and phrase[0].dep_ not in bad_deps:
                    phrase = phrase[1:]
                if len(phrase) > 1:
                    # Merge the tokens, e.g. good_ideas
                    phrase.merge(phrase.root.tag_, phrase.text,
                                 phrase.root.ent_type_)
                # Iterate over named entities
                for ent in doc.ents:
                    if len(ent) > 1:
                        # Merge them into single tokens
                        ent.merge(ent.root.tag_, ent.text, ent.label_)
        dat = doc.to_array([attr, LIKE_URL, LIKE_EMAIL])
        if len(dat) > 0:
            msg = "Negative indices reserved for special tokens" 
            assert dat.min() >= 0, msg
            # Replace email and URL tokens
            # select the indices of tokens that are URLs or Emails
            idx = (dat[:, 1] > 0) | (dat[:, 2] > 0)
            dat = dat.astype('int64')
            dat[idx] = skip
            length = min(len(dat), max_length)
            data[row, :length] = dat[:length, 0].ravel()
    uniques = np.unique(data)
    vocab = {v: nlp.vocab[v].lower_ for v in uniques if v != skip}
    vocab[skip] = '<SKIP>'
    return data, vocab


if __name__ == "__main__":
    import doctest
    doctest.testmod()
