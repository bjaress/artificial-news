import requests
import base64

# https://cloud.google.com/text-to-speech/docs/basics

import logging

import api.error


class Client:
    def __init__(self, config, requests=requests):
        self.requests = requests
        self.url = f"{config.server}/v1/text:synthesize?key={config.api_key}"
        self.config = config

    def speak(self, story):
        response = self.requests.post(
            url=self.url,
            json={
                "input": {"text": story.text(self.config)},
                "voice": {
                    "languageCode": "en-gb",
                    "name": "en-GB-Standard-A",
                    "ssmlGender": "FEMALE",
                },
                "audioConfig": {"audioEncoding": "MP3"},
            },
        )
        api.error.check_response(response)
        return base64.b64decode(response.json()["audioContent"])
