
class Abstracted:
    """
    heartless.abstracted - abstracted data for use with anything really.
    """
    def __init__(self, **kwargs):
        self.fields = dict()
        for k, v in kwargs.items():
            self.fields[k] = v
        
