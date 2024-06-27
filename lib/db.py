"""Simple database library."""
import os


def get_default_db_path():
    """Return the path to the default db text file."""
    return os.path.join("data", "db.txt")


class DB:
    """Simple database class using a text file to store data."""

    def __init__(self, path=None):
        if path:
            self.path = path
        else:
            self.path = get_default_db_path()
        self.data = self.load()
    
    def load(self):
        """Load data from the db text file."""
        data = {}
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                for line in f:
                    key, value = line.strip().split(":")
                    data[key] = value
        return data
    
    def save(self):
        """Save data to the db text file."""
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as f:
            for key, value in self.data.items():
                if value is not None:
                    f.write(f"{key}:{value}\n")
    
    def delete(self):
        """Delete the db text file."""
        os.remove(self.path)
        self.data = {}
