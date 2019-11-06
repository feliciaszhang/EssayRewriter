from flask import Flask, render_template, request, redirect, url_for, jsonify
import pymongo
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
nltk.download('all')
from nltk.corpus import wordnet
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)
app = Flask(__name__)
myfile = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
mydb = myfile["thesaurus"]
mycol = mydb["files"]


@app.route("/syn", methods=['POST', 'GET'])
def syn():
    if request.method == 'POST':
        if request.form.get("back"):
            return redirect("/")
        else:
            original = request.form.get("text")
            syn = request.form.get("syn")
            return redirect(url_for('save',
                original = original,
                syn = syn))
    else:
        return render_template("syn.html",
            listofsyn = listofsyn)


@app.route("/save/<original>/<syn>", methods=['POST', 'GET'])
def save(original, syn):
    if request.method == 'POST':
        filename = request.form.get("filename")
        timestamp = datetime.now()
        original = request.form.get("readonlytext")
        syn = request.form.get("syn")
        mydict = {"filename": filename, "original": original, "syn": syn, "timestamp": timestamp}
        file = mycol.insert_one(mydict)
        return redirect("/files")
    else:
        return render_template("save.html",
            original = original,
            syn = syn)


@app.route("/files", methods=['POST', 'GET'])
def files():
    if request.method == 'POST':
        if request.form.get("back"):
            return redirect("/")
        else:
            filename = request.form.get("filename")
            return redirect(url_for("document",
                filename = filename))
    else:
        files = mycol.find({})
        return render_template("files.html",
            files = files)

@app.route("/document/<filename>", methods=['POST', 'GET'])
def document(filename):
    if request.method == 'POST':
        if request.form.get("back"):
            return redirect("/files")
        elif request.form.get("change"):
            changingfilename = request.form.get("hidden")
            new = request.form.get("new")
            mycol.update_one({filename:changingfilename},{"$set":{filename:new}})
            return redirect("/files")
        else:
            deletingfilename = request.form.get("hidden")
            mycol.remove({filename:deletingfilename})
            return redirect("/files")
    else:
        document = mycol.find({})
        return render_template("document.html",
            document = document,
            filename = filename)


@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        if request.form.get("all"):
            return redirect("/files")
        else:
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
                            synonyms.append(l.name())
                            syns = set(synonyms)
                            sortedsyns = sorted(syns, key=len)
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




if __name__ == "__main__":
    app.run(debug=True)
