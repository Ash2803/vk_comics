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


def get_wall_upload_url(vk_token, group_id):
    params = {
        'access_token': vk_token,
        'group_id': group_id,
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


def save_wall_photo(vk_token, group_id, image):
    params = {
        'access_token': vk_token,
        'server': image['server'],
        'photo': image['photo'],
        'hash': image['hash'],
        'group_id': group_id,
        'v': 5.131
    }
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
    response.raise_for_status()
    image_content = {
        'id': response.json()['response'][0]['id'],
        'owner_id': response.json()['response'][0]['owner_id'],
    }
    return image_content


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
    try:
        uploaded_image = upload_comics(get_wall_upload_url(vk_token, group_id))
    except KeyError:
        print("KeyError, please check request parameters")
        os.remove("comic.png")
    except ConnectionError:
        print('Connection error')
        os.remove("comic.png")
    try:
        saved_image = save_wall_photo(vk_token, group_id, uploaded_image)
    except KeyError:
        print("KeyError, please check request parameters")
        os.remove("comic.png")
    except ConnectionError:
        print('Connection error')
        os.remove("comic.png")
    try:
        publish_wall_photo(vk_token, group_id, save_image['owner_id'], save_image['id'], get_comics())
    except KeyError:
        print("KeyError, please check request parameters")
        os.remove("comic.png")
    except ConnectionError:
        print('Connection error')
        os.remove("comic.png")
    os.remove("comic.png")


if __name__ == '__main__':
    main()
