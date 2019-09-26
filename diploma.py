from urllib.parse import urlencode
from pymongo import MongoClient
from pprint import pprint
import requests
import json
import time
import re

APP_ID = 7060537

BASE_URL = 'https://oauth.vk.com/authorize'
auth_data = {
    'client_id': APP_ID,
    'response_type': 'token',
    'v': '5.101'
}

TOKEN = ''


class User:
    def __init__(self, token, id):
        self.token = token
        self.id = id

    def get_params(self):
        params = dict(
            access_token=self.token,
            v='5.101',
            count=1000,
            has_photo=1,
            status=6,
            fields='interests'
        )
        if type(id) == int:
            params['user_id'] = {id}
        else:
            params['screen_name'] = {id}
        print('Доступные параметры поиска: sex (пол), age_from (минимальный возраст), age_to (максимальный '
              'возраст), hometown (город), religion (религия), position (должность/профессия), interests (интересы).')
        return params

    def get_partners(self):
        params = self.get_params()
        s_params_input = input('Введите параметры поиска: ')
        if 'sex' in s_params_input:
            sex_input = input('Введите пол партнера по коду: женщина - 1, мужчина - 2, не важно - 0 ')
            params['sex'] = sex_input
        if 'age_from' in s_params_input:
            age_from_input = input('Введите минимальный возраст партнера: ')
            params['age_from'] = age_from_input
        if 'age_to' in s_params_input:
            age_to_input = input('Введите максимальный возраст партнера: ')
            params['age_to'] = age_to_input
        if 'hometown' in s_params_input:
            hometown_input = input('Введите название города: ')
            params['hometown'] = hometown_input
        if 'religion' in s_params_input:
            religion_input = input('Введите религию партнера: ')
            params['religion'] = religion_input
        if 'position' in s_params_input:
                position_input = input('Введите должность партнера: ')
                params['position'] = position_input
        final_list = []
        response = requests.get(
            'https://api.vk.com/method/users.search',
            params
        )
        resp_json = response.json()['response']['items']
        if 'error' in resp_json and 'error_code' in resp_json['error'] and resp_json['error']['error_code'] == 6:
            time.sleep(2)
        counter = 0
        if 'interests' in s_params_input:
            with open('previous-results.txt', 'r+') as f:
                previous_results = f.read()
                if 'interests' in s_params_input:
                    interests_input = input('Введите интерес партнера: ')
                for person in resp_json:
                    try:
                        if 'interests' in s_params_input:
                            pattern = re.compile(interests_input, re.I)
                            if person['interests']:
                                result = re.search(pattern, person['interests'])
                                if result is None:
                                    continue
                                else:
                                    person_id = str(person['id'])
                                    if counter < 10 and person_id not in previous_results and \
                                            person['is_closed'] is False:
                                        final_list.append(person)
                                        f.write(f' {person_id} ')
                                        counter += 1
                    except KeyError:
                        continue
        else:
            with open('previous-results.txt', 'r+') as f:
                previous_results = f.read()
                for person in resp_json:
                    person_id = str(person['id'])
                    if counter < 10 and person_id not in previous_results and person['is_closed'] is False:
                        final_list.append(person)
                        f.write(f' {person_id} ')
                        counter += 1
        return final_list
        # pprint(final_list)

    def get_vk_data(self, method, params, tries=15):
        for i in range(tries):
            try:
                response = requests.get(
                    f'https://api.vk.com/method/{method}',
                    params
                )
                resp_json = response.json()['response']['items']
                return resp_json
            except KeyError:
                time.sleep(1)

    def add_top3_photos_json(self):
        final_list = list(self.get_partners())
        params = dict(
            access_token=self.token,
            v='5.101',
            album_id='profile',
            extended=1
        )
        for person in final_list:
            params['owner_id'] = person['id']
            resp_json = self.get_vk_data('photos.get', params, tries=15)
            top_dict = {'1': {'link': 0, 'likes_amount': 0},
                        '2': {'link': 0, 'likes_amount': 0},
                        '3': {'link': 0, 'likes_amount': 0}}
            for photo in resp_json:
                likes_amount = int(photo['likes']['count'])
                i = len(photo['sizes'])
                if likes_amount >= top_dict['1']['likes_amount']:
                    top_dict['1'] = {'link': photo['sizes'][i-1]['url'], 'likes_amount': likes_amount}
                elif likes_amount >= top_dict['2']['likes_amount']:
                    top_dict['2'] = {'link': photo['sizes'][i-1]['url'], 'likes_amount': likes_amount}
                elif likes_amount >= top_dict['3']['likes_amount']:
                    top_dict['3'] = {'link': photo['sizes'][i-1]['url'], 'likes_amount': likes_amount}
            person['top3_photos'] = top_dict
        with open('vkinder.json', 'w') as file:
            json.dump(final_list, file, ensure_ascii=False, indent=2)
        return final_list
        # pprint(final_list)

    def add_to_bd(self):
        client = MongoClient()
        mikhailutca_db = client['mikhailutca']
        vkinder_collection = obiwankenolya_db['vkinder']
        with open('vkinder.json') as file:
            vkinder_json = json.load(file)
            for person in vkinder_json:
                partner = {
                    'id': person['id'],
                    'first_name': person['first_name'],
                    'last_name': person['last_name'],
                    'top3_photos': person['top3_photos']
                }
                mikhailutca_db.vkinder_collection.insert_one(partner)
        return vkinder_collection


user1 = User(TOKEN, 6280082)

if __name__ == '__main__':
    # user1.get_partners()
    user1.add_top3_photos_json()
    user1.add_to_bd()
