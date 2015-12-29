import json
import requests

def melon_search(q):
    url = "http://www.melon.com/search/keyword/index.json"
    params = {
        'jscallback': 'jQuery19109275648718392078_1451370314372',
        'query': q,
    }

    response = requests.get(url, params=params).text
    json_string = response.replace(params['jscallback'] + '(', '').replace(');', '')
    result_dict = json.loads(json_string)

    if 'SONGCONTENTS' not in result_dict:
        print('not found')
    else:
        for song in result_dict['SONGCONTENTS']:
            print('''{SONGNAME} {ALBUMNAME} {ARTISTNAME}
 - http://www.melon.com/song/detail.htm?songId={SONGID}'''.format(**song))

if __name__ == '__main__':
    line = input()
    melon_search(line)
