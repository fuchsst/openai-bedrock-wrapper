# LLM Wrapper API

This project simulates the ChatGPT-4 API by translating requests to AWS Bedrock Claude models and running it locally.

## Setup

1. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. Install dependencies:
    ```bash
    pip install -r api/requirements.txt
    ```

3. Set up environment variables in a `.env` file based on the `config/dev.env` file.

4. Update the `config.yaml` file with the appropriate mappings.

5. Run the server:
    ```bash
    ./run.sh
    ```

## Usage

Send POST requests to `http://127.0.0.1:5000/v1/chat/completions` with a JSON body containing the `model`, `messages`, `max_tokens`, and `temperature` fields.
