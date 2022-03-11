# This is where emails will be sent and/or telegram notifications.

class Notification:

    def __init__(self, position, status, media="email"):
        self.media = media
        self.position = position
        self.status = status
