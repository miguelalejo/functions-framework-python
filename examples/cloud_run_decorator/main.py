# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This sample creates a function using the CloudEvents SDK
# (https://github.com/cloudevents/sdk-python)
import functions_framework
from flask import escape
from flask import abort

@functions_framework.http
def hello_http(request):
    """ Responds to a GET request with "Hello world!". Forbids a PUT request.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """  
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600'
    }

    
    if request.method == 'GET':
        return (hello_http_get(request), 200, headers)
    elif request.method == 'POST':
        return (hello_http_post(request), 200, headers)
    elif request.method == 'PUT':
        return (hello_http_put(request), 200, headers)
    else:
        return abort(405)

@functions_framework.cloud_event
def hello_cloud_event(cloud_event):
    return f"Received event with ID: {cloud_event['id']} and data {cloud_event.data}"


def hello_http_get(request):
    return "Hello world! My Friends"

def hello_http_post(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    print("POST START")
    print(request.form)
    fields = {}
    data = request.form.to_dict()
    for field in data:
        fields[field] = data[field]
        print('Field: %s' % field)   
        print('Value: %s' % data[field])
    fileBlob = data['fileBlob']
    fileName = data['fileName']
    if fileBlob is None or fileName is None:
        fileName = "None File"   
    
    return 'Hello {}!'.format(escape(fileName))


def hello_http_put(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    print("PUT START")
    request_json = request.get_json(silent=True)
    print(request_json)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'
    return 'Hello {}!'.format(escape(name))
