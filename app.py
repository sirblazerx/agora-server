from flask import Flask, render_template
import json
from flask_cors import CORS

from utils import start_cloud_recording, stop_cloud_recording, start_transcription, stop_transcription, start_transcription_simple

app = Flask(__name__)
CORS(app)


@app.route('/',)
def endpoints():
    app_routes = ['/start-recording/<channel>',
                  '/stop-recording/<channel>/<sid>/<resource_id>', '/start-transcribing/<channel>', '/start-transcribing-simple/<channel>', '/stop-transcribing/<agent_id>']
    return json.dumps(app_routes)


@app.route('/start-recording/<path:channel>', methods=['GET', 'POST'])
def start_recording(channel):
    resource_id, sid = start_cloud_recording(channel)
    context = {'sid': sid, "resource_id": resource_id}
    return json.dumps(context)


@app.route('/stop-recording/<path:channel>/<path:sid>/<path:resource_id>', methods=['GET', 'POST'])
def stop_recording(channel, sid, resource_id):
    data = stop_cloud_recording(channel, resource_id, sid)
    context = {}
    return json.dumps(data)


@app.route('/start-transcribing/<path:channel>', methods=['GET', 'POST'])
def start_transcribing(channel):
    data = start_transcription(channel)
    return json.dumps(data)


@app.route('/start-transcribing-simple/<path:channel>', methods=['GET', 'POST'])
def start_transcribing_simple(channel):
    data = start_transcription_simple(channel)
    return json.dumps(data)


@app.route('/stop-transcribing/<path:agent_id>/', methods=['GET','POST'])
def stop_transcribing(agent_id):
    print("Stopping transcription for agent_id:", agent_id)
    data = stop_transcription(agent_id)
    context = {}
    return json.dumps(data)


if __name__ == '__main__':
    app.run(debug=True)
