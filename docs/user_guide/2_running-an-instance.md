# Running An Instance

From a terminal, simply navigate to the root of the cloned repository and run the command in your terminal/command prompt:
`python __main__.py`

Depending on how your terminal's python path is configured, you may have to write **python3** instead of **python** 

eg. `python3 __main__.py`

- Corrently, it's configured only to work with the values set in user-config.ini
- I will however implement a user-friendly CLI which makes changing the configuration possible even after starting the bot

!!! todo
    - [ ] I'll also make a shell script inside the folder for either running a single instance or multiple instances.
    - When that's done, you'd have to just type in your terminal something like: `./run` or `./run-multiple`