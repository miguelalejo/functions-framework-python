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
import flask
from flask import escape
from flask import abort
import requests
import pymongo
from pymongo.errors import BulkWriteError,DuplicateKeyError
from google.cloud import pubsub_v1
from MongoService import *
import json
from bson import ObjectId
from datetime import date, datetime
import base64

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
    

def createObject(groupId,blobXml,fileName):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """   
    uri = "cluster0.2gzpcvj.mongodb.net/?retryWrites=true&w=majority"
    user = "m001-student"
    password = "m001-mongodb-basics"    
    mgConectorServ = MongoServiceConector(uri, user, password)
    try:
        mgConectorServ.insert_one(bd_name="edocuments",collecion="bills", value={'group_id': groupId, 'blob_xml': blobXml,  'file_name': fileName}) 
    except DuplicateKeyError as e:
        print(e)
        print("Errro insert")

def send_pub(dataVal):
    publisher = pubsub_v1.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    project_id = "bazarservicios"
    topic_id = "DEVIVA_XML_PROCESOR_GROUPID_EVENT"
    topic_path = publisher.topic_path(project_id, topic_id)    
    # Data must be a bytestring
    data = json.dumps(dataVal).encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data)
    print(future.result())

    print(f"Published messages to {topic_path}.")

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
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
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
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """    
    uri = "cluster0.2gzpcvj.mongodb.net/?retryWrites=true&w=majority"
    user = "m001-student"
    password = "m001-mongodb-basics"    
    mgConectorServ = MongoServiceConector(uri, user, password)    
    documents = mgConectorServ.findSort(bd_name="edocuments",collecion="excel_dev_reports",query= {},projection={ "group_id": 1, "_id": 1 , 'ruc': 1,'date': 1},sortValue='date')
    listReportes = []
    for doc in documents:
        if "group_id" in doc.keys():
            print(doc)
            print("Generar Blob")
            groupId = doc["group_id"]
            idTran = doc["_id"]
            ruc = doc["ruc"]
            date = doc["date"]
            reporte = {
            "groupId": groupId,
            "idTran": idTran,
            "ruc": ruc,
            "date":date
            }                
            listReportes.append(reporte)

    return JSONEncoder().encode(listReportes)

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
    fileName = None  
    
    if 'fileName' in fields:
        fileName = data['fileName']
    idTransaction = None
    if 'idTransaction' in fields:
        idTransaction = int(float(data['idTransaction']))
    
    dataFiles = request.files.to_dict()        
    fieldsFiles = {}    
    for field in dataFiles:
        fieldsFiles[field] = dataFiles[field]        
        print('Field File: %s' % field)
    
    fileWapperBlob = None
    if 'fileBlob' in fieldsFiles:
        fileWapperBlob = dataFiles['fileBlob']
        print('Type File: %s' % type(fileWapperBlob))
        filename = fileWapperBlob.filename
        print('File Name: %s' % filename)
        fBlob = fileWapperBlob.read()
    print("CONNECT MONGO")
    createObject(groupId=idTransaction,blobXml=fBlob,fileName=filename)    
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
    fields = {}
    data = request.form.to_dict()        
    for field in data:
        fields[field] = data[field]        
        print('Field: %s' % field)   
        print('Value: %s' % data[field])       
    
    idTransaction = None
    nFiles = 0
    if 'idTransaction' in fields:
        idTransaction = int(float(data['idTransaction']))
    if 'nFiles' in fields:
        nFiles = int(float(data['nFiles']))
    print("SEND PUB")
    dataVal = {"idTransaction":idTransaction,"nFiles":nFiles}
    print("Data",dataVal)
    send_pub(dataVal)
    return 'Hello {}!'.format(escape(idTransaction))
