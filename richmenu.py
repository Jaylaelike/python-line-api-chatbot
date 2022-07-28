channel_access_token = 'R/w/UnfJQoBGVwZYLwpoBoK+WOboUHivVVomw0BSQvPXUE4eVDRHL9HfFnZyeK9FBTbfpXIicHUGSG3gfckrw/K1TFsdCYpuQgMkuxQTZO3J2oJ5d35vUv1T8hNrNZYgSGc6AsDIbXd6t+213+QP1QdB04t89/1O/w1cDnyilFU='
import json
import requests

richdata = {
  "size": {
    "width": 2500,
    "height": 843
  },
  "selected": True,
  "name": "Rich Menu 1",
  "chatBarText": "กดเพื่อดูเมนู",
  "areas": [
    {
      "bounds": {
        "x": 1025,
        "y": 524,
        "width": 1475,
        "height": 319
      },
      "action": {
        "type": "message",
        "text": "ออกจากการสนทนา"
      }
    }
  ]
}


def RegisRich(Rich_json, channel_access_token):
    url = 'https://api.line.me/v2/bot/richmenu'
    Rich_json = json.dumps(Rich_json)
    Authorization = 'Bearer {}'.format(channel_access_token)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': Authorization}
    response = requests.post(url, headers=headers, data=Rich_json)
    print(str(response.json()['richMenuId']))
    return str(response.json()['richMenuId'])


def CreateRichMenu(ImageFilePath, Rich_json, channel_access_token):
    richId = RegisRich(Rich_json=Rich_json, channel_access_token=channel_access_token)
    url = 'https://api-data.line.me/v2/bot/richmenu/{}/content'.format(richId)
    Authorization = 'Bearer {}'.format(channel_access_token)
    headers = {'Content-Type': 'image/jpeg',
               'Authorization': Authorization}
    img = open(ImageFilePath, 'rb').read()
    response = requests.post(url, headers=headers, data=img)
    print(response.json())


CreateRichMenu(ImageFilePath='img_richmenu/richmenu.jpg', Rich_json=richdata,
               channel_access_token=channel_access_token)

# richmenu-6139854e51bc89df43a328d2e9bfdc34