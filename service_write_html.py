import os

def fill_html(base, html, name, ignore = ()):
    for item in base.items():
        if item[0] in ignore: continue
        html = html.replace(f'{name}.{item[0]}', item[1])
    return html

def fill_html2(base, html, sh, name):
    result = list()
    for text in base:
        result.append(sh.format(text = text))
    return html.replace(name, '\n'.join(result))

def get_template():
    template = dict()
    for filename in os.listdir('template'):
        with open(f'template\\{filename}', encoding='utf-8') as f:
            template.update({filename[:filename.find('.')]: f.read()})
    return template