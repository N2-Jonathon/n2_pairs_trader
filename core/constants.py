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

USER_CONFIG_PATH = None
"""
`USER_CONFIG_FILEPATH` has to be assigned in __main__, 
otherwise if I use `f"{os.getcwd()}/user/user-config.ini"`
inside this file, then wherever I import it will mess up
the relative path. So, here it's set to `None`

f"{os.getcwd()}/user/user-config.ini" will only work 
when the current working directory is the project root.
"""



print(USER_CONFIG_PATH)
