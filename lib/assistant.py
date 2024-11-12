import os
import json
import time
import openai
import importlib
from lib.logger import logger
from lib.db import DB


class Assistant:
    """GPT Assistant class."""

    def __init__(self, name=None, instructions=None, load=False, plugins=[], files=[], code_interpreter=False):
        self.client = openai.OpenAI(default_headers={"OpenAI-Beta": "assistants=v2"})
        self.config = {
            "model": "gpt-4o",
        }
        self.tools = []
        self._name = None
        self._id = None
        self.assistant = None
        if name is None:
            return
        self.name = name
        self.db = DB(f"assistant_{self.name}.txt")
        self.init_assistant(instructions, plugins, files, code_interpreter)
        self.init_thread(load)
    
    @property
    def name(self):
        """Get the assistant's name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the assistant's name."""
        if " " in value:
            value = value.replace(" ", "-")
        self._name = value
    
    @property
    def id(self):
        """Get the assistant's ID."""
        if not self._id:
            self._id = self.db.data.get("id")
        return self._id
    
    @id.setter
    def id(self, value):
        """Set the assistant's ID."""
        self._id = value
        self.db.data["id"] = value
        self.db.save()
    
    def init_assistant(self, instructions, plugins, files, code_interpreter):
        """Initialize assistant."""
        if self.id:
            self.assistant = self.load()
        else:
            self.assistant = self.load_from_name()
        if not self.assistant:
            self.assistant = self.create(instructions)
        elif instructions:
            self.assistant = self.client.beta.assistants.update(
                assistant_id=self.id,
                instructions=instructions,
            )
        if plugins:
            self.load_plugins(plugins)
        if files:
            self.load_files(files)
        if code_interpreter:
            self.tools.append({"type": "code_interpreter"})
        self.add_tools()

    def init_thread(self, load):
        """Initialize thread."""
        if load:
            self.load_thread()
        else:
            self.create_thread()

    def load_plugins(self, plugins):
        """Load plugins."""
        for plugin in plugins:
            try:
                module = importlib.import_module(f"lib.plugins.{plugin}")
                self.tools.append(getattr(module, "get_plugin")())
            except ImportError as e:
                logger.error(f"Failed to load plugin: {plugin}")
                logger.error(e)

    def load_files(self, files=[]):
        """Load plugins."""
        self.add_files(files)
        self.tools.append({"type": "file_search"})
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.id,
            tool_resources={"file_search": {"vector_store_ids": [self.db.data["storage_id"]]}},
        )
    
    def add_tools(self):
        """Add tools to the assistant."""
        if self.tools:
            self.assistant = self.client.beta.assistants.update(
                assistant_id=self.id,
                tools=self.tools,
            )

    def create(self, instructions):
        """Create a new assistant."""
        if instructions is None:
            raise ValueError("Instructions are required to create a new assistant.")
        assistant = self.client.beta.assistants.create(
            name=self.name,
            model=self.config["model"],
            instructions=instructions,
        )
        self.id = assistant.id
        self.db.data["id"] = self.id
        self.db.save()
        return assistant
    
    def load(self):
        """Load an existing assistant."""
        assistant = self.client.beta.assistants.retrieve(self.id)
        self.instructions = assistant.instructions
        return assistant
    
    def load_from_name(self):
        """Load an existing assistant by name."""
        for assistant in self.list():
            if assistant.name == self.name:
                self.id = assistant.id
                self.instructions = assistant.instructions
                self.db.data["id"] = self.id
                self.db.save()
                return assistant
        return None

    def delete(self):
        """Delete the assistant."""
        self.client.beta.assistants.delete(self.id)
        self.delete_thread()
        self.db.delete()

    def list(self):
        """List all assistants."""
        assistants = self.client.beta.assistants.list()
        return assistants

    """Thread methods."""

    def create_thread(self):
        """Create a new thread."""
        self.delete_thread()
        thread = self.client.beta.threads.create()
        self.db.data["thread_id"] = thread.id
        self.db.save()
        return thread

    def load_thread(self):
        """Load an existing thread."""
        if self.db.data.get("thread_id"):
            thread = self.client.beta.threads.retrieve(self.db.data["thread_id"])
            return thread
        return None
    
    def delete_thread(self):
        """Delete the thread."""
        if self.db.data.get("thread_id"):
            self.client.beta.threads.delete(self.db.data["thread_id"])
            self.db.data["thread_id"] = None
            self.db.save()
    
    def message(self, content, role="user"):
        """Add a message to the thread."""
        if self.db.data.get("thread_id"):
            self.client.beta.threads.messages.create(self.db.data["thread_id"], role=role, content=content)

    def create_run(self):
        """Run the assistant on a message."""
        if self.db.data.get("thread_id"):
            run = self.client.beta.threads.runs.create(thread_id=self.db.data["thread_id"], assistant_id=self.id)
            self.db.data["run_id"] = run.id
            self.db.save()
            return run
        return None

    @property
    def messages(self):
        """Get all messages in the thread."""
        if self.db.data.get("thread_id"):
            return self.client.beta.threads.messages.list(self.db.data["thread_id"])

    @property
    def last_message(self):
        """Get last message in the thread."""
        if self.db.data.get("thread_id"):
            return self.client.beta.threads.messages.list(self.db.data["thread_id"], limit=1)

    def reload_run(self):
        """Reload run."""
        if self.db.data.get("thread_id") and self.db.data.get("run_id"):
            return self.client.beta.threads.runs.retrieve(thread_id=self.db.data["thread_id"], run_id=self.db.data["run_id"])
        return None

    def handle_calls(self, run, calls):
        """Handle tool calls."""
        tool_outputs = []
        for call in calls:
            tool, function = call.function.name.split("-")
            kwargs = json.loads(call.function.arguments)
            module = importlib.import_module(f"lib.plugins.{tool}")
            ret = getattr(module, function)(**kwargs)
            tool_outputs.append({
                "tool_call_id": call.id,
                "output": ret,
            })
        self.client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=self.db.data["thread_id"],
            run_id=run.id,
            tool_outputs=tool_outputs,
        )
        return self.last_message

    def get_reply(self):
        """Get the assistant's reply."""
        run = self.create_run()
        while run.status in ("queued", "in_progress"):
            time.sleep(1)
            run = self.reload_run()
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.db.data["thread_id"],
            run_id=run.id
        )
        logger.debug(f"Run steps: {run_steps}")
        if run.status == "requires_action":
            logger.debug(f"Run requires action: {run.required_action.submit_tool_outputs.tool_calls}")
            return self.handle_calls(run, run.required_action.submit_tool_outputs.tool_calls)
        logger.debug(f"Usage: {run.usage}")
        if run.status != "completed":
            logger.error(f"Run failed: {run}")
            return None
        return self.last_message
    
    """Files Methods."""

    def create_storage(self, name):
        """Create a storage object."""
        storage = self.client.beta.vector_stores.create(name=name)
        self.db.data["storage_id"] = storage.id
        self.db.save()
        return storage

    def add_files(self, file_paths):
        """Add files to the assistant."""
        if not self.db.data.get("storage_id"):
            self.create_storage("assistant_files")
        file_streams = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                continue
            file_streams.append(open(file_path, "rb"))
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.db.data["storage_id"], files=file_streams
        )
        logger.debug(f"File batch status: {file_batch.status}")
        while file_batch.status == "in_progress":
            time.sleep(1)
            logger.debug(f"File batch status: {file_batch.status}")
