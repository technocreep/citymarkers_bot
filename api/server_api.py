import requests
from config import SERVER_TOKEN


async def send_to_server(photo_url, data):

    url = 'http://vadimpotemkin.pythonanywhere.com/api/'
    data = {
        'name': data.get('name'),
        'latti': data.get('location')[0],
        'longi': data.get('location')[1],
        "author": data.get('author'),
        "addrdate": data.get('addrdate'),
        "photo": photo_url,
        "status": data.get('status'),
        "typeof": data.get('typeof')
    }
    headers = {
        'Authorization': f'Token {SERVER_TOKEN}'
    }
    response = requests.post(url=url,
                             data=data,
                             headers=headers)
    return response.status_code
