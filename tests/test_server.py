import unittest
from api import server
from api.server import chatgpt_to_bedrock


class TestChatgptToBedrock(unittest.TestCase):

    def setUp(self):
        self.test_data = [
            {
                "role": "system",
                "content": "You are using Linux"
            },
            {
                "role": "user",
                "content": "Help me set up IntelliJ"
            }
        ]
        self.expected_data = [
            {
                "role": "system",
                "content": [{
                    # "type": "text",
                    "text": "You are using Linux"
                }]
            },
            {
                "role": "user",
                "content": [{
                    # "type": "text",
                    "text": "Help me set up IntelliJ"
                }]
            }
        ]

    def test_chatgpt_to_bedrock(self):
        self.assertEqual(chatgpt_to_bedrock(self.test_data), self.expected_data)

    def test_empty_list(self):
        self.assertEqual(chatgpt_to_bedrock([]), [])

    def test_type_error(self):
        with self.assertRaises(TypeError):
            chatgpt_to_bedrock(None)
        with self.assertRaises(TypeError):
            chatgpt_to_bedrock('invalid')
        with self.assertRaises(TypeError):
            chatgpt_to_bedrock(123)

    def tearDown(self):
        pass


class TestBedrockToChatGpt(unittest.TestCase):

    def test_bedrock_to_chatgpt(self):
        # Create a mock response
        mock_response = {
            "output": {
                "message": {
                    "content": "Test message"
                }
            }
        }

        # Call the function with the mock response
        result = server.bedrock_to_chatgpt(mock_response)

        self.assertIn("id", result)
        self.assertIn("object", result)
        self.assertIn("created", result)
        self.assertIsInstance(result["created"], int)
        self.assertIn("model", result)
        self.assertIn("system_fingerprint", result)
        self.assertIn("choices", result)
        self.assertEqual(result["choices"], mock_response["output"]["message"]["content"])
        self.assertIn("usage", result)
        self.assertEqual(result["usage"]["prompt_tokens"], 9)
        self.assertEqual(result["usage"]["completion_tokens"], 12)
        self.assertEqual(result["usage"]["total_tokens"], 21)

    def test_bedrock_to_chatgpt_empty_input(self):
        # Call the function with an empty dict and expect an exception
        with self.assertRaises(KeyError):
            server.bedrock_to_chatgpt({})
