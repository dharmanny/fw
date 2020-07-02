import importlib

class RobotLibraryIncluder:
    lib = importlib.import_module('__init__', 'SeleniumLibrary')


import robot

robot.run_cli()