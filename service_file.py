import json
import os
import re

def load_json(name):
    if not os.path.exists(f'{name}.json'): return None
    with open(f'{name}.json', encoding='UTF-8') as f:
        return json.load(f)

def save_json(base, name):
    with open(f'{name}.json', "w", encoding='UTF-8') as f:
        f.write(json.dumps(base, indent=4, ensure_ascii=False))

def cvs_convert_json(filename, titles = None):
    result = list()
    with open(filename, encoding='UTF-8') as f:
        if titles is None: titles = f.readline().replace('\n', '').split(',')
        result = f.read().replace(',,', ',0,').replace('"/n"', '"\n"')
        if result.find('"') != -1: 
            result = re.sub('".*?"',  lambda x: x.group().replace(',', '$@'), result)
            result = result.replace(',', "~")
            result = result.replace('$@', ",")
        else:
            result = result.replace(',', "~")
        result = result.replace('"', "")
        res = list()
        for s in result.split('\n'):
            res.append(s.split('~'))
        #result = tuple(map(lambda x: tuple(map(lambda y: y.replace('"', ''), x)), result))
        result = tuple(map(lambda x: dict(zip(titles, x)), res))
    return result