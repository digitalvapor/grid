"""-----------
--------------
---- GRID ----
--------------
--------------
By Tom Spalding (https://github.com/digitalvapor)
-------------
    SHOP
-------------
Note: This truncates the item's description at the first newline. If you format
your descriptions with newlines then you can easily keep things brief.

You can call the following metadata:
page.etsy_shopname
page.etsy_store
page.store_url
page.num_items
page.item_title[i]
page.item_url[i]
page.item_desc[i]
page.item_quantity[i]
page.item_tags[i]
page.item_id[i]
page.item_img0[i]
page.item_img1[i]
page.item_img2[i]
page.item_img3[i]

--------------
    RECIPE
--------------
num_recipes
cook[i]
cook_url[i]
recipe_url[i]
recipe_js[i]
recipe_json[i]
recipe_oIng[i]
recipe_oEqu[i]
recipe_oIns[i]
recipe_oSpecial[i]
recipe_diff[i]
recipe_created[i]
recipe_created2[i]
recipe_src_url[i]
recipe_src_text[i]
recipe_img[i]
recipe_title[i]
recipe_serves[i]
recipe_slug[i]
recipe_timeTaken[i]

TODO: cleanup, test on both python 2 and 3, merge redundancies, add storeenvy and youtube support, better data structure
"""

import urllib3
import urllib
import json
import re
from pelican import signals

def shop(generator, metadata):

    if not ('ETSY_SHOPNAME' in generator.settings.keys() or 'ENVY_SHOPNAME' in generator.settings.keys()):
        print('No store info found in Pelican conf. See readme.')
        return

    etsy_api_key = generator.settings['ETSY_API_KEY']

    if 'ETSY_STORE' in generator.settings.keys():
        metadata['etsy_shopname'] = generator.settings['ETSY_SHOPNAME']
        metadata['etsy_store'] = generator.settings['ETSY_STORE']

    if 'shoptype' in metadata.keys():
        shoptype = metadata['shoptype']
    else:
        shoptype = 'whatever'
        #print('shoptype not specified.. set as',shoptype)#debug
        return

    #--------------------
    # construct requests
    #--------------------
    etsy_params = {
       'api_key':etsy_api_key,
       'fields':'title,url,description,quantity,tags',#see fields https://www.etsy.com/developers/documentation/reference/listing#section_fields
       'limit':20,
       'includes':'MainImage',
    }

    etsy_data = urllib.urlencode(etsy_params)
    etsy_base_url = 'https://openapi.etsy.com/v2/shops/'+repr(metadata['etsy_store'])+'/listings/active'
    etsy_url = etsy_base_url + '?' + etsy_data

    r = urllib.urlopen(etsy_url)   #response object
    j = r.read()                   #read response object to get json
    j = j.replace('\r\n','\\r\\n') #replace offensive character :)
    j = json.loads(j)              #converts json string to dict
    c = j['count']

    metadata['num_items'] = c
    metadata['item_title'] = []
    metadata['item_url'] = []
    metadata['item_desc'] = []
    metadata['item_quantity'] = []
    metadata['item_tags'] = []
    metadata['item_id'] = []
    metadata['item_img0'] = []
    metadata['item_img1'] = []
    metadata['item_img2'] = []
    metadata['item_img3'] = []
    metadata['store_url'] = 'http://'+metadata['etsy_shopname']+'.etsy.com'

    for result in j['results']:
        metadata['item_title'].append(result['title'])
        shorter_url = re.split('\?',result['url'])#decided to shorten this a bit because I dont care about the analytics of it, and the w3 validator throws a warning about ampersands. feel free to chime in if you see it differently.
        metadata['item_url'].append(shorter_url[0])
        shorter_desc = re.split('\r\n',result['description'])
        metadata['item_desc'].append(shorter_desc[0])
        metadata['item_quantity'].append(result['quantity'])
        metadata['item_tags'].append(result['tags'])
        metadata['item_id'].append(result['MainImage']['listing_id'])
        metadata['item_img0'].append(result['MainImage']['url_75x75'])
        metadata['item_img1'].append(result['MainImage']['url_170x135'])
        metadata['item_img2'].append(result['MainImage']['url_570xN'])
        metadata['item_img3'].append(result['MainImage']['url_fullxfull'])

