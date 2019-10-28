import time
from pprint import pprint
import requests
import config
from dbconnect import datdb as db
import json
import re


class User:
    token = 'cb6c56d4f9f54d37c74990608bcebd40b1043b054cd716404f5d40eda33c620ccb25ba78bb64e709f2454'

    def __init__(self, user_id):
        URL_API_VK = 'https://api.vk.com/method/users.get'
        params = {'access_token': self.token,
                  'user_ids': user_id,
                  'fields': config.fields,
                  'v': '5.101'}
        time.sleep(1)
        try:
            response = requests.get(URL_API_VK, params=params)
        except:
            print('Ошибка подключения')
        else:
            res = {}
            while 'response' not in res:
                res = response.json()
                if 'response' in res:
                    self.__dict__.update(res['response'][0])
                    self.weight = 0
                else:
                    self.token = input('токен неверный, введите токен: ')

    def search_list_ids_by_parameters(self, count=1000, age_from=0, age_to=0,
                                      id_city=0, sex=0, status=0):
        URL_API_VK = 'https://api.vk.com/method/users.search'
        params = {'access_token': self.token,
                  'count': count,
                  'age_from': age_from,
                  'age_to': age_to,
                  'city': id_city,
                  'sex': sex,
                  'status': status,
                  'v': '5.52'}
        time.sleep(1)
        try:
            response = requests.get(URL_API_VK, params=params)
        except:
            pass
        else:
            res = response.json()
            search_list = []
            if 'response' in res:
                for item in res['response']['items']:
                    search_list.append(item['id'])
            return search_list

    def search(self):
        if hasattr(self, 'city'):
            search_id_city = self.city['id']
        else:
            search_id_city = 0

        sexual_self = ''
        while sexual_self not in config.sexual:
            sexual_self = input('ориентация: введите geter, gom или bi - ')

        if hasattr(self, 'sex'):
            self_sex = self.sex
        else:
            self_sex = 0

        if sexual_self == 'gom':
            search_sexes = [0, self_sex]
        elif sexual_self == 'bi':
            search_sexes = config.sex
        else:  
            search_sexes = list(set(config.sex).difference({0, self_sex}))

        search_statuses = config.relation

        search_age_from = 0
        search_age_to = 100
        while (int(search_age_from) <= 0) or (int(search_age_to) >= 100):
            search_age_from = input('введите диапазон возраста для поиска. От: ')
            search_age_to = input('До: ')

        list_ids_saved_to_db = []
        list_users_saved_to_db = list(db['users'].find())
        for user_saved in list_users_saved_to_db:
            list_ids_saved_to_db.append(user_saved.get('id'))
        print('list_ids_saved_to_db:')
        print(list_ids_saved_to_db)

        iter = 0
        res_search = set()
        while (len(res_search) < 10) and (iter < 10):
            for search_sex in search_sexes:
                for search_status in search_statuses:
                    set_ids = set(self.search_list_ids_by_parameters(count=5,
                                                                     age_from=search_age_from,
                                                                     age_to=search_age_to,
                                                                     id_city=search_id_city,
                                                                     sex=search_sex,
                                                                     status=search_status))
                    res_search.update(set_ids)
            iter += 1
         
            res_search.difference_update(set(list_ids_saved_to_db))
        return list(res_search)

    def get_weight(self, other_user):
        weight = 0
     
        if hasattr(other_user, 'common_count'):
            if other_user.common_count > 0:
                weight += config.weight_common_friends
      
        list_groups_self = self.get_list_ids_groups()
        list_groups_other = other_user.get_list_ids_groups()
        if set(list_groups_self).intersection(set(list_groups_other)):
            weight += config.weight_common_groups
      
        if self.get_intersection_interests(other_user, 'interests'):
            weight += config.weight_interests
    
        if self.get_intersection_interests(other_user, 'music'):
            weight += config.weight_music
     
        if self.get_intersection_interests(other_user, 'books'):
            weight += config.weight_books
        return weight

    def get_intersection_interests(self, other_user, iterest='interests'):
        if hasattr(self, iterest) and hasattr(other_user, iterest):
            pattern = "[\w]+"
            self_result = re.findall(pattern, getattr(self, iterest), re.U)
            other_user_result = re.findall(pattern, getattr(other_user, iterest), re.U)
            if set(self_result).intersection(set(other_user_result)):
                return 1
            else:
                return 0

    def get_list_users_with_weight(self):
        list_ids = self.search()
        print('list_ids_not_saved_to_database:')
        print(list_ids)
        list_users = []
        for id in list_ids:
            new_user = User(id)
            new_user.weight = self.get_weight(new_user)
            list_users.append(new_user)
            print(new_user.weight)
        return list_users

    def get_list_photo_profile(self):
        URL_API_VK = 'https://api.vk.com/method/photos.get'
        params = {'access_token': self.token,
                  'owner_id': self.id,
                  'album_id': 'profile',
                  'extended': 1,
                  'count': 1000,
                  'v': '5.101'}
        try:
            response = requests.get(URL_API_VK, params=params)
        except:
            pass
        else:
            res = response.json()
            if 'response' in res:
                list_photos = res['response']['items']
                list_photos_top3 = sorted(list_photos,
                                          key=lambda x: x['likes']['count'],
                                          reverse=True)[0:3]
                list_photos_top3_only_url = []
                for photo in list_photos_top3:
                    list_photos_top3_only_url.append(photo['sizes'][-1]['url'])
                return list_photos_top3_only_url

    def get_list_top(self):
        list_users = self.get_list_users_with_weight()
        list_dict = []
        for user in list_users:
            dict = user.__dict__
            for key in list(dict.keys()):
                if key not in ['id', 'weight']:
                    del dict[key]
            dict['photos_top3'] = user.get_list_photo_profile()
            list_dict.append(dict)

        sorted_list_top10_dict = sorted(list_dict,
                                        key=lambda user: user['weight'],
                                        reverse=True)[0:10]
     
        if sorted_list_top10_dict:
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(sorted_list_top10_dict, f, ensure_ascii=False, indent=4)
            db['users'].insert_many(sorted_list_top10_dict)
        return sorted_list_top10_dict

    def get_list_ids_groups(self, extended='0'):
        URL_API_VK = 'https://api.vk.com/method/groups.get'
        params = {'access_token': self.token, 'user_id': self.id, 'v': '5.101', 'extended': extended,
                  'count': '1000'}
        while True:
            print('_')
            time.sleep(1)
            try:
                response = requests.get(URL_API_VK, params=params)
            except:
                pass
            else:
                res = response.json()
                if 'response' in res:
                    res_res = res['response']
                    if 'items' in res_res:
                        return res_res['items']
                    else:
                        return []
                else:
                    return []


if __name__ == '__main__':
    id_me = 6280082
    me = User(id_me)
    pprint(me.__dict__)
    print('Начать поиск')
    pprint(me.get_list_top())

