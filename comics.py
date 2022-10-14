import os
import random

import requests
from dotenv import load_dotenv


def get_comics():
    current_comic = requests.get('https://xkcd.com/info.0.json')
    current_comic.raise_for_status()
    last_comic = current_comic.json()['num']
    random_comic_num = random.randint(0, last_comic)
    response = requests.get(f'https://xkcd.com/{random_comic_num}/info.0.json')
    response.raise_for_status()
    image = requests.get(response.json()['img'])
    image.raise_for_status()
    comics_name = 'comic.png'
    with open(comics_name, 'wb') as file:
        file.write(image.content)
    return response.json()['alt']


def vk_groups(vk_token):
    params = {
        'access_token': vk_token,
        'v': 5.124,
        'count': 10,
        'extended': 1
    }
    response = requests.get('https://api.vk.com/method/groups.get/', params=params)
    response.raise_for_status()
    return response.json()


def get_wall_upload_url(vk_token):
    params = {
        'access_token': vk_token,
        'group_id': '216491312',
        'v': 5.131
    }
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def upload_comics(upload_url):
    with open('comic.png', 'rb') as file:
        url = upload_url
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()


def save_wall_photo(vk_token, image):
    params = {
        'access_token': vk_token,
        'server': image['server'],
        'photo': image['photo'],
        'hash': image['hash'],
        'group_id': '216491312',
        'v': 5.131
    }
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
    response.raise_for_status()
    image_info = {
        'id': response.json()['response'][0]['id'],
        'owner_id': response.json()['response'][0]['owner_id'],
    }
    return image_info


def publish_wall_photo(vk_token, group_id, owner_id, media_id, text):
    params = {
        'access_token': vk_token,
        'from_group': 1,
        'v': 5.131,
        'attachments': f'photo{owner_id}_{media_id}',
        'owner_id': f'-{group_id}',
        'message': text
    }
    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()
    return response.json()


def main():
    load_dotenv()
    vk_token = os.environ['VK_TOKEN']
    group_id = '216491312'
    get_comics()
    uploaded_photo = upload_comics(get_wall_upload_url(vk_token))
    saved_photo = save_wall_photo(vk_token, uploaded_photo)
    print(publish_wall_photo(vk_token, group_id, saved_photo['owner_id'], saved_photo['id'], get_comics()))


if __name__ == '__main__':
    main()
