# ***v0.0.1*** *(Development Release)*

!!! todo
    - [ ] Publish the release on the Github repo
    - [ ] Come back and add some more information here describing how the steps below are implemented including:
        
        - [ ]  a PlantUML class diagram of each of the classes:
            
            - **Config**
                - **PositionManager**
                - **Position**
                - **Notifier**
                -  **StrategyBase**
                    -  **N2SuperTrend**
      
        <img src='https://www.planttext.com/api/plantuml/png/XP1DYy8m48Rlyok6dbQN7FOg7YfwKF2q29v3EzXXavdIfCgY_dTRsog27xUyvCdpJYODqLQnzWuWSdI4l-HiP9LGS1dGuDpP4731TbTP3m1Pbm_a7CiEZu3ulPA8MvPS3w6DU-KSrvhzRGfQg5PV8pWF3sTbK-T9Of-NMWVgptFrlfOXTSAXhz40t5gd9zFSYRdh9hYIWYgELZ9w0lRkJzXrd1TGyfFWsDIbmSHR-K_w2IUjkzJ0xTRUqEqN7bb8IV9czHS0' width=400>

        - [x] An activity diagram depicting the strategy **N2SuperTrend** (Right click the image and open in a new tab to see full-size):

        <img src='https://s3.us-west-2.amazonaws.com/secure.notion-static.com/92e6bdea-d919-4a04-88ec-b422aea8cbf0/n2_kucoin_long_short_activity.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220331%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220331T034407Z&X-Amz-Expires=86400&X-Amz-Signature=84fe129d7fd839927195ed7504ea4afc1ba60daf8a448cce9af02da82e116c04&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22n2_kucoin_long_short_activity.png%22&x-id=GetObject' width=400>



