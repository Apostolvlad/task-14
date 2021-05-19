import datetime
import os
import random
from collections import defaultdict

import service_file

BASE_DATE = (
    'сегодня',
    'вчера',
    '2 дня назад',
    '3 дня назад',
    '4 дня назад',
    '5 дней назад',
    '6 дней назад',
    '7 дней назад'
)

def get_base_orders_id(base_orders_id):
    base_orders = service_file.cvs_convert_json('Flyword_DB - ReviewData.csv')
    for data_order in base_orders:
        if data_order['sectionId'] == '': continue
        data_order['date'] = random.choice(BASE_DATE)
        base_orders_id[data_order['sectionId']].append(data_order)

def get_base_masters(base_masters):
    base_master_about = tuple(sorted(service_file.cvs_convert_json('Flyword_DB - MasterAbout.csv'), key = lambda x: (x['masterDataId'], x['id'])))
    base_master_data = service_file.cvs_convert_json('Flyword_DB - MasterData.csv')
    base_master_education = service_file.cvs_convert_json('Flyword_DB - MasterEducation.csv')
    
    for master_data in base_master_data:
        path = master_data['path']
        base_masters[path].update({'education':list(), 'about':list()})
        base_masters[path].update(master_data)
        experience_days = (datetime.datetime.today() - datetime.datetime.strptime(base_masters[path]['experience'], '%Y-%m-%d')).days
        y, experience_days  = experience_days // 365, experience_days % 365
        y_word = ''
        m_word = ''
        m = experience_days // 30
        if y < 11 or y > 19:
            y_ = y % 10
        else:
            y_ = 5
        if y_ == 1:
            y_word = f'{y} год '
        elif y_ > 1 and y_ < 5:
            y_word = f'{y} года '
        elif y_ > 4 or (y > 0 and y_ == 0):
            y_word = f'{y} лет '
        if m == 1:
            m_word = f'{m} месяц'
        elif m > 1 and m < 5:
            m_word = f'{m} месяца'
        elif m > 5:
            m_word = f'{m} месяцев'
        base_masters[path]['experience'] = f'{y_word}{m_word}'
    
    for master_about in base_master_about:
        base_masters[master_about['masterDataId']]['about'].append(master_about['aboutText'])
    
    for master_education in base_master_education:
        base_masters[master_education['masterDataId']]['education'].append(master_education['education'])

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

def main():
    try: 
        os.mkdir('result')
    except OSError:
        pass
    base_masters = defaultdict(dict)
    base_orders_id = defaultdict(list)

    base_containers = service_file.cvs_convert_json('Flyword_DB - Container.csv')
    base_geo = service_file.cvs_convert_json('Flyword_DB - Geo.csv')
    
    get_base_orders_id(base_orders_id)
    get_base_masters(base_masters)

    template = dict()
    for filename in os.listdir('template'):
        with open(f'template\\{filename}', encoding='utf-8') as f:
            template.update({filename[:filename.find('.')]: f.read()})
    sitemaps = list()
    list_masters = list() 
    base_containers_selects = list()
    for data_container in base_containers:
        data_orders = base_orders_id.get(data_container['sectionId']) 
        if len(data_orders) < 7: continue
        d_orders = data_orders[:10]
        data_orders = data_orders[10:]
        base_orders_id.update({data_container['sectionId']:data_orders})
        data_container.update({'data_orders':d_orders})
        base_containers_selects.append(data_container)
        
    base_containers = base_containers_selects
    for data_container in base_containers:
        data_orders = data_container.pop('data_orders') #base_orders_id.get(data_container['sectionId']) 
        if len(list_masters) < 10: 
            list_masters = list(base_masters.values())
            random.shuffle(list_masters)
        index = fill_html(data_container, template['index'], 'Container', ignore = ('linksBlock_3', 'data_orders'))

        for i_m in range(10):
            master = list_masters.pop()
            sh1 = '<p class="education-item hide-item">{text}</p>'
            sh2 = '<p class="education-item hide-item">{text}</p>' 
            master_item = fill_html(master, template['master_item'], 'MasterData', ignore = ('about', 'education'))
            master_about = ''
            master_education = ''
            if len(master['about']):
                master_about = fill_html2(master['about'], template['master_about'], sh = sh1, name = 'MasterAbout.aboutText')
            if len(master['education']):
                master_education = fill_html2(master['education'], template['master_education'], sh = sh2, name = 'MasterEducation.education')
            i_insert = master_item.find('"masters-item__content">') + 24
            master_item = f'{master_item[:i_insert]}\n{master_about}{master_education}{master_item[i_insert:]}'
            if i_m > 4:
                i_insert = index.find('"masters-wrap__right">') + 22
            else:
                i_insert = index.find('"masters-wrap__left">') + 21
            index = f'{index[:i_insert]}\n{master_item}{index[i_insert:]}'
        for i_m in range(10):
            if not len(data_orders): break
            data_order = data_orders.pop()
            data_order['rate'] = data_order['rate'].replace('.00', '')
            post_item = fill_html(data_order, template['post_item'], 'ReviewData')
            if data_order['rate'] == '5':
                post_item = post_item.replace('icon5', 'img/star-icon.svg')
            else:
                post_item = post_item.replace('icon5', 'img/star-empty-icon.svg')
            if i_m > 4:
                i_insert = index.find('"reviews-wrap__left">') + 21
            else:
                i_insert = index.find('"reviews-wrap__right">') + 22
            index = f'{index[:i_insert]}\n{post_item}{index[i_insert:]}'
        link_items1 = list()
        link_items3 = list()
        for data_container2 in base_containers:
            if data_container == data_container2: continue
            if data_container2['location'] == 'online':
                link_items = link_items1 
                templ_name = 'link_item1'
            elif data_container['sectionId'] == data_container2['sectionId']:
                link_items = link_items3
                templ_name = 'link_item3'
            else:
                continue
            link_items.append(fill_html(data_container2, template[templ_name], 'Container', ignore = ('data_orders',)))
        link_items1 = '\n'.join(link_items1)
        index = index.replace('Container.listLinks_1', f'\n<ul>{link_items1}</ul>')

        list_items3 = ''
        if data_container['linksBlock_3'] != '0':
            random.shuffle(link_items3)
            link_items3 = '\n'.join(link_items3)
            for value in base_geo:
                link_items3 = link_items3.replace(f'>{value["location"]}<', f'>{value["name"]}<')
            list_items3 = template['list_items3'].replace('Container.listLinks_3', f'\n<ul>{link_items3}</ul>').replace('Container.linksBlock_3', data_container['linksBlock_3'])
        index = index.replace('Container.list_items3', list_items3)

        index = index.replace('href="/index"', 'href="/"')
        sitemaps.append(template['item_sitemap'].replace('>url<', f'>https://flyvord.com/{data_container["urlPath"]}<'))
        with open(f'html\\{data_container["urlPath"]}.html', 'w', encoding='utf-8') as f:
            f.write(index)
        with open(f'result\\{data_container["urlPath"]}.html', 'w', encoding='utf-8') as f:
            f.write(index)
    sitemaps = '\n'.join(sitemaps).replace('/index', '/')
    sitemap = template['sitemap'].replace('items', sitemaps)
    with open(f'html\\sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    with open(f'result\\sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print('')
    
# "masters-wrap__left">
# вставлять блок master_item.html

# "masters-item__content">
# вставляем блок из master_about.html и master_education.html

# "reviews-wrap__left">
# вставлять блок post_item.html
# img/star-icon.svg если rate = 5, img/star-empty-icon.svg если rate = 4


if __name__ == '__main__':
    main()
    