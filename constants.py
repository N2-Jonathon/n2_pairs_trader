"""
This file is for global constants to be declared
I'm doing this because in different modules, the
relative path to `user-config.ini` gets messed
up by having different `sys.path`, so I'm just
going to declare it once as a global constant
in the top level of the project.

There may be other constants I add to here

Also, maybe it's possible to have this inside
the core module and use a relative filepath
but still only set this value once as a constant,
instead of pulling out my hair figuring out how
to import this file from different relative
locations.
"""
import os


USER_CONFIG_FILEPATH = f"{os.getcwd()}/user/user-config.ini"

print(USER_CONFIG_FILEPATH)
