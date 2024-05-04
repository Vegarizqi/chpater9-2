import requests

api_key = 'ba9c34e7-04a8-40c7-9654-1362a53acaf3'
word = 'potato'
url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'

res = requests.get(url)

definitions = res.json()

for definition in definitions:
    print(definition)