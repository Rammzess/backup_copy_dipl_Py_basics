import json
import requests
import time
from pprint import pprint
from tqdm import tqdm
from operator import itemgetter
import os
from dotenv import load_dotenv


class UserException(Exception):
    pass


class VKinfo:
    def __init__(self, id_vk):
        self.id = id_vk

    def _get_photos(id_vk, token_vk):
        URL = 'https://api.vk.com/method/photos.get'
        params = {
            'user_id': id_vk,
            'access_token': token_vk,
            'v': '5.131',
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1'
        }
        response = requests.get(URL, params=params, verify=True)
        response.raise_for_status()
        if response.ok:
            photos_data = response.json()
        else:
            raise UserException("Возникла ошибка при сполучении данных!")
        required_info = photos_data['response']['items']
        for object in required_info:
            photo_date = object['date']
            photo_likes = str(object['likes']['count'])
            if photo_likes in final_dict_urls.keys():
                photo_likes = (str(object['likes']['count'])
                + '_' + str(photo_date)
                )
            sizes_list = sorted(
                object['sizes'],
                key=itemgetter('height'),
                reverse=True
            )
            final_dict_urls[photo_likes] = sizes_list[0]
            final_dict_urls[photo_likes]['size'] = (
                f"{final_dict_urls[photo_likes]['height']}"
                + f" x {final_dict_urls[photo_likes]['width']}"
            )
            del (final_dict_urls[photo_likes]['width'],
                final_dict_urls[photo_likes]['height'],
                final_dict_urls[photo_likes]['type']
            )
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_dict_urls, f,
                      ensure_ascii=False, indent=4
            )
        # pprint(final_dict_urls)
        return final_dict_urls


class YaUploader:
    def __init__(self, token_yandex):
        self.token = token_yandex

    def _check_request(self, response):
        response.raise_for_status()
        try:
            response.ok
        except requests.exceptions.HTTPError:
            raise UserException("Возникла ошибка!")
        return

    def _get_info(self, dir_name):
        folder_URL = "https://cloud-api.yandex.net/v1/disk/resources/public"
        params = {
            "type": "dir"
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.token
        }
        response = requests.get(folder_URL, headers=headers, params=params)
        dict_dir = response.json()['items']
        for dict in dict_dir:
            if dir_name in dict['path']:
                return True
            else:
                return False

    def _publish_res(self, res_name):
        URL = "https://cloud-api.yandex.net/v1/disk/resources/publish"
        headers = {
            'Authorization': self.token
        }
        params = {
            'path': res_name
        }
        requests.put(URL, headers=headers, params=params)
        return

    def _create_folder(self, folder_name):
        folder_URL = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {
            "path": folder_name,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.token
        }
        response = requests.put(folder_URL, headers=headers, params=params)
        self._publish_res(folder_name)
        self._check_request(response)
        return

    def _upload_file(self, path_on_disk: str, file_path_upload):
        headers = {
            'Authorization': self.token
        }
        params = {
            "url": file_path_upload,
            "path": path_on_disk,
            "overwrite": "true"
        }
        # requests.utils.quote-преобразование текста в кодированный формат url
        response = requests.post(
            "https://cloud-api.yandex.net/v1/disk/resources/upload",
            params=params,
            headers=headers
        )
        self._check_request(response)
        for i in tqdm(range(1),
                      desc='Uploading photo to Yandex Disk'):
            time.sleep(0.2)
        return


def photo_uploader(token_yandex, token_vk, id_vk):
    VKinfo._get_photos(id_vk, token_vk)
    uploader = YaUploader(token_yandex)
    folder_name = "/vk-backup-photos"
    fold_info = uploader._get_info(folder_name)
    if fold_info is True:
        pass
    else:
        uploader._create_folder(folder_name)
    for name, photos in final_dict_urls.items():
        path_to_file = photos['url']
        disk_url = f"disk:{folder_name}/{name}.jpg"
        uploader._upload_file(disk_url, path_to_file)
    pprint("Файлы Успешно Загружены!")
    return


if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), 'config.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    print("Данная программа сделает бэкап ваших аватарок ВК на ЯндексДиск!")
    id_vk = input("Введите свой id Vkontakte:")
# https://vk.com/begemot_korovin - id552934290
    token_yandex = os.getenv('YANDEX_KEY')
    token_vk = os.getenv('VK_KEY')
    final_dict_urls = {}
    start_time = 0

photo_uploader(token_yandex, token_vk, id_vk)
