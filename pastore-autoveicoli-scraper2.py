#!/usr/bin/python3

from bs4 import BeautifulSoup, Comment
import requests
import pandas
import json
import time

url = "http://www.pastoreautoveicoli.it/prodotti/"

# setting up the lists that will form our dataframe with all the resultstitles = []
#Image = []
#Title = []
#Price = []
#Rif = []
#Data = []
#Km = []
#Euro = []
#Link = []

#cols = ["Image", "Title", "Price", "Rif", "Data", "Km", "Euro", "Link"]
car_dict_list = {'Cars': []}

headers = {
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
}


async def fetch_url(session, url):
    async with session.get(url, timeout=60 * 60) as response:
        return await response.text()


def check_price():

    page = requests.get(url, headers=headers)

    #print(page)
    #print(page.text)

    soup = BeautifulSoup(page.text, "lxml")

    cars_container = soup.find_all('article', class_="car-entry")
    #print(cars_container[0])
    #print(len(cars_container))

    for car in cars_container:

        car_dict = {}

        #Get image
        image = car.find_all('img')[0]['src']
        #       Image.append(image)
        car_dict['Image'] = image
        #       print(image)

        #Get title
        title = car.find('h6', class_='title-item').get_text().strip()
        #      Title.append(title)
        car_dict['Title'] = title
        #print(title)

        #Get price
        price = car.find('div', class_='price').get_text().strip()
        #if price == "N.D.":
        #    converted_price = "N.D."
        #         Price.append(converted_price)
        #    car_dict['Price'] = converted_price
        #else:
        #    price = price.replace('€', '')
        #   price = price.replace(',', '')
        #   converted_price = float(price[0:len(price)])
        #        Price.append(converted_price)

        car_dict['Price'] = price
        #print(price)

        #Get info
        entry = car.find('ul', class_="list-entry").find_all('span')
        #print(entry)
        rif = entry[0].get_text().strip()
        data = entry[1].get_text().strip()
        km = entry[2].get_text().strip()
        emissioni = entry[3].get_text().strip()

        #   Rif.append(rif)
        #  Data.append(data)
        # Km.append(km)
        #Euro.append(emissioni)
        # print(rif,data,km,emissioni)
        if rif != '':
            car_dict['Rif'] = rif
        if data != '':
            car_dict['Data'] = data
        if km != '':
            car_dict['Km'] = km
        if emissioni != '':
            car_dict['Euro'] = emissioni

        #Get link
        link = car.find('a', class_="button orange")['href']
        #Link.append(link)
        car_dict['Link'] = link

        #print(link)
        #print(len(Link))

        get_page_data(link, car_dict)

        #print(car_dict['Rif. : '])

        car_dict_list['Cars'].append(car_dict)

    print("Inizio creazione file json")
    with open('pastore.json', 'w') as f:
        json.dump(car_dict_list, f)


#    pastore = pandas.DataFrame({
#        "Image": Image,
#        "Title": Title,
#        "Price": Price,
#        "Rif": Rif,
#        "Data": Data,
#        "Km": Km,
#        "Euro": Euro,
#        "Link": Link
#    })[cols]

#   pastore.to_csv('pastore_raw.csv')
#   pastore.to_excel('pastore_raw.xls')
#   pastore.to_json('pastore_raw.json')

#    pastore2 = pandas.DataFrame(car_dict_list)
#    pastore2.to_json('pastore2.json')

#pastore3 = json.dumps(car_dict_list)


def get_page_data(url_page, dict_func):

    page2 = requests.get(url_page, headers=headers)
    #print(page)
    #print(page.text)

    soup2 = BeautifulSoup(page2.content, "lxml")

    images = soup2.find('div', class_="car-slider").find('ul').find_all('img')
    image_list = []

    for img in images:
        #print(img['src'])
        image_list.append(img['src'])

#print(image_list)

    [
        x.decompose()
        for x in soup2.findAll(lambda tag: (not tag.contents or len(
            tag.get_text(strip=True)) <= 0) and not tag.name == 'br')
    ]

    sidebar = soup2.find_all('ul', class_="type-car-position")
    caratteristiche = sidebar[1]

    descrizione = soup2.find('div', class_='entry-item')
    descr_remove1 = descrizione.find('div', class_='wpcf7')
    descr_remove2 = descrizione.find('div', class_='cBox--related-items')
    descr_remove3 = descrizione.find('a', class_='backBUttonAuto')
    descr_remove4 = descrizione.find('div', class_='acc-box')
    #print(len(descrizione))
    #print(descr_remove1)
    if descr_remove1 is not None:
        descr_remove1.decompose()
    if descr_remove2 is not None:
        descr_remove2.decompose()
    if descr_remove3 is not None:
        descr_remove3.decompose()
    if descr_remove4 is not None:
        descr_remove4.decompose()

    for element in descrizione(text=lambda text: isinstance(text, Comment)):
        element.extract()

    keys = []
    p_value = []
    ul_value = []
    count = -1
    flag = False
    descr_dict = {}
    descr_dict_list = []
    key=''

    for child in descrizione.children:
        if (child != '\n'):    
            #print(child)
            #print(child.next_element)
            #print(child.text)
            tmp = child.text

            if (child.name == 'h5'):
                if (tmp[0:6] != 'F.A.Q.' and tmp[0:8] != 'Richiedi' and tmp[0:7]!='SCARICA'):
                    count = count + 1
                    flag = True
                    key = tmp.strip()
                    key = key.replace('.','').replace('/','_')
                    #keys.append(tmp)
                    descr_dict[count] = {'Titolo': key,'Contenuto':''}
                    #dict_func[key] = ""
                    #print(descr_dict[count])
                    #print(count)

            elif (child.name == 'p'):
                if (child.text != '' and child.text[0:1]!='I'):
                    if (flag):
                        #print(child.text)
                        descr_dict[count]['Contenuto'] += child.text + '\n'
                        #dict_func[key] += child.text + '\n'
                        #p_value.append(child.text)
                        #print(descr_dict[count])
                        #print(count)

            elif (child.name == 'ul'):
                if (flag):
                    #print(child.text)
                    descr_dict[count]['Contenuto'] += child.text + '\n'
                    #dict_func[key] += child.text + '\n'
                    #ul_value.append(child.text)
                    #print(descr_dict[count])
                    #print(count)


    #print(len(list(content)))
    #print(keys)
    #print(p_value)
    #print(ul_value)
    #time.sleep(60)

    #ul_value[0] = u

    caratteristiche_items = caratteristiche.find_all('li')

    #print(caratteristiche_items[0].find('b').get_text())

    for cara in caratteristiche_items:
        caratteristiche_nome = cara.find('b').get_text().replace(
            ':', '').replace('.', '').strip()
        caratteristiche_value = cara.find('span').get_text()
        #print(caratteristiche_nome)
        #print(caratteristiche_value)

        if caratteristiche_value != '-':
            dict_func[caratteristiche_nome] = caratteristiche_value

    #print(descrizione.text)
    #dict_func['Descrizione'] = descrizione.text
    dict_func['postImages'] = image_list
    #dict_func['h5'] = keys
    #dict_func['p'] = p_value
    #dict_func['ul'] = ul_value
    
    #descr_dict_list.append(descr_dict)
    dict_func["CarPage"] = descr_dict

check_price()