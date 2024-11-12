import argparse
from lib.logger import logger
from lib.assistant import Assistant


def main(args):
    """Main function"""
    if args.action == "create":
        assistant = Assistant(name=args.name, instructions=args.instructions, plugins=args.plugins, files=args.files, code_interpreter=args.code_interpreter)
    if args.action == "update":
        assistant = Assistant(name=args.name, instructions=args.instructions, plugins=args.plugins, files=args.files, code_interpreter=args.code_interpreter)
    elif args.action == "delete":
        try:
            assistant = Assistant(name=args.name)
        except ValueError:
            logger.warning("Assistant not found.")
            return
        assistant.delete()
    elif args.action == "list":
        assistant = Assistant(None)
        logger.info(assistant.list())
    elif args.action == "chat":
        assistant = Assistant(name=args.name, load=args.load)
        message = None
        logger.warning("Type 'exit' to end the conversation.")
        try:
            while message != "exit":
                message = input("You: ")
                if message == "exit":
                    break
                assistant.message(message)
                response = assistant.get_reply()
                if not response:
                    break
                logger.info(f"Assistant: {response.data[0].content[0].text.value}")
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interact with GPT Assistants.")
    parser.add_argument("action", type=str, help="Action to perform [create, update, delete, list, chat]")
    parser.add_argument("--name", type=str, help="Assistant name")
    parser.add_argument("--instructions", type=str, help="Assistant instructions")
    parser.add_argument("--load", action="store_true", default=False, help="Load existing thread")
    parser.add_argument("--plugins", type=str, nargs="+", help="List of plugins to enable")
    parser.add_argument("--files", type=str, nargs="+", help="List of files to store in the assistant's database")
    parser.add_argument("--code-interpreter", action="store_true", default=False, help="Enable code interpreter for the assistant")
    args = parser.parse_args()
    main(args)
