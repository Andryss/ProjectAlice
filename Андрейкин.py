from flask import Flask, request
import json
import requests
import random

words = {'words_hello': ["Привет! Назови своё имя!",
                         #"Вечер в хату! Как звать?",
                         "Здравствуйте, сир. Можно ли узнать ваше имя?"
                        ],
        'words_map': ["Я надеюсь, я вас удивила. Ну что ж, продолжим...",
                      "Вы же не для этого сюда пришли? Продолжим...",
                      "Ну интересная же функция, не так ли? Продолжаем...",
                      "А ты знал, что я именно это тебе покажу? Продолжаем...",
                      "Если что, зеленая метка - введенный адрес, а флажок - организация."
                     ],
        'words_stop': ["Результаты обнулены. И теперь назови новый адрес, который хочешь рассмотреть.",
                       "Все пропало! Все пропало! Начни заново! Скажи Адрес!",
                       "Хьюстон, у нас проблемы! Результаты потеряны! Начнем заново, скажи адрес.",
                       "Houston, We've Got a Problem! Results lost! Начнем сначала, а именно с нового адреса."
                      ],
        'words_yes_no': ["К сожалению, я еще не настолько продвинута, чтобы ответить в тему. Поэтому, сейчас просто тактично промолчу... А ты, пожалуйста, ответь на вопрос (если такой вообще был), как я просила или продолжи разговор.",
                        ],
        'words_help': ["Привет, я Алиса. Я занимаюсь поиском ближайших организаций. Всё просто: ты говоришь адрес и организацию, а я тебе - информацию об этой организации. Если ты захочешь сменить адрес поиска, просто скажи 'стоп'. А теперь ответь на предыдущий мой вопрос!"
                      ],
        'words_first_name_false': ["Не расслышала имя. Повтори, пожалуйста!",
                                   "Такого имени нет в моей базе данных. Повтори, пожалуйста!"
                                  ],
        'words_first_name_true': ['Приятно познакомиться, {}. Будем на ты. А теперь назови адрес в формате "Город, Улица, Номер дома" (например: "Москва, Льва Толстого, 16"), и я покажу тебе кое-что!',
                                  'Будем закомы, {}. Назови адрес в формате "Город, Улица, Номер дома" (например: "Санкт-Петербург, Пискарёвский проспект, 2"), и я постараюсь тебя удивить!'
                                 ],
        'words_address_not_get': ['Не расслышала адрес! Введи ответ в формате: "ГОРОД, УЛИЦА, НОМЕР ДОМА"!',
                                  'Пожалуйста, введи адрес в формате: "ГОРОД, УЛИЦА, НОМЕР ДОМА", как я просила!'
                                 ],
        'words_address_not_find': ["Не могу найти на карте этот адрес. Попробуй сказать точнее!"
                                  ],
        'words_address': ['Рассматриваю адрес: "{}". А теперь назови организацию, которую хочешь найти (например: "аптека").',
                          'Уже ищу по запросу "{}". Введите организацию (например: "больница").'
                         ],
        'words_obj_not_get': ["Слишком много слов, я путаюсь. Скажи только тип организации!"
                             ],
        'words_obj_not_find': ["Неверный тип организации! Скажи существующую организацию!",
                               "Не существует такой организации! Давай ты скажешь сущетвующую."
                              ],
        'words_error': ["Разработчики лоханулись",
                        "Упс... Непредвиденная ошибочка",
                        "На такой ответ разработчики не рассчитывали"
                       ],
        'words_bye': ["До свидания! Надеюсь, еще спишемся!",
                      "Прощай! Надеюсь, была полезной для тебя.",
                      "Ну, я пошла. Пока!"
                     ]
    }




#############################

