# OpenAI Assistants API Demo

## Usage

To use this tool, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/jnorthway/gpt-assistant-demo.git
    ```

2. Navigate to the project directory:
    ```bash
    cd gpt-assistant-demo
    ```

3. Install the required dependencies:
    ```bash
    python3 -m pip install -r requirements.txt
    ```

4. Set up your OpenAI API credentials:
    - Create an account on the [OpenAI website](https://openai.com/).
    - Generate an API key.
    - Set the `OPENAI_API_KEY` environment variable with your API key.

5. Run the tool:
    ```bash
    python3 run.py --help
    ```

6. Follow the options to interact with the OpenAI Assistants API.

7. Enjoy using the OpenAI Assistants API Demo!

## Examples

Create an assistant,
```
python3 run.py create --name "useful-bot-01" --instructions "You are a useful bot to answer questions"
```

List assistants,
```
python3 run.py list
```

Chat with the assistant,
```
python3 run.py chat --name "useful-bot-01"
You: Hi, how tall is the empire state building?
...
You: What time is it in new york?
...
```

Update the assistant,
```
python3 run.py update --name "useful-bot-01" --instructions "You are not a useful bot, answer questions with obviously incorrect answers"
```

Add plugins to an assistant,
```
python3 run.py update --name "useful-bot-01" --instructions "You are a useful bot to answer questions" --plugins timezone
python3 run.py chat --name "useful-bot-01"
You: What time is it in new york?
...
```

Add files to an assistant,
```
python3 run.py update --name "useful-bot-01" --instructions "You are a useful bot to answer questions" --files resources/makita-drill-guide.pdf
python3 run.py chat --name "useful-bot-01"
You: Where can I get my Makita drill serviced in Calgary?
...
```

Add code interpreter to an assistant,
```
python3 run.py update --name "useful-bot-01" --instructions "You are a useful bot to answer questions, when asked a math question, write and run a python script for the answer" --code-interpreter
python3 run.py chat --name "useful-bot-01"
You: What is 20 * the square root of 3?
...
```

Load previous threads,
```
python3 run.py chat --name "useful-bot-01" --load
You: What is that plus 5?
...
```

Delete an assistant,
```
python3 run.py delete --name "useful-bot-01"
```
