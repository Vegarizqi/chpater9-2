from flask import (
    Flask,
    request,
    render_template,
    jsonify,
    url_for,
    redirect
)
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

client = MongoClient('mongodb+srv://test:sparta@cluster0.2vwvwy7.mongodb.net/')

db = client.dbsparta_plus_week2
app = Flask(__name__)

@app.route('/')
def main():
    words_result = db.words.find({},{'_id':False})
    words=[]
    for word in words_result:
        definition = word["definitions"][0]["shortdef"]
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word':word['word'],
            'definition':definition,
        })

    msg = request.args.get('msg')
    return render_template('index.html', words=words, msg=msg)

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = 'ba9c34e7-04a8-40c7-9654-1362a53acaf3'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for(
            'main',
            msg=f'tidak menemukan "{keyword}" ini'
        ))
    
    if type(definitions[0]) is str:
        suggestions = ', '.join(definitions)
        return redirect(url_for(
            'error',
            msg=f'tidak menemukan {keyword} ini, dan apakah kata yang di maksud adalah {suggestions}'
        ))

    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html', 
        word = keyword, 
        definitions=definitions,
        status =status
        )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc={
        'word' : word,
        'definitions' : definitions,
        'date':datetime.now().strftime('%D%m%d')
    }

    db.words.insert_one(doc)

    return jsonify({
        'result':'success',
        'msg' : f'menyimpan kata {word}, mentimpan',
    })
    

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word':word})
    db.examples.delete_many({'word':word})
    return jsonify({
        'result' : 'success',
        'msg': 'data berhasil dihapus'
    })

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word':word})
    examples = []
    for example in example_data:
        examples.append({
            'example':example.get('example'),
            'id':str(example.get('_id')),
        })
    return jsonify({
        'result':'success',
        'examples':examples,
        })

@app.route('/api/save_ex', methods=['POST'])
def save_exs():
    word = request.form.get('word')
    example = request.form.get('example')
    doc={
        'word':word,
        'example':example
    }
    db.examples.insert_one(doc)
    return jsonify({
        'result':'success',
        'msg':f'{example} anda sudah disimpan dengan kata {word}'
        })

@app.route('/api/delete_ex', methods=['POST'])
def delete_exs():
    id = request.form.get('id')
    word = request.form.get('word')
    db.examples.delete_one({'_id':ObjectId(id)})
    return jsonify({
        'result':'success',
        'msg':f'{word} kamu sudah dihapus'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)