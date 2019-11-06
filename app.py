from flask import Flask, render_template, request, redirect, url_for, jsonify
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

app = Flask(__name__)



@app.route("/", methods=['POST', 'GET'])
def hello():
    nltk.download('all')
    if request.method == 'POST':
        text = request.form.get("text")
        listofwords = word_tokenize(text)
        listoftagged = nltk.pos_tag(listofwords)
        listofsyn = []
        longest = ""
        tags = ['IN', 'JJ', 'JJR', 'JJS', 'NN', 'NNS', 'RB', 'RBR', 'RBS', 'RP', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        for word in listoftagged:
            if word[1] in tags:
                synonyms = []
                longest = ""
                for syn in wordnet.synsets(word[0]):
                    for l in syn.lemmas():
                        if filtered(l.name()):
                            synonyms.append(l.name())
                        syns = set(synonyms)
                        sortedsyns = sorted(syns, key=len)
                        if len(sortedsyns) == 0:
                            listofsyn.append(word[0])
                        else:
                            longestsyn = (sortedsyns[-1],)
                            for longest in longestsyn:
                                longest = str(longest)
                listofsyn.append(longest)
            else:
                listofsyn.append(word[0])
        return render_template("syn.html",
            listofsyn = listofsyn,
            text = text)
    else:
        return render_template("home.html")

def filtered(w):
    for l in w:
        if l == "_" or l == "-":
            return False
    return True


@app.route("/syn", methods=['POST', 'GET'])
def syn():
    return redirect("/")






if __name__ == "__main__":
    from os import environ
    app.run(debug=True, host='0.0.0.0', port=environ.get("PORT", 5000))