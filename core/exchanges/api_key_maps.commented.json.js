
// [NOTE] * This is not valid json, nor is it meant to be complete JavaScript,
//        but it mirrors the api_key_maps.json. Maybe I'll replace this with
//        a markdown document. For now this will be an empty data structure
//        containing the templates for api required credentials. ccxt has
//        already implemented a way to get this info but you have to first
//        import and then initialize an exchange to use a method called
//        `.fetchRequredCredentials`.
//        * Instead of importing, I will reference `api_key_maps.json` to get
//        the required credentials of an exchange since it's not the same for
//        all of them. Sometimes there are 2 or 3 keys with different names, and
//        this file is to make a reference of that. I'll just take the dictionary
//        of the possible required credentials from ccxt.exchange, then make my
//        own dictionary which maps `bool` values to each credential type for
//        each exchange.
//        TODO: - [ ] Make a script to fetch the required credentials using
//         ccxt for all exchanges, and write them to api_key_maps.json