!!! done

    - [x] **1.** Write a script which scrapes the contents of what the `describe()` method returns. This was necessary to avoid having to import every exchange to be able to get this information which I was trying to do before with many issues.

    ---

    - [x] **2.** Fix imports in `core.constants` for the scraped data to not give any errors when saved as a python dict.
        * [x] For now I only need the content of `rateLimit` `requiredCredentials` and `has` which don't have any out of scope variable names like the rest of the errors, so I can ommit the rest for now and focus on getting those two working first, then sort out the imports after.
        * Having every exchange's `requiredCredentials` as a constant helps in the `Config` & `StrategyBase` classes where the exchange isn't yet imported or initialized but I still need to know what those credentials need to be
        * Having every exchange's `has` as a constant will make it very easy to see which exchanges support what, and be able to judge which strategies are suitable for which exchanges. eg. which exchanges already support margin trading and `fetchBorrowRate` etc

    ---

    - [x] **3.** Make a list of all ccxt exchanges which have:
        * [x] margin trading 
        * [x] `fetchBorrowRate`
    * ***NOTE:***
        You can view this info & more by looking at the 'CCXT Insights' section of the docs

    ---

    - [x] **4.** Fully implement each step of Long/Short positions including borrowing.
        - [x] ***[4.1]*** **open_long:**
            - [x] **Step 1:**
            Query exchange to fetch max borrow quantity of borrow_coin.
                - **borrow_coin** will be the base coin of the quote pair
                - e.g. in ETHUSDT/**BTC**USDT it is **BTC**
            - [x] **Step 2:**
            If prompt_borrow is true, print the max borrow amount retrieved in step 1, then prompt the user to either accept the max amount or instead enter an amount.
            - [x] **Step 3:**
            Borrow from the exchange in the desired quantity
            - [x] **Step 4:**
            Sell quote pair using the coins borrowed in step 3.
                - eg. Sell BTC for USDT
            - [x] **Step 5:**
            Buy the base coin of the base pair using the quote coin of the base pair.
                - eg. Buy ETH with USDT
        - [x] ***[4.2]*** **open_short:**
            - [x] Copy & modify steps from open_long (refactor this later)
            - **borrow_coin** will be the base coin of the base pair
                - e.g. in **ETH**USDT/BTCUSDT it is **ETH**
        - [x] ***[4.3]*** **close:**
            - [x] Re-pay loan
            - [x] Sell assets back to stake currency USDT 
            * This will only work properly when event handling is implemented, and when it is, it'll also be very simple to add the notifications

    ---

    - [x] **5.** Implement Telegram Notifications with telethon
        - **Note:** I did this in my last project so I can just copy/paste that 

___

# **Dev Log:**

!!! note
    ***(March 26th, 2022)***
    ***[21:30 CET | 18:30 EDT]***

    To make managing positions dynamic, it needs to have a 'newSignal' event which, when fired will call PositionManager.open(), or PositionManager.close(), so that a signal can come at any time.
    
    - Implementing this will also make notifications much simpler.
    - I've worked briefly with event handling in C# but I have to admit this is making my head spin. I think I have a handle on it (no pun intended), and I've got a jupyter notebook in **dev_scripts/dev_EventHandling.ipynb** where I'm figuring out how to get it to work properly. 
    - Once it works in the notebook, I'll do the same in the real classes and add the notifications. At that point the MVP will be finished and ready to submit. 

    ***(March 25th, 2022)***
    ***[22:34 CET | 19:31 EDT]***

    This is already partially usable. At the very least, you can see it open long or short positions, and now I'm just making it save more metadata which will be used to close each position. Once that works, the telegram bot will just send the contents of either `pm.current_position.status` or `pm.current_position.borrow_info` & `pm.current_position.trade_info`.

    - If you want to test this out, then I'd recommend doing so on [KuCoin's sandbox exchange](https://sandbox.kucoin.com/) which works the same as the normal exchange but without real funds. 
    - Right now the bot is using the sandbox API urls/endpoints, so to try it on the real exchange you'd need to delete lines **34-39** from **core/exchanges/kucoin_extended.py**

    ***(March 24th, 2022)***
    ***[16:31 CET | 11:31 EDT]***

    Now each step in open_long works. So next I will do (almost) the same thing for open_short, then move onto close & send notification.

    ***(March 23rd, 2022)***
    ***[20:21 CET | 17:37 EDT]***

    !!! success
        I thought that after borrowing, I'd be able to use normal trades, but KuCoin's API is different for trading with the regular trading account and the margin account, so I am adding a new method for posting a margin order which you can see [here](/KuCoin_Extended/)
        
        {--Right now I'm--} {++I was++} getting this error as a response from KuCoin:
        ```
        {'code': '200000', 'msg': 'position internal error'}
        ```

        {--I'm working on figuring it out--} {++I figured it out++}, and I've also [posted an issue](https://github.com/ccxt/ccxt/issues/12457) in the ccxt repo. I was calling the API incorrectly, but also it seems a bug on their end didn't give the correct error code. 

    ***(March 23rd, 2022)***
    ***[07:37am CET | 03:37am EDT]***

    So I didn't manage to get it finished on Wednesday since yet again I mis-judged how long it would take. However, I have made loads of progress since then and it's looking quite promising. Getting closer to the finish line, since I already managed to properly extend `ccxt.kucoin` and added 2 new methods to it: `fetchMaxBorrowSize` and `borrow` which work properly. 

    - Actually making trades is simple compared to that, since it's already built in and it won't be difficult to figure out how to get ccxt to do that like it was with the margin-related stuff
    - I've been using KuCoin's sandbox exchange for testing which works the same way as the real one.
    - Once `open_long` works, then I can just copy, paste & tweak it for `open_short`
    - Then I'll add a `close` method which closes the position & repays the loan 
    - If you want to see how it's working, you can open the program in an IDE with a debugger, and just watch `self.status`. I will walk you through that when it's submitted.

    ***(March 21st, 2022)***

    ***[11:08am CET | 06:08am EDT]***

    Like I said last night, I'm trying to get this functional by the end of today. Since our last message, I've managed to get through steps 2 & 3 which is going to help a lot with step 4.

    ***(March 20th, 2022)***

    Hi Nico, this is my first update in a couple of days since I got stuck on a problem which I've just recently (mostly) solved. I will explain that below.

    I've also migrated the **TODO** list to here for now while I'm developing this, but after the first release I will migrate the **TODO** to its own page, and this will be the Index/Home.