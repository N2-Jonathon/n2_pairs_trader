# ***v0.1.0*** *(stable & unit tested)*

!!! todo
    - [ ] Make sure limit orders `price='@best'` is working properly, which fetches the order book for the best asks/bids, then creates a limit order at the current best price (For it to be real-time, it needs to be done via websocket which is only part of the ccxt pro apparently which is going to become free later this year. I can also however implement that myself. For now, I've managed to get the order book from the REST API, but so far I haven't been able to get real-time data from that
        - [ ] [REST API] fetch best bids/asks? (if it's possible)
        - [ ] Implement Websockets connection & fetch best 5 bids/asks as written in KuCoin's documentation
    - [ ] Ensure every method has debug status prints for when debug_mode is enabled
    - [ ] Ensure all queries are within the rate limits as they vary for different API endpoints
    - [ ] Log the status and save into a file
    - [ ] Try different configurations and check the logs for any errors/exceptions, then fix them
    - [ ] Write unit test cases 
    - [ ] Do any debugging required for the unit tests to all pass
    - [ ] Write CLI setup wizard which guides the user through setting up a configuration/strategy (maybe also a password)
    - [ ] Add email notifications
    - [ ] Release **Stable v0.1.0**

    - [ ] Create Sequence Diagram for the entire program execution (example below)

        <img src='https://www.planttext.com/api/plantuml/png/FOyn2iCm34LtdK9upmKwb40AfKCdDsHMOk4Q4Zkrd26thrqddSJ_3-cXLXB5j2qpG79fPbHF5Y7BWWrg_cpi9yQR8njfKG0qfH2n5uumXiqRYZkgWKUyzm-596N257oAOKQbts5TdRVOPSaFwmxOPzEEWpEM4nXAD9BmaGMW7CVcMYxX1Ly1Jn6K9WFTrVxGGCwvhVkLL0KSrHzAfQSIe6LlykzV' width=400>