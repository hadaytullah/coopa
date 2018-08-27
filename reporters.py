"""Model and agent reporters for Mesa's data collector.
"""

__all__ = ['compute_gini',
           'compute_dropped_trashes',
           'compute_average_battery_power',
           'compute_max_battery_power',
           'compute_min_battery_power'
           ]


def compute_gini(model):
    agent_resources = [agent.trash_count for agent in model.schedule.agents]
    x = sorted(agent_resources)
    N = model.num_agents
    if sum(x) > 0:
        B = sum(xi * (N-i) for i, xi in enumerate(x)) / (N*sum(x))
        return 1 + (1/N) - 2*B
    else:
        return 0


def compute_dropped_trashes(model):
    dropped_trashes = [trashcan.trash_count for trashcan in model.trashcans]
    return sum(dropped_trashes)


def compute_average_battery_power(model):
    bps = [agent.battery.charge for agent in model.schedule.agents if hasattr(agent, 'battery')]
    return sum(bps) / len(bps)


def compute_max_battery_power(model):
    bps = [agent.battery.charge for agent in model.schedule.agents if hasattr(agent, 'battery')]
    return max(bps)


def compute_min_battery_power(model):
    bps = [agent.battery.charge for agent in model.schedule.agents if hasattr(agent, 'battery')]
    return min(bps)