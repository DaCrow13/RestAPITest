import json
import boto3
import uuid
from flask import Flask, request

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UsersTable')
app = Flask(__name__)

def createUser(event, context):
    data = json.loads(event['body'])
    user_id = str(uuid.uuid4())
    table.put_item(
        Item={
            'id': user_id,
            'name': data['name'],
            'email': data['email']
        }
    )
    return {
        "statusCode": 200,
        "body": json.dumps({"id": user_id})
    }

def getUserById(event, context):
    user_id = event['pathParameters']['id']
    result = table.get_item(Key={'id': user_id})

    if 'Item' in result:
        return {
            "statusCode": 200,
            "body": json.dumps(result['Item'])
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "User not found"})
        }
