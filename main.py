# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, render_template, request
import google.auth
from google.cloud import translate
import json
import random

app = Flask(__name__)
_, PROJECT_ID = google.auth.default()
TRANSLATE = translate.TranslationServiceClient()
PARENT = 'projects/{}'.format(PROJECT_ID)
SOURCE, TARGET = ('en', 'English'), ('es', 'Spanish')

# the English alphabet in a similar format to what's given by the Airtable API
x = '''

    {
  "records": [
    {
      "fields": {
        "English": "A",
        "Position": 1
      }
    },
    {
      "fields": {
        "English": "B",
        "Position": 2
      }
    },
    {
      "fields": {
        "English": "C",
        "Position": 3
      }
    },
    {
      "fields": {
        "English": "D",
        "Position": 4
      }
    },
    {
      "fields": {
        "English": "E",
        "Position": 5
      }
    },
    {
      "fields": {
        "English": "F",
        "Position": 6
      }
    },
    {
      "fields": {
        "English": "G",
        "Position": 7
      }
    },
    {
      "fields": {
        "English": "H",
        "Position": 8
      }
    },
    {
      "fields": {
        "English": "I",
        "Position": 9
      }
    },
    {
      "fields": {
        "English": "J",
        "Position": 10
      }
    },
    {
      "fields": {
        "English": "K",
        "Position": 11
      }
    },
    {
      "fields": {
        "English": "L",
        "Position": 12
      }
    },
    {
      "fields": {
        "English": "M",
        "Position": 13
      }
    },
    {
      "fields": {
        "English": "N",
        "Position": 14
      }
    },
    {
      "fields": {
        "English": "O",
        "Position": 15
      }
    },
    {
      "fields": {
        "English": "P",
        "Position": 16
      }
    },
    {
      "fields": {
        "English": "Q",
        "Position": 17
      }
    },
    {
      "fields": {
        "English": "R",
        "Position": 18
      }
    },
    {
      "fields": {
        "English": "S",
        "Position": 19
      }
    },
    {
      "fields": {
        "English": "T",
        "Position": 20
      }
    },
    {
      "fields": {
        "English": "U",
        "Position": 21
      }
    },
    {
      "fields": {
        "English": "V",
        "Position": 22
      }
    },
    {
      "fields": {
        "English": "w",
        "Position": 23
      }
    },
    {
      "fields": {
        "English": "X",
        "Position": 24
      }
    },
    {
      "fields": {
        "English": "Y",
        "Position": 25
      }
    },
    {
      "fields": {
        "English": "Z",
        "Position": 26
      }
    }
  ]
}

'''

# parse x
# it's currently just a string, so this looks for json formatting and stores the info in python dictionary
y = json.loads(x)

# it's a dictionary of dictionaries. The top-level dictionary 'y' has just one entry, called 'Records', which stores a sub-dictionary.
# this stores the sub dictionary 'z'
z = y.get('records')

@app.route('/', methods=['GET', 'POST'])
def translate(gcf_request=None):
    """
    main handler - show form and possibly previous translation
    """
    # initialize this_letter
    this_letter = "0"

    # Flask Request object passed in for Cloud Functions
    # (use gcf_request for GCF but flask.request otherwise)
    local_request = gcf_request if gcf_request else request

    #store information from the last time if available
    if (this_letter is not "0"):
        last_letter = this_letter
    #reset information to none otherwise
    else:
        last_letter = "0"
    #get letter for this time
    rand_num = random.randrange(1, 26)
    this_letter = z[rand_num].get('fields').get('English')


    # reset all variables (GET)
    text = translated = None

    # form submission and if there is data to process (POST)
    if local_request.method == 'POST':
        # get a new random position every time there is a request
        rand_num = random.randrange(1, 26)
        text = local_request.form['text'].strip()
        if text:
            data = {
                'contents': [text],
                'parent': PARENT,
                'target_language_code': TARGET[0],
            }
            # handle older call for backwards-compatibility
            try:
                rsp = TRANSLATE.translate_text(request=data)
            except TypeError:
                rsp = TRANSLATE.translate_text(**data)
            translated = rsp.translations[0].translated_text

    # create context & render template
    # this version passes a random letter and number instead of the translated text
    context = {
        'this_letter': this_letter,
        'last_letter': last_letter,
        'orig':  {'text': text, 'lc': SOURCE},
        'trans': {'text': z[rand_num].get('fields').get('English'), 'lc': z[rand_num].get('fields').get('Position')},
        'letter': z[rand_num].get('fields').get('English')
    }
    return render_template('index.html', **context)


if __name__ == '__main__':
    import os
    app.run(debug=True, threaded=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
