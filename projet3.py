# coding: utf-8
from multiprocessing import Pool
import unittest
import requests
from bs4 import BeautifulSoup
import re

URL_PAGE2 = "https://kim.fspot.org/cours/page2.html"
URL_PAGE3 = "https://kim.fspot.org/cours/page3.html"

# 1) Ecrire une fonction get_prices_from_url() qui extrait des informations à partir des 2 pages ci-dessus.
# Exemple get_prices_from_url(URL_PAGE2) doit retourner :
# {'Personal': {'price': '$5', 'storage': '1GB', 'databases': 1},
#  'Small Business': {'price': '$25', 'storage': '10GB', 'databases': 5},
#  'Enterprise': {'price': '$45', 'storage': '100GB', 'databases': 25}}

def get_prices_from_url(url):
    prices = {}
    r =requests.get(url) 
    soup = BeautifulSoup(r.content, features="lxml")
    #I create a dictionary as keys I put the text in h2 and as values a dictionary
    #with key "price" and values the prices
    for i in soup.findAll('div', attrs={'class': 'pricing-table-header'}):
        dico = {}
        p = i.find('span', attrs={'class':"pricing-table-price"})
        dico["price"]=p.text.strip().replace(" per month", "")
        prices[i.find('h2').text] = dico
    #I create a list of dictionaries, each dictonary contains as keys 'storage' and 'databases', 
    #as values the giga and the number of databases. I have erased in the values every character 
    #which was not inreresting for me
    l= []
    for i in soup.findAll('ul', attrs={'class': "pricing-table-list"}):
        d={}
        giga=i.findAll('li')[3].text.replace(" file storage", "")
        database=i.findAll('li')[4].text
        databasenumber=int(re.sub('\D', '', database)) 
        d['storage'] = giga
        d['databases'] = databasenumber
        l.append(d)    
    #I merge each dictionary of the list l to the corresponding dictionary in 
    #    
    v= [i for i in prices.values()]
    for x,y in zip(v,l):
        x.update(y)
    return prices


# 2) Ecrire une fonction qui extrait des informations sur une bière de beowulf
# Exemple URL: https://www.beerwulf.com/fr-fr/p/bieres/brouwerij-t-verzet-super-noah.33

def extract_beer_infos(url):
    infos ={}
    r =requests.get(url) 
    soup = BeautifulSoup(r.content, features="lxml")
    infos ={}
    infos['name']= soup.find('h1').text
    infos['note'] = int(re.sub('\D', '', soup.find('div', attrs ={'class':"stars"})['data-percent'])) 
    infos['price'] = float(re.sub(' €', '', soup.find('span', attrs ={'class':'price'}).text).replace(",", "."))
    infos['volume'] = int(re.sub('\D', '', soup.find('dd', attrs ={'class': 'small-6 medium-9 columns js-beer-volume'}).text))
     
    return infos


# Cette URL retourne un JSON avec une liste de bières
URL_BEERLIST_AUTRICHE = "https://www.beerwulf.com/fr-FR/api/search/searchProducts?country=Autriche&container=Bouteille"

# 3) Ecrire une fonction qui prend l'argument "url" retourne les informations sur une liste de bière via l'API de beowulf.
# Cette fonction doit retourner la liste des informations obtenues par la fonction extract_beer_infos() définie ci-dessus.
# Chercher comment optimiser cette fonction en utilisant multiprocessing.Pool pour paralléliser les accès web.
#
# Exemple de retour :
# [{'name': 'Engelszell Benno', 'note': 70, 'price': 4.29, 'volume': 33}
#  {'name': 'Engelszell Trappisten Weiße', 'note': 70, 'price': 3.39, 'volume': 33}
#  {'name': 'Engelszell Gregorius', 'note': 70, 'price': 4.49, 'volume': 33}
#  {'name': 'Bevog Rudeen Black IPA', 'note': 80, 'price': 4.49, 'volume': 33}
#  {'name': 'Bevog Tak Pale Ale', 'note': 70, 'price': 2.79, 'volume': 33}
#  {'name': 'Brew Age Affenkönig', 'note': 70, 'price': 3.49, 'volume': 33}
#  {'name': 'Stiegl Goldbraü', 'note': 70, 'price': 2.49, 'volume': 33}
#  {'name': 'Stiegl Columbus 1492', 'note': 70, 'price': 2.49, 'volume': 33}
#  {'name': 'Brew Age Hopfenauflauf', 'note': 70, 'price': 2.99, 'volume': 33}]


