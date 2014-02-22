from flask.ext.script import Command, Option, Manager
from flask import current_app

manager = Manager()


class Setup(Command):
    """
    """
    
    @property
    def app(self):
        return current_app
    
    def run(self):
        pass


manager.add_command("setup", Setup())
