import requests
from config import TOKEN


def send_to_host(file_id):
    url = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}'
    file_path = requests.get(url=url).json()['result']['file_path']
    data = {
        'image': f'https://api.telegram.org/file/bot{TOKEN}/{file_path}',
        'name': 'name'
    }
    ans = requests.post(url='https://api.imgbb.com/1/upload?key=5bf5f797d6172fbd7cd993ebd2fba007',
                        data=data)
    return ans.json()['data']['url']
