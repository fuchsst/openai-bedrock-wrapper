import requests
import json
import os

API_KEY = os.getenv('API_KEY')
API_URL = "http://127.0.0.1:5000/v1/chat/completions"


def chat_with_model():
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    conversation_history = []

    print("You can start chatting with the model. Type 'exit' to end the conversation.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        conversation_history.append({"role": "user", "content": user_input})

        payload = {
            "model": "gpt-4",
            "messages": conversation_history,
            "max_tokens": 100,
            "temperature": 0.7
        }

        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            response_data = response.json()
            assistant_message = response_data['choices'][0]['message']['content']
            print(f"Model: {assistant_message}")
            conversation_history.append({"role": "assistant", "content": assistant_message})
        else:
            print(f"Error: {response.status_code}, {response.text}")


if __name__ == '__main__':
    chat_with_model()
