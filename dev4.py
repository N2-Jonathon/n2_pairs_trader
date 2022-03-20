"""
This is a one-time script I made to populate the constant EXCHANGE_DESCRIPTIONS
inside of core.constants
It scrapes the python files from the ccxt library to get the json-like structure
which is returned from the `describe()` method of each exchange. I did it this
way since calling that method directly means importing and instantiating each 
exchange. I tried that frist using importlib.importmodule(f"ccxt.{exchange_id}")
but I had problems getting that work so I just scraped the python files directly.
It would be a good idea to update this whenever ccxt releases an update.

If this script needs to be run manually again, it shold be placed in the root
directory one level up from the scripts folder, but since I'm not using it for 
now I'm just placing it back in here. 

Trying to do a relative import from the scripts folder instead of the root dir 
could lead to the same issues with relative imports that lead to the idea of 
having these as constants in the first place.
"""

import os
from core.constants import ROOT_DIR
from pprint import pprint
ccxt_dir = f"{ROOT_DIR}/venv/lib/python3.10/site-packages/ccxt"


print(ccxt_dir)
# The path for listing items
path = ccxt_dir

# List of only files
files = [f for f in os.listdir(path) if str(f).endswith('.py')]  # if os.path.isfile(f)


exchange_ids = []
import_paths = []
abs_paths = []
# Loop to print each filename separately
for filename in enumerate(files):
    if filename[1] != '__init__.py':
        try:
            exchange_id = filename[1].split('.')[0]
            exchange_ids.append(exchange_id)
            # import_paths.append(f"ccxt.{exchange_id}")
            abs_paths.append(f"{ccxt_dir}/{filename[1]}")
        finally:
            pass

# pprint(exchange_ids)
# pprint(import_paths)
pprint(abs_paths)

DEBUG_enum_abs_paths = enumerate(abs_paths)
output = ''
for f in enumerate(files):

    if filename[1] != '__init__.py':
        try:
            exchange_id = f[1].split('.')[0]

            path = f"/home/jonathon/Developer/freelance/@N2_Capital/n2_pairs_trader/venv/lib/python3.10/site-packages/ccxt/{f[1]}"

            file = open(path)

            file_string = file.read()
            # pprint(file_string)

            def_describe_idx = file_string.find('def describe(self):')
            def_describe_endline = file_string.find('\n', def_describe_idx)
            # def_describe_line = file_string[def_describe_idx:def_describe_endline]
            first_method_idx = file_string.find('    def ', def_describe_endline)

            describe_method = file_string[def_describe_idx:first_method_idx]

            dict_start = describe_method.find('describe(), {')+12
            dict_end = describe_method.rfind('}')+1

            output += describe_method[dict_start:dict_end]
            output += ',\n'

            pr_output = f"[{f[0]}/{len(abs_paths)}] Added {exchange_id}.\n"
            print(pr_output)
        finally:
            pass

output = output.replace('\n        ', '\n')
output_file = open('output.txt', 'a')
output_file.write(output)
output_file.close()

pass