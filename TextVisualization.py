"""Text visualization to show some basic information during the simulation without chart visualization's overhead.

Filename follows mesa.visualization.modules style.
"""

from mesa.visualization.modules import TextElement


class TextModule(TextElement):
    """Basic text module implementation because Mesa's TextElement does not have rendering functionality.
    """

    def __init__(self, model_var_name, visible_name=None):
        self.model_var_name = model_var_name
        if visible_name is None:
            self.template = self.model_var_name + ": {}"
        else:
            self.template = visible_name + ": {}"

    def render(self, model):
        try:
            val = getattr(model, self.model_var_name)
        except:
            val = 0
        return self.template.format(val)
