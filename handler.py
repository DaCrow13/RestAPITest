import json
import boto3
import uuid
from flask import Flask, request

# Initialize the DynamoDB resource and specify the table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UsersTable')

# Initialize the Flask app
app = Flask(__name__)

def generate_response(status_code, body):
    """
    Helper function to generate an HTTP response.
    Args:
        status_code (int): The HTTP status code.
        body (dict): The body of the response, typically a dictionary that will be converted to JSON.
    Returns:
        dict: A formatted response dictionary for API Gateway.
    """
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }

def create_user(event, context):
    """
    Lambda function to create a new user in the DynamoDB table.
    Args:
        event (dict): The event dictionary containing the request data.
        context: The context in which the function is executed.
    Returns:
        dict: A response dictionary with the status code and body.
    """
    try:
        # Parse the incoming JSON body
        data = json.loads(event['body'])

        # Generate a unique ID for the new user
        user_id = str(uuid.uuid4())

        # Add the new user to the DynamoDB table
        table.put_item(
            Item={
                'id': user_id,
                'name': data['name'],
                'email': data['email']
            }
        )

        # Return a success response with the user's ID
        return generate_response(200, {"id": user_id})

    except Exception as e:
        # Handle any errors that occur and return a 500 error response
        return generate_response(500, {"error": str(e)})

def get_user_by_id(event, context):
    """
    Lambda function to retrieve a user by ID from the DynamoDB table.
    Args:
        event (dict): The event dictionary containing the request data.
        context: The context in which the function is executed.
    Returns:
        dict: A response dictionary with the status code and body.
    """
    try:
        # Extract the user ID from the URL path parameters
        user_id = event['pathParameters']['id']

        # Retrieve the user data from DynamoDB
        result = table.get_item(Key={'id': user_id})

        # Check if the user was found in the table
        if 'Item' in result:
            # Return the user data if found
            return generate_response(200, result['Item'])
        else:
            # Return a 404 error if the user was not found
            return generate_response(404, {"error": "User not found"})

    except Exception as e:
        # Handle any errors that occur and return a 500 error response
        return generate_response(500, {"error": str(e)})

# Flask routes for local testing
@app.route('/user', methods=['POST'])
def create_user_flask():
    """
    Flask route to create a user for local testing.
    Returns:
        Response: A Flask response with the status code and body.
    """
    return create_user({"body": request.data}, None)

@app.route('/user/<id>', methods=['GET'])
def get_user_by_id_flask(id):
    """
    Flask route to get a user by ID for local testing.
    Args:
        id (str): The ID of the user to retrieve.
    Returns:
        Response: A Flask response with the status code and body.
    """
    return get_user_by_id({"pathParameters": {"id": id}}, None)

# Run the Flask app for local testing
if __name__ == "__main__":
    app.run(debug=True)
