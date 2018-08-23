# This might expand into a huge thing
class Cooperation:
    def __init__(self, with_agent):
        self._with_agent = with_agent
        self._trust = 0 #0 to 10, 10 being the highest
        self._messages = []

    @property
    def trust (self):
        return self._trust

    def set_trust(self, trust_level):
        self._trust = trust_level

    def add_message(self, message):
        self._messages.append(message)

