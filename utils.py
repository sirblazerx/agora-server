import base64
import requests
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()

CUSTOMER_KEY = os.getenv('CUSTOMER_KEY')
CUSTOMER_SECRET = os.getenv('CUSTOMER_SECRET')

TEMP_TOKEN = os.getenv('TEMP_TOKEN')
APP_ID = os.getenv('APP_ID')
UID = random.randint(1, 232)

SECRET_KEY = os.getenv('SECRET_KEY')
ACCESS_KEY = os.getenv('ACCESS_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')


def generate_credential():
    # Generate encoded token based on customer key and secret
    credentials = CUSTOMER_KEY + ":" + CUSTOMER_SECRET

    base64_credentials = base64.b64encode(credentials.encode("utf8"))
    credential = base64_credentials.decode("utf8")
    return credential


credential = generate_credential()


def generate_resource(channel):

    payload = {
        "cname": channel,
        "uid": str(UID),
        "clientRequest": {}
    }

    headers = {}

    headers['Authorization'] = 'basic ' + credential

    headers['Content-Type'] = 'application/json'
    headers['Access-Control-Allow-Origin'] = '*'

    url = f"https://api.agora.io/v1/apps/{APP_ID}/cloud_recording/acquire"
    res = requests.post(url, headers=headers, data=json.dumps(payload))

    data = res.json()
    resourceId = data["resourceId"]

    return resourceId

# generate_resource()


def start_cloud_recording(channel):
    resource_id = generate_resource(channel)
    url = f"https://api.agora.io/v1/apps/{APP_ID}/cloud_recording/resourceid/{resource_id}/mode/mix/start"
    payload = {
        "cname": channel,
        "uid": str(UID),
        "clientRequest": {
            # "token": TEMP_TOKEN,

            "recordingConfig": {
                "maxIdleTime": 3,
            },

            "storageConfig": {
                "secretKey": SECRET_KEY,
                "vendor": 1,  # 1 is for AWS
                "region": 1,
                "bucket": BUCKET_NAME,
                "accessKey": ACCESS_KEY,
                "fileNamePrefix": [
                    "agora",
                ]
            },

            "recordingFileConfig": {
                "avFileType": [
                    "hls",
                    "mp4"
                ]
            },
        },
    }

    headers = {}

    headers['Authorization'] = 'basic ' + credential

    headers['Content-Type'] = 'application/json'
    headers['Access-Control-Allow-Origin'] = '*'

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    data = res.json()
    sid = data["sid"]

    return resource_id, sid


def stop_cloud_recording(channel, resource_id, sid):
    url = f"https://api.agora.io/v1/apps/{APP_ID}/cloud_recording/resourceid/{resource_id}/sid/{sid}/mode/mix/stop"

    headers = {}

    headers['Authorization'] = 'basic ' + credential

    headers['Content-Type'] = 'application/json;charset=utf-8'
    headers['Access-Control-Allow-Origin'] = '*'

    payload = {
        "cname": channel,
        "uid": str(UID),
        "clientRequest": {
        }
    }

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    data = res.json()
    resource_id = data['resourceId']
    sid = data['sid']
    server_response = data['serverResponse']
    mp4_link = server_response['fileList'][0]['fileName']
    m3u8_link = server_response['fileList'][1]['fileName']

    formatted_data = {'resource_id': resource_id, 'sid': sid,
                      'server_response': server_response, 'mp4_link': mp4_link, 'm3u8_link': m3u8_link}

    return formatted_data


def start_transcription(channel):
    url = f"https://api.agora.io/api/speech-to-text/v1/projects/{APP_ID}/join"
    payload = {
        "name": f"stt-task-{channel}",  # Required unique task name
        "languages": ["en-US", "es-ES"],  # Convert to array
        "maxIdleTime": 60,
        "rtcConfig": {
            "channelName": channel,
            "pubBotUid": "100",  # Bot that pushes subtitles to channel
            "pubBotToken": TEMP_TOKEN,
            "subBotUid": "100"
            # "subscribeAudioUids": []  # Optional, leave empty for all
        },
        "captionConfig": {
            "sliceDuration": 60,  # Duration of recorded subtitle files
            "storage": {
                "accessKey": ACCESS_KEY,
                "secretKey": SECRET_KEY,
                "bucket": BUCKET_NAME,
                "vendor": 1,  # 1 is for AWS
                "region": 1,
                "fileNamePrefix": ["rtt"]
            }
        }
    }

    headers = {}

    headers['Authorization'] = 'basic ' + credential

    headers['Content-Type'] = 'application/json'

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code != 200:
        raise Exception(f"API error: {res.status_code} {res.text}")
    data = res.json()
    if "agent_id" not in data:
        raise Exception(f"Unexpected response: {data}")
    return data


def start_transcription_simple(channel):
    url = f"https://api.agora.io/api/speech-to-text/v1/projects/{APP_ID}/join"
    payload = {
        "name": f"stt-task-simple-{channel}",  # Required unique task name
        "languages": ["en-US", "es-ES"],  # Convert to array
        "maxIdleTime": 60,
        "rtcConfig": {
            "channelName": channel,
            "pubBotUid": "100",  # Bot that pushes subtitles to channel
            "pubBotToken": TEMP_TOKEN,
            "subBotUid": "100"
            # "subscribeAudioUids": []  # Optional, leave empty for all
        }
        # No captionConfig - transcription happens but no recording/storage
    }

    headers = {}

    headers['Authorization'] = 'basic ' + credential

    headers['Content-Type'] = 'application/json'

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code != 200:
        raise Exception(f"API error: {res.status_code} {res.text}")
    data = res.json()
    if "agent_id" not in data:
        raise Exception(f"Unexpected response: {data}")
    return data


def stop_transcription(agent_id):
    url = f"https://api.agora.io/api/speech-to-text/v1/projects/{APP_ID}/agents/{agent_id}/leave"

    headers = {}

    headers['Authorization'] = 'basic ' + credential
    

    headers['Content-Type'] = 'application/json'

    payload = {}

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    data = res.json()
    return data
