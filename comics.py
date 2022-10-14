import os
from pprint import pprint

import requests
from dotenv import load_dotenv


def get_comics():
    response = requests.get('https://xkcd.com/353/info.0.json')
    response.raise_for_status()
    image = requests.get(response.json()['img'])
    image.raise_for_status()
    comics_name = 'Comics.png'
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
    with open('Comics.png', 'rb') as file:
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


def publish_wall_photo(vk_token, owner_id, media_id, text):
    params = {
        'access_token': vk_token,
        'group_id': '216491312',
        'from_group': 1,
        'v': 5.131,
        'attachments': f'photo{owner_id}_{media_id}',
        'owner_id': owner_id,
        'message': text
    }
    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()
    return response.json()


def main():
    load_dotenv()
    vk_token = os.environ['VK_TOKEN']
    photo_message = "I wrote 20 short programs in Python yesterday.  It was wonderful.  Perl, I'm leaving you."
    # print(get_comics())
    # # get_comics()
    # # print(get_wall_upload_address(vk_token))
    upload_photo = upload_comics(get_wall_upload_url(vk_token))
    a = save_wall_photo(vk_token, upload_photo)
    print(publish_wall_photo(vk_token, a['owner_id'], a['id'], photo_message))


if __name__ == '__main__':
    main()
