import json
import requests
import time
from pprint import pprint
from tqdm import tqdm
from operator import itemgetter


# Перебрать с json фото максимального размера + в имени добавить кол-во лаков фото
# фото сохранить на Яндекс Диск + инфо по фотографиям сохранять в json-файл

class VKinfo:
    def __init__(self, id_vk):
        self.id = id_vk

    def _get_photos(id_vk, token_vk):
        sizes_dict = {}
        sizes_dict_sorted = {}
        URL = 'https://api.vk.com/method/photos.get'
        params = {
            'user_id': id_vk,
            'access_token': token_vk, # токен и версия api являются обязательными параметрами во всех запросах к vk
            'v':'5.131',
            'album_id':'profile',
            'extended':'1',
            'photo_sizes':'1'
        }
        photos_data = requests.get(URL, params=params, verify=True).json()
        required_info = photos_data['response']['items']
        for object in required_info: # Получаем словари с лайками данными по фото
            photo_date = object['date']
            photo_likes = str(object['likes']['count'])
            if photo_likes in sizes_dict.keys():
                photo_likes = str(object['likes']['count']) + '_' + str(photo_date)
            sizes_dict[photo_likes] = object['sizes']   
        for date, photos_list in sizes_dict.items():  #сортируем словарь фото по размеру
            newlist = sorted(photos_list, key=itemgetter('height'), reverse=True) 
            sizes_dict_sorted[date] = newlist    
        for date, photos in sizes_dict_sorted.items(): # собрать первые картинки с URL в финал словарь
            final_dict_urls[date] = photos[0]  
            for photo in photos:  # собрать все разрешения картинок в формате width x height
                photo['size'] = f"{photo['height']} x {photo['width']}"            
                del photo['width'], photo['height'], photo['type']
        with open('data.json', 'w', encoding='utf-8') as f:  #запись json в файл
            json.dump(final_dict_urls, f, ensure_ascii=False, indent=4)
        pprint(final_dict_urls) 
        return final_dict_urls
 
    def _photo_counter(len_count_dict):  # считаем кол-во фото
        photo_counter = 0
        photo_counter = len(len_count_dict)  
        return photo_counter        
        

class YaUploader:
    def __init__(self, token_yandex):
        self.token = token_yandex
    
 
    def _get_link(self, path_to_file):
        # Получение ссылки на загрузку
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"   
        params = {"path": path_to_file, "overwrite": "true"}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
            }
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def _upload_file(self, path_on_disk: str, file_path_upload):
        """Метод загружает файл на яндекс диск"""  
        response_dict = self._get_link(path_to_file=path_on_disk)
        href = response_dict.get("href", "")   # возвращает пустую строку если нет ключа Хреф
        #заливка
        response = requests.post(href, data=open(file_path_upload, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print("Фото успешно загружено!")
        return

if __name__ == '__main__':
    print("Данная программа сделает бэкап ваших аватарок ВК на ЯндексДиск!")
    id_vk = input("Введите свой id Vkontakte:")
# Test account https://vk.com/begemot_korovin  - id552934290
    token_yandex = input("Введите свой токен YandexDisk:") 
    final_dict_urls = {}
    
    with open('token_vk.txt', 'r') as file_vk:
        token_vk = file_vk.read().strip()
        # Получить путь к загружаемому файлу и токен от пользователя
    VKinfo._get_photos(id_vk, token_vk)
    # print(VKinfo._photo_counter(final_dict_urls))
    uploader = YaUploader(token_yandex)
    for name, photos in final_dict_urls.items():  # проходимся циклом по словарю и загружаем фото по одному
        # for photo in photos:
        path_to_file = photos['url']               
        disk_url = f"disk:/vk-backup-photos/{name}.jpg"
        for i in tqdm(range(VKinfo._photo_counter(final_dict_urls)), desc = 'Uploading photos to Yandex Disk'): # прогресс загрузки
            time.sleep(0.2)
        result = uploader._upload_file(disk_url, path_to_file)  # загрузило только когда прописал полный путь к файлу disk: и название
        print(result)          
        


 


