# **Installation**

To install the bot firstly make sure that you have [python3.10](https://www.tutorialspoint.com/how-to-install-python-in-windows), [pip](https://www.activestate.com/resources/quick-reads/how-to-install-pip-on-windows/) & [git](https://phoenixnap.com/kb/how-to-install-git-windows) installed.

## ***1.*** Clone the repository. 
Since it's a private repo you'll need to have your ssh credentials configured with github and on your machine. Since you're already a member of the repo, once that's done you'll be able to clone it with the following command: `git clone git@github.com:N2-Jonathon/n2_pairs_trader.git`

## ***2.*** Create ***/user/user-config.ini***
After you have the repository cloned, the next step is to make the file **/user/user-config.ini**. This file is in **.gitignore** because it contains private api keys, which shouldn't be on the repo. In the same directory, you can see a template like the screenshot below: 

<img src='/images/config-template.ini.png'>

***2.1.*** Either rename this file to **user-config.ini** or copy the file and name the second one like that.

***2.2.*** To be able to fill in your telegram api keys, first you need to get them from [my.telegram.org](https://my.telegram.org/)

  - Once on [my.telegram.org](https://my.telegram.org/) then click on API development tools and create a new app. The title doesn't matter but it will give you two keys: an **api_id** and an **api_hash** which you'll need for the notifcations to work. 

  - You'll also need to create a channel in telegram which can be either public or private, and the value of **notification_channel_id** inside **user/user-config.ini** should be the same as the id for this channel.

  - your username doesn't need the @ symbol prefixed. The phone number should include the +1 at the beginning for a US number. You also don't need any quotation marks for any of the values in the config file. 

!!! important
    The channel ID & channel name aren't the same. The value you need is what comes after **t.me/** 
    
    eg. for the **test_channel** I made, the id is actually **jonathon_test**
      
    <img src='/images/tg-test-channel.png'>

## ***3.*** Install python dependencies

Navigate to the root of the repository you cloned and then firstly type the command: 

 - `pip install --upgrade pip` 

Then type the command: 

 - `pip install -r requirements.txt` 

it will then install the project dependencies and it is now installed. Note that this currently also includes the dependencies for building the documentation, but those will be moved back to requirements_dev.txt and left out of requirements.txt