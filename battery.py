


class Battery:
    """Simulated battery for the agent.

    Moving and other agent actions consume battery charge, agent must recharge the battery repeatedly.
    """

    def __init__(self, maximum_charge, initial_charge=None):
        self._max_charge = maximum_charge
        if initial_charge is None:
            self._charge = self._max_charge
        else:
            self._charge = initial_charge

        self._scan_radius_coefficient = 1.5
        self._speed_coefficient = 1.0
        self._carrying_coefficient = 0.0

    @property
    def max_charge(self):
        """Battery's maximum charge.
        """
        return self._max_charge

    @property
    def charge(self):
        """Battery's current charge.
        """
        return self._charge

    def recharge(self, amount=10):
        self._charge += amount
        if self._charge > self._max_charge:
            self._charge = self._max_charge

    def consume_charge(self, agent_configuration):
        self._charge -= self.compute_scan_charge(agent_configuration['scan_radius'])
        self._charge -= self.compute_speed_charge(agent_configuration['speed'])
        self._charge -= self.compute_carrying_charge(agent_configuration['trash_count'])

        if self._charge < 0.0:
            self._charge = 0.0

    def compute_scan_charge(self, scan_radius):
        return (scan_radius - 1) ** self._scan_radius_coefficient

    def compute_speed_charge(self, speed):
        return speed ** self._speed_coefficient

    def compute_carrying_charge(self, trash_carried):
        return (trash_carried ** self._carrying_coefficient) - 1




