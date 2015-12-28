import json
import re
import requests

def spellchecker(q):
    url = "https://m.search.naver.com/p/csearch/dcontent/spellchecker.nhn"
    params = {
        '_callback': 'window.mycallback',
        'q': q,
    }

    response = requests.get(url, params=params).text
    response = response.replace(params['_callback'] + '(', '')
    response = response.replace(');', '')
    response_dict = json.loads(response)
    result_text = response_dict['message']['result']['html']
    result_text = re.sub(r'<\/?.*?>', '', result_text)
    return result_text

if __name__ == '__main__':
    line = input()
    print(spellchecker(line))
    