#Indedd the json does not contain any 'note, so my function returns:
# #[{'name': 'Engelszell Trappisten Weiße', 'price': 3.39, 'volume': 33},
#  {'name': 'Engelszell Benno', 'price': 3.2175, 'volume': 33},
#  {'name': 'Bevog Rudeen Black IPA', 'price': 4.49, 'volume': 33},
#  {'name': 'Engelszell Gregorius', 'price': 4.49, 'volume': 33},
#  {'name': 'Bevog Tak Pale Ale', 'price': 2.79, 'volume': 33},
#  {'name': 'Brew Age Affenkönig', 'price': 3.49, 'volume': 33},
#  {'name': 'Stiegl Goldbraü', 'price': 2.49, 'volume': 33},
#  {'name': 'Stiegl Columbus 1492', 'price': 2.49, 'volume': 33},
#  {'name': 'Brew Age Hopfenauflauf', 'price': 2.99, 'volume': 33}]


def extract_beer_list_infos(url):
    response = requests.get(url)
    data = response.json()
  
    # Collecter les pages de bières à partir du JSON
    beer_pages = data["items"]
    
    # Sequential version (slow):
    beers = []
    for i in beer_pages:
        dico={}
        dico['name']=i['title']
   
        dico['price']=i['displayInformationPrice']['filterPrice']
        dico['volume']=int(i['volume'])
        beers.append(dico)
    return beers



#Parallel version (faster):
def g(i):
    dico = {}
    dico['name']=i['title']
    dico['price']=i['displayInformationPrice']['filterPrice']
    dico['volume']=int(i['volume'])
    return dico 

def extract_beer_list_infos_seq(url):
    response = requests.get(url)
    data = response.json()
  
    # Collecter les pages de bières à partir du JSON
    beer_pages = data["items"]
    p = Pool()
    beers = p.map(g, beer_pages)
    p.close()
    p.join()
    beers
    return beers





class Lesson3Tests(unittest.TestCase):
    def test_01_get_prices_from_url_page2(self):
        prices = get_prices_from_url(URL_PAGE2)
        # We should have found 3 products:
        self.assertIsInstance(prices, dict)
        self.assertEqual(len(prices), 3)
        self.assertIn('Personal', prices)
        self.assertIn('Small Business', prices)
        self.assertIn('Enterprise', prices)

        personal = prices['Personal']
        self.assertIn('price', personal)
        self.assertIn('storage', personal)
        self.assertIn('databases', personal)
        self.assertEqual(personal['price'], '$5')
        self.assertEqual(personal['storage'], '1GB')
        self.assertEqual(personal['databases'], 1)

    def test_02_get_prices_from_url_page3(self):
        prices = get_prices_from_url(URL_PAGE3)
        self.assertIsInstance(prices, dict)
        self.assertEqual(len(prices), 4)
        self.assertEqual(
            prices['Privilege'],
            {'databases': 100, 'price': '$99', 'storage': '1TB'}
        )

    def test_03_extract_beer_list_infos(self):
        infos = extract_beer_list_infos(URL_BEERLIST_AUTRICHE)
        # >Il y a 9 bières autrichiennes :
        self.assertIsInstance(infos, list)
        self.assertEqual(len(infos), 9)
        # toutes ont 33cl :
        for beer in infos:
            self.assertEqual(beer['volume'], 33)


def run_tests():
    test_suite = unittest.makeSuite(Lesson3Tests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)


if __name__ == '__main__':
    run_tests()
