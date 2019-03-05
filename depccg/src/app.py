
from flask import Flask, request, json, jsonify
from depccg import PyAStarParser
from collections import namedtuple
import jsonpickle

model = "tri_headfirst"
parser = PyAStarParser(model,batchsize=32,nbest=1)

app = Flask(__name__)

@app.route('/ccgParsing', methods=['POST'])
def ccgParsing():
    sents = request.form.get('sent')
    if(sents is None):
        return json.dumps({"error": 'masukkan sent!'}), 500
    else :
        res = parser.parse_doc([sents.strip()])
      
        global resp;

        for nbests in res:
            for tree, log_prob in nbests:
                resp = jsonify(tree=str(tree), log_prob=log_prob)
        
        return resp, 200

if __name__ == '__main__':
    app.run(debug=True)