def look(address, tup):
    try:
        toponym = address
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {"geocode": toponym, "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)

        # Преобразуем ответ в json-объект
        json_response = response.json()
        # Получаем первый топоним из ответа геокодера.
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        chemist = search(toponym_coodrinates, tup)
        return chemist
    except:
        return None



def search(address, name):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    search_params = {
        "apikey": api_key,
        "text": str(name),
        "lang": "ru_RU",
        "ll": str(address),
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первую найденную организацию.
    organization = json_response["features"][0]
    # Название организации.
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    # Адрес организации.
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    o = org_address.split(',')
    org_address = ', '.join([o[0],o[1]])
    org_time = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
    org_phone = organization["properties"]["CompanyMetaData"]["Phones"][0]["formatted"]
    org_link = organization["properties"]["CompanyMetaData"]["Links"][0]["href"]
    # Получаем координаты ответа.
    point = ",".join([str(organization["geometry"]["coordinates"][0]), str(organization["geometry"]["coordinates"][1])])
    address = ",".join(address.split())

    link = "https://static-maps.yandex.ru/1.x/?pt={},pm2gnm~{},flag&l=map".format(address, point)

    stroka = "Организация: \t{}\nАдрес: \t{}\nРасписание: \t{}\nТелефон: \t{}\nПодробнее по ссылке: \t{}".format(org_name, org_address, org_time, org_phone, org_link)

    return (stroka, point, link)



#############################






# импортируем функции из нашего второго файла geo

app = Flask(__name__)



# Добавляем логирование в файл. Чтобы найти файл,
# перейдите на pythonwhere в раздел files, он лежит в корневой папке

sessionStorage = {}
first_name = None



@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    return json.dumps(response)




def handle_dialog(res, req):
    global words
    try:
        user_id = req['session']['user_id']
        res['response']['buttons'] = [
                    {
                        'title': "Справка о боте",
                        'hide': True
                    }
            ]

        if req['session']['new']:
            res['response']['text'] = random.choice(words['words_hello'])
            sessionStorage[user_id] = {
                'first_name': None,
                'address': None,
                'obj': None
            }
            return



        if (" ".join(req['request']['nlu']['tokens']) == "справка о боте"):
            res['response']['text'] = random.choice(words['words_help'])
            return


        if ("пока" in req['request']['nlu']['tokens']):
            res['response']['text'] = random.choice(words['words_bye'])
            res['response']['end_session'] = True
            return


        if ("стоп" in req['request']['nlu']['tokens']) or ("остановись" in req['request']['nlu']['tokens']):
            sessionStorage[user_id] = {
                'first_name': sessionStorage[user_id]['first_name'],
                'address': None,
                'obj': None
            }
            res['response']['text'] = random.choice(words['words_stop'])
            return


        if ("да" in req['request']['nlu']['tokens']) or ("нет" in req['request']['nlu']['tokens']):
            res['response']['text'] = random.choice(words['words_yes_no'])
            return


        if ("показать" in req['request']['nlu']['tokens']) and ("карте" in req['request']['nlu']['tokens']):
            res['response']['text'] = random.choice(words['words_map'])
            return


        if sessionStorage[user_id]['first_name'] is None:
            first_name = get_first_name(req)
            if first_name is None:
                res['response']['text'] = random.choice(words['words_first_name_false'])
            else:
                sessionStorage[user_id]['first_name'] = first_name
                res['response']['text'] = random.choice(words['words_first_name_true']).format(first_name.title())
            return


        elif sessionStorage[user_id]['address'] is None:
            address = get_address(req)
            if address is None:
                res['response']['text'] = random.choice(words['words_address_not_get'])
            else:
                nearest_test = look(address, 'магазин')
                if nearest_test is None:
                    res['response']['text'] = random.choice(words['words_address_not_find'])
                else:
                    sessionStorage[user_id]['address'] = address
                    res['response']['text'] = random.choice(words['words_address']).format(address.title())
            return


        elif sessionStorage[user_id]['obj'] is None:
            obj = get_obj(req)
            if obj is None:
                res['response']['text'] = random.choice(words['words_obj_not_get'])
                return

            else:
                nearest_test = look(sessionStorage[user_id]['address'], obj)
                if nearest_test is None:
                    res['response']['text'] = random.choice(words['words_obj_not_find'])
                    return

                else:
                    sessionStorage[user_id]['obj'] = obj

        res['response']['buttons'].append(
                    {
                        'url': str(nearest_test[2]),
                        'title': 'Показать на карте',
                        'hide': False
                    }
                )
        res['response']['text'] = nearest_test[0]
        sessionStorage[user_id] = {
                'first_name': sessionStorage[user_id]['first_name'],
                'address': sessionStorage[user_id]['address'],
                'obj': None
            }
        return


    except Exception:
        res['response']['text'] = random.choice(words['words_error'])



def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value']:
                cities.append(entity['value']['city'])
    return cities



def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)



def get_address(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.GEO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            if len(entity['value']) >= 3:
                info = [entity['value']['city'], entity['value']['street'], entity['value']['house_number']]
                if len(info) == 3:
                    return ", ".join(info)
                else:
                    return None



def get_obj(req):
    tokens = req['request']['nlu']['tokens']
    try:
        return " ".join(tokens)
    except:
        return None



if __name__ == '__main__':
    app.run()