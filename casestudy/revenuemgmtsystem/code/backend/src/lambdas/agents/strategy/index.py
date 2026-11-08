import json
import os
import boto3
import uuid
from datetime import datetime

# Initialize DynamoDB Client
dynamodb = boto3.client('dynamodb')
TABLE_NAME = os.environ.get('INSIGHTS_TABLE_NAME')

def lambda_handler(event, context):
    print(f"Strategy Agent Event: {json.dumps(event)}")
    
    action_group = event.get('actionGroup')
    api_path = event.get('apiPath')
    http_method = event.get('httpMethod')
    
    # Bedrock sends requestBody properties as a list of {name, type, value} objects
    properties = event.get('requestBody', {}).get('content', {}).get('application/json', {}).get('properties', [])
    request_body = {p['name']: {'value': p.get('value')} for p in properties}
    
    response_body = {}
    http_status_code = 200
    
    try:
        if api_path == "/insights" and http_method == "POST":
            insight_id = str(uuid.uuid4())
            
            # Extract properties
            insight_type = request_body.get('type', {}).get('value')
            suggested_action = request_body.get('suggestedAction', {}).get('value')
            reasoning = request_body.get('reasoning', {}).get('value', 'N/A')
            
            item = {
                'id': {'S': insight_id},
                'type': {'S': insight_type},
                'suggestedAction': {'S': suggested_action},
                'reasoning': {'S': reasoning},
                'status': {'S': 'PENDING'},
                'createdAt': {'S': datetime.now().isoformat()}
            }
            
            dynamodb.put_item(TableName=TABLE_NAME, Item=item)
            
            response_body = {
                'application/json': {
                    'body': json.dumps({
                        'insightId': insight_id,
                        'status': 'PENDING'
                    })
                }
            }
        else:
            raise Exception(f"Unrecognized path: {api_path}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        http_status_code = 500
        response_body = {
            'application/json': {
                'body': json.dumps({'error': str(e)})
            }
        }

    action_response = {
        'actionGroup': action_group,
        'apiPath': api_path,
        'httpMethod': http_method,
        'httpStatusCode': http_status_code,
        'responseBody': response_body
    }
    
    return {
        'messageVersion': '1.0',
        'response': action_response
    }
