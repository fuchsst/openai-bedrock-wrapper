import json
import os
import time

import boto3
import yaml
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import uuid


# Load environment variables
AWS_REGION = os.getenv('AWS_REGION')

# Load configuration from YAML file
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

app = Flask(__name__)


def chatgpt_to_bedrock(messages: List[Dict[str, str]]):
    return [{
        "role": message["role"],
        "content": [{
            "type": "text",
            "text": message["content"]
        }]
    } for message in messages]


def bedrock_to_chatgpt(response: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": response["id"],
        "object": "chat.completion",
        "created": int(time.time() * 1000),
        "model": response["model"],
        "system_fingerprint": "fp_44709d6fcb",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": response["role"],
                    "content": response["content"][0]["text"],
                },
                "finish_reason": response["stop_reason"],
            }
        ],
        "usage": {
            "prompt_tokens": response["usage"]["input_tokens"],
            "completion_tokens": response["usage"]["output_tokens"],
            "total_tokens": response["usage"]["input_tokens"]+response["usage"]["output_tokens"]
        }
    }


@app.route('/v1/chat/completions', methods=['POST'])
def invoke():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401

    api_key = auth_header.split()[1]
    if api_key not in config['api_keys']:
        return jsonify({"error": "Invalid API key"}), 403

    api_key_config = config['api_keys'][api_key]
    endpoint = api_key_config['endpoint']
    model_id = api_key_config['model_id']
    role_arn = api_key_config['aim_role']
    region_name = endpoint.split('.')[1]

    request_data = request.get_json()

    response = handle_request(
        request_data=request_data,
        model_id=model_id,
        endpoint=endpoint,
        role_arn=role_arn,
        region_name=region_name
    )
    return jsonify(response)


def handle_request(request_data,
                   model_id: str,
                   endpoint: str,
                   role_arn: str,
                   region_name: str):
    sts_client = boto3.client('sts')
    try:
        assumed_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='BedrockInvocation'
        )
    except (NoCredentialsError, PartialCredentialsError):
        return {"error": "Credentials error"}, 403

    credentials = assumed_role['Credentials']

    bedrock_client = boto3.client(
        'bedrock-runtime',
        region_name=region_name,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    request_body = {
        'anthropic_version': "bedrock-2023-05-31",
        'messages': chatgpt_to_bedrock(request_data['messages']),
        'max_tokens': request_data.get('max_tokens', 512),
        'temperature': request_data.get('temperature', 0.3),
        'top_p': request_data.get('top_p', 0.999)
    }
    print(request_body)

    response = bedrock_client.invoke_model(
        modelId=model_id,
        contentType='application/json',
        accept='application/json',
        body=json.dumps(request_body).encode('utf-8')
    )
    response_model_output = json.loads(response['body'].read().decode('utf-8'))

    print(response_model_output)
    return bedrock_to_chatgpt(response_model_output)


if __name__ == '__main__':
    app.run(debug=True)
