#! /usr/bin/env python
import sys
from flask.ext.script import Manager

# import app
from vircu.app import app

manager = Manager(app)

from vircu.tasks.devel import manager as devel_manager
manager.add_command("devel", devel_manager)

from vircu.tasks.ticker import manager as devel_manager
manager.add_command("ticker", devel_manager)

from vircu.tasks.aggregate import manager as aggregate_manager
manager.add_command("aggregate", aggregate_manager)

from vircu.tasks.cron import manager as cron_manager
manager.add_command("cron", cron_manager)

from vircu.tasks.build import manager as build_manager
manager.add_command("build", build_manager)

if __name__ == "__main__":
    manager.run()