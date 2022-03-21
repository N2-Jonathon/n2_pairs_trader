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
DEBUG_output = ''
output = ''
exchanges = {
    "requiredCredentials provided": [],
    "requiredCredentials not provided": []

}

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

            dict_start = describe_method.find('describe(), {') + 12
            dict_end = describe_method.rfind('}') + 1
            describe_method_dict = describe_method[dict_start:dict_end]
            status = "Found describe method return contents"

            _rateLimit_idx = describe_method_dict.find("'rateLimit': ") + 13
            _rateLimit = describe_method_dict[_rateLimit_idx:describe_method_dict.find(',\n', _rateLimit_idx)]
            status = f"Found at index: {_rateLimit_idx}\n'rateLimit': {_rateLimit}"

            _has_idx = describe_method_dict.find("'has': ") + 7
            _has = describe_method_dict[_has_idx:describe_method_dict.find('}', _has_idx) + 1]
            status = f"Found at index: {_has_idx}\n'has': {_has}"

            if "'requiredCredentials': " not in describe_method_dict:
                has_requiredCredentials = False
                exchanges["requiredCredentials not provided"].append(exchange_id)
                status = ValueError(f"{exchange_id} does not have requiredCredentials specified.")
                DEBUG_output += ("<<<<! " + str(status) + " !>>>>\n")

                new_output = (f'\n"{exchange_id.upper()}": ' + "{\n"
                              f"""
                                  "requiredCredentials": False,
                                  "rateLimit": {_rateLimit},
                                  "has": {_has}
                              """
                              "\n},\n")
                output += new_output
                DEBUG_output += new_output
            else:
                has_requiredCredentials = True
                exchanges["requiredCredentials provided"].append(exchange_id)
                _requiredCredentials_idx = describe_method_dict.find("'requiredCredentials': ", _has_idx) + 22
                _requiredCredentials = describe_method_dict[_requiredCredentials_idx:describe_method_dict.find('}',
                                                                                                               _requiredCredentials_idx) + 1]

                new_output = (f'\n"{exchange_id.upper()}": ' + "{\n"
                              f"""
                                  "requiredCredentials": {_requiredCredentials},
                                  "rateLimit": {_rateLimit},
                                  "has": {_has}
                               """
                              "\n},\n")

                output += new_output
                DEBUG_output += new_output

            pr_output = f"[{f[0]}/{len(abs_paths)}] Added {exchange_id}.\n"
            print(pr_output)
        finally:
            pass

output = output.replace('\n        ', '\n')
output = output.replace('                      "', '    "')
output = output.replace("    '", "        '")
output = output.replace('    },', '        },')
output = output.replace("'has': {\n            'CORS': None,", '')





DEBUG_output = DEBUG_output.replace('\n        ', '\n')
DEBUG_output = DEBUG_output.replace('                      "', '    "')
DEBUG_output = DEBUG_output.replace("    '", "        '")
DEBUG_output = DEBUG_output.replace('    },', '        },')
DEBUG_output = DEBUG_output.replace("'has': {\n            'CORS': None,", '')




output = (f'{len(exchanges["requiredCredentials provided"])} exchanges with requiredCredentials:\n'
          f'{exchanges["requiredCredentials provided"]}\n\n'
          f'{len(exchanges["requiredCredentials not provided"])} exchanges with unknown requiredCredentials:\n'
          f'{exchanges["requiredCredentials not provided"]}\n\n'
          "\n----------------------\n\n"
          "EXCHANGES =  {" + output + "}")

output_file = open('ccxt_scraper_output.py', 'w')
output_file.write(output)
output_file.close()

DEBUG_output_file = open('ccxt_scraper_DEBUG_output.txt', 'w')
DEBUG_output_file.write(DEBUG_output)
DEBUG_output_file.close()

pass
