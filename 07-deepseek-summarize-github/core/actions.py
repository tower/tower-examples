from typing import Any

class Action:
    def __init__(self, actionname: str = None):
        if actionname is not None:
            self.actionname = actionname
        else:
            self.actionname = "UnnamedAction"


    def do(self,*args:Any, **kwargs: Any):
        pass

    # ThisAction(params) or ThisAction.do(params)
    def __call__(self,*args:Any, **kwargs: Any):
        return self.do(*args, **kwargs)
