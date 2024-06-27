import argparse
from lib.logger import logger
from lib.assistant import Assistant


def main(args):
    """Main function"""
    if args.action == "create":
        assistant = Assistant(name=args.name, instructions=args.instructions, plugins=args.plugins, files=args.files)
    if args.action == "update":
        assistant = Assistant(name=args.name, instructions=args.instructions, plugins=args.plugins, files=args.files)
    elif args.action == "delete":
        assistant = Assistant(name=args.name)
        assistant.delete()
    elif args.action == "list":
        assistant = Assistant(None)
        logger.info(assistant.list())
    elif args.action == "chat":
        assistant = Assistant(name=args.name, load=args.load)
        message = None
        logger.warning("Type 'exit' to end the conversation.")
        while message != "exit":
            message = input("You: ")
            if message == "exit":
                break
            assistant.message(message)
            response = assistant.get_reply()
            if not response:
                break
            logger.info(f"Assistant: {response.data[0].content[0].text.value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interact with GPT Assistants.")
    parser.add_argument("action", type=str, help="Action to perform")
    parser.add_argument("--name", type=str, help="Assistant name")
    parser.add_argument("--instructions", type=str, help="Assistant instructions")
    parser.add_argument("--load", action="store_true", default=False, help="Load existing thread")
    parser.add_argument("--plugins", type=str, nargs="+", help="List of plugins to enable")
    parser.add_argument("--files", type=str, nargs="+", help="List of files to store in the assistant's database")
    args = parser.parse_args()
    main(args)