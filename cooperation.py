import random

# This might expand into a huge thing
class Cooperation:
    def __init__(self, with_agent):
        self.with_agent = with_agent
        self.trust = 0 #0 to 10, 10 being the highest
        self.messages = []

    def set_trust(self, trust_level):
        self.trust = trust_level

    def add_message(self, message):
        self.messages.append(message)

