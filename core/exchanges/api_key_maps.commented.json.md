
[NOTE] * This is not valid json, nor is it meant to be complete JavaScript,
        but it mirrors the api_key_maps.json. Maybe I'll replace this with
        a markdown document. For now this will be an empty data structure
        containing the templates for api required credentials. ccxt has
        already implemented a way to get this info but you have to first
        import and then initialize an exchange to use a method called
        `.fetchRequredCredentials`.
        * Instead of importing and querying through an exchange instance,
        I will reference `api_key_maps.json` to get the required credentials
        of an exchange since it's not the same for all of them.
        - Sometimes there are 2, 3 or more keys with different names for some
        exchanges, and this file is to make a reference for that to know which
        keys to look for in a config.ini file.
        - I'll just take the dictionary of the possible required credentials
        from ccxt.exchange, then make my own dictionary which maps `bool`
        values to each credential type for each exchange.
        * I first tried doing this inside of the classes with the python built-in
        `importlib.importmodule()` but I had a lot of issues trying to get that
        to work, so that's why I'm taking this approach instead.
          - I will still use `importlib.importmodule()` but only in a script
            which I'll run once to generate this file.
        TODO: - [ ] Make a script to fetch the required credentials using
         ccxt for all exchanges, and write them to api_key_maps.json
         I should only need to do this once, or whenever new exchanges are
         added to ccxt. If I extend any of the exchanges the same way as
         kucoin in `core.exchanges.kucoin_extended`, then I will also make
         a reference to that in this file to know whether to use the default
         ccxt class, or a custom local class which inherits the ccxt class