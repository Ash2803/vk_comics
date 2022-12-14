import os
import random
import traceback

import requests
from dotenv import load_dotenv


class VKError(Exception):
    pass


def get_comic():
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
    url = response.json()
    if 'error' in url:
        raise VKError(url['error'])
    return response.json()['response']['upload_url']


def upload_comic(upload_url):
    with open('comic.png', 'rb') as file:
        url = upload_url
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    uploaded_comic = response.json()
    if 'error' in uploaded_comic:
        raise VKError(uploaded_comic['error'])
    return response.json()


def save_wall_photo(vk_token, group_id, server, photo, photo_hash):
    params = {
        'access_token': vk_token,
        'server': server,
        'photo': photo,
        'hash': photo_hash,
        'group_id': group_id,
        'v': 5.131
    }
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
    response.raise_for_status()
    saved_photo = response.json()
    image_content = {
        'id': saved_photo['response'][0]['id'],
        'owner_id': saved_photo['response'][0]['owner_id'],
    }
    if 'error' in saved_photo:
        raise VKError(saved_photo['error'])
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
    published_photo = response.json()
    if 'error' in published_photo:
        raise VKError(published_photo['error'])
    return response.json()


def main():
    load_dotenv()
    vk_token = os.environ['VK_TOKEN']
    group_id = os.environ['GROUP_ID']
    try:
        comic = get_comic()
        uploaded_image = upload_comic(get_wall_upload_url(vk_token, group_id))
        saved_image = save_wall_photo(
            vk_token,
            group_id,
            uploaded_image['server'],
            uploaded_image['photo'],
            uploaded_image['hash']
        )
        publish_wall_photo(vk_token, group_id, saved_image['owner_id'], saved_image['id'], comic)
    except requests.exceptions.HTTPError:
        print(traceback.format_exc())
    finally:
        os.remove("comic.png")


if __name__ == '__main__':
    main()
