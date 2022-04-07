# Changing the configuration

To change the configuration values, currently the only way to do it is to edit the values in user-config.ini

For example, the current default base and quote pairs are **ETH/USDT** & **BTC/USDT** respectively, meaning that the artificial pair is **ETHUSDT/BTCUSDT**

The coin which has to be borrowed is worked out automatically depending on whether you are opening a long or short position. 

!!! note 
    I will move this to the developer guide later. As a user you don't need to care about this but I'm writing it now because it will still have to be explained in the developer guide.
    
    Inside the code, the artificial pair or 'synth pair' is read from the configuration file and then stored as a tuple  called 'synth_pair_tuple' which basically means a group of values in a specific order. 

    The indexes of this tuple are as follows:

    **[0]** Full artificial symbol ie. **ETHUSDT/BTCUSDT**
    **[1]** Base currency of base pair ie. **ETH**
    **[2]** Quote currency of base pair ie. **USDT**
    **[3]** Base currency of quote pair ie. **BTC**
    **[4]** Quote currency of quote pair ie. **USDT**

    There's currently no reason why **[2]** & **[4]** would be different but it's technically possible to have two pairs with different denominators although that's untested.  