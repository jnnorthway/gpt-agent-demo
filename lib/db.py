"""Simple database library."""
import os


def get_default_db_file():
    """Return the filename for the default db text file."""
    return "db.txt"


class DB:
    """Simple database class using a text file to store data."""

    def __init__(self, path=None):
        self._path = None
        self.path = path
        self.data = self.load()
        
    @property
    def path(self):
        """Get the path to the db text file."""
        return self._path

    @path.setter
    def path(self, value=None):
        """Set the path to the db text file."""
        if not value:
            value = get_default_db_file()
        self._path = os.path.join("data", value)
    
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
