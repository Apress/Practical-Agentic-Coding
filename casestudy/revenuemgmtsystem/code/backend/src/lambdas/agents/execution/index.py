import json
import os
import boto3
import uuid

# Initialize DynamoDB Client
dynamodb = boto3.client('dynamodb')
RATES_TABLE_NAME = os.environ.get('RATES_TABLE_NAME')

def lambda_handler(event, context):
    print(f"Execution Agent Event: {json.dumps(event)}")
    
    action_group = event.get('actionGroup')
    api_path = event.get('apiPath')
    http_method = event.get('httpMethod')
    
    properties = event.get('requestBody', {}).get('content', {}).get('application/json', {}).get('properties', [])
    request_body = {p['name']: {'value': p.get('value')} for p in properties}
    
    response_body = {}
    http_status_code = 200
    
    try:
        if api_path == "/rates/update" and http_method == "POST":
            # Extract params
            date = request_body.get('date', {}).get('value')
            room_type = request_body.get('roomType', {}).get('value')
            new_rate = request_body.get('newRate', {}).get('value')
            
            print(f"Updating Rate for {date} / {room_type} to {new_rate}")
            
            # Mock PMS Call or DB Update
            # dynamodb.put_item(...)
            
            transaction_id = str(uuid.uuid4())
            
            response_body = {
                'application/json': {
                    'body': json.dumps({
                        'transactionId': transaction_id,
                        'success': True
                    })
                }
            }
            
        elif api_path == "/inventory/promo" and http_method == "POST":
            promo_code = request_body.get('promoCode', {}).get('value')
            print(f"Launching Promo {promo_code}")
            
            response_body = {
                'application/json': {
                    'body': json.dumps({
                        'success': True
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