def item(generator, metadata):
    if not ('ETSY_SHOPNAME' in generator.settings.keys() or 'ENVY_SHOPNAME' in generator.settings.keys()):
        print('No store info found in Pelican conf. See readme.')

    etsy_api_key = generator.settings['ETSY_API_KEY']

    if 'ETSY_STORE' in generator.settings.keys():
        metadata['etsy_shopname'] = generator.settings['ETSY_SHOPNAME']
        metadata['etsy_store'] = generator.settings['ETSY_STORE']

    items = {}
    if ('shop' in metadata.keys()) and ('items' in metadata.keys()):
        shoptype = metadata['shop']
        items = re.split(',',metadata['items'])
        i=0
        for item in items:
            items[i] = item.strip()
            i+=1
    else:
        return

    etsy_params = {
       'api_key':etsy_api_key,
       'fields':'title,url,description,quantity,tags',
       'limit':100,
       'includes':'MainImage',
    }

    etsy_data = urllib.urlencode(etsy_params)
    etsy_base_url = 'https://openapi.etsy.com/v2/shops/'+repr(metadata['etsy_store'])+'/listings/active'
    etsy_url = etsy_base_url + '?' + etsy_data

    r = urllib.urlopen(etsy_url)
    j = r.read()
    j = j.replace('\r\n','\\r\\n')
    j = json.loads(j)
    c = j['count']

    metadata['num_items'] = c
    metadata['item_title'] = []
    metadata['item_url'] = []
    metadata['item_desc'] = []
    metadata['item_quantity'] = []
    metadata['item_tags'] = []
    metadata['item_id'] = []
    metadata['item_img0'] = []
    metadata['item_img1'] = []
    metadata['item_img2'] = []
    metadata['item_img3'] = []
    metadata['store_url'] = 'http://'+metadata['etsy_shopname']+'.etsy.com'

    for result in j['results']:
        item = result['MainImage']['listing_id']
        if repr(item) in items:
            metadata['item_title'].append(result['title'])
            shorter_url = re.split('\?',result['url'])
            metadata['item_url'].append(shorter_url[0])
            shorter_desc = re.split('\r\n',result['description'])
            metadata['item_desc'].append(shorter_desc[0])
            metadata['item_quantity'].append(result['quantity'])
            metadata['item_tags'].append(result['tags'])
            metadata['item_id'].append(result['MainImage']['listing_id'])
            metadata['item_img0'].append(result['MainImage']['url_75x75'])
            metadata['item_img1'].append(result['MainImage']['url_170x135'])
            metadata['item_img2'].append(result['MainImage']['url_570xN'])
            metadata['item_img3'].append(result['MainImage']['url_fullxfull'])

'''
'http://forkthecookbook.com/recipes/'+recipe-slug+'.'+fmt, where fmt is 'js' or 'json'
'''
def recipe(generator,metadata):
    if not ('cookbook' in metadata.keys()):
        return

    # fmt = 'json' #use json by default
    # if ('javascript' in metadata['cookbook']):
    #     fmt = 'js'

    #split recipe slugs and remove the fmt info passed
    recipes = metadata['cookbook'].split(',')
    recipes = sorted(set(recipes)) #removes duplicates
    for datum in recipes:
        if datum == 'js' or datum == 'json':
            recipes.remove(datum)

    base_url = 'http://forkthecookbook.com/recipes/'

    #remove slugs that 404
    for slug in recipes:

        recipe_url = base_url+slug
        r = urllib.urlopen(recipe_url)

        if(r.getcode()==404):
            print('found a value (%s) that wasnt a formatting option or a proper recipe slug in the cookbook metadata.'%slug)
            recipes.remove(slug)
            continue

    metadata['num_recipes'] = len(recipes)
    metadata['recipe_js'] = []
    metadata['recipe_json'] = []
    metadata['recipe_diff'] = []
    metadata['cook'] = []
    metadata['cook_url'] = []
    metadata['recipe_created'] = []
    metadata['recipe_created2'] = []
    metadata['recipe_src_url'] = []
    metadata['recipe_src_text'] = []
    metadata['recipe_img'] = []
    metadata['recipe_title'] = []
    metadata['recipe_serves'] = []
    metadata['recipe_slug'] = []
    metadata['recipe_url'] = []

    #get js
    for slug in recipes:

        recipe_url = base_url+slug
        recipe_js = recipe_url+'.js'
        r = urllib.urlopen(recipe_js)
        js = r.read()
        metadata['recipe_js'].append(js)

    #get json
    for slug in recipes:

        recipe_url = base_url+slug
        recipe_json = recipe_url+'.json'
        r = urllib.urlopen(recipe_json)
        j = r.read()
        j = j.replace('\\r\\n','')
        j = json.loads(j)
        metadata['recipe_json'].append(j)
        metadata['recipe_diff'].append(j['difficulty'])
        metadata['cook'].append(j['author']['userName'])
        cook_url = 'http://forkthecookbook.com/'+j['author']['userName']
        metadata['cook_url'].append(cook_url)
        metadata['recipe_created'].append(j['dateAdded'])
        metadata['recipe_created2'].append(j['humanDateTime'])
        metadata['recipe_src_url'].append(j['source']['url'])
        metadata['recipe_src_text'].append(j['source']['anchortext'])
        metadata['recipe_img'].append(j['mainPicture'])
        metadata['recipe_title'].append(j['title'])
        metadata['recipe_serves'].append(j['serves'])
        metadata['recipe_slug'].append(j['slug'])
        metadata['recipe_url'].append(recipe_url)

'''
'http://forkthecookbook.com/'+COOK+'.json'
'''
# def cook(generator,metadata):
#     pass

def register():
    signals.page_generator_context.connect(shop)
    signals.page_generator_context.connect(recipe)
    #signals.page_generator_context.connect(cook)
    signals.article_generator_context.connect(item)
