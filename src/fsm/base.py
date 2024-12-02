from typing import Optional, Dict, List


class FSM():
    """Base class for FSM
    This class Is used to prepare representations
    of objects based on object's state and desired
    way of representing.

    For example, there can be "general" and "edit"
    representations, that, respectfully, generates
    look for object in common way, like show some info
    and in editing way, showing fields for updating

    So, FSM gives a way to define "default" representation for
    each representation way, like default_general or default_edit
    and re-define needed state-specific places. For example,
    object in state "paused" should not have any edit representation,
    so in FSM you can define paused_edit func to return nothing.
    Or you need send specifc set of fields on "work_appeal" state,
    so you can do this in func "work_appeal_edit"

    In API level it's expected from you to crate function like
    handle_{representation}, for example, handle_edit
    You can define needed input for representation and then
    you need to execute "handle_representation" method
    to automaticly route your output based on representation/state
    provided.
    """
    default_move_rules = {}

    def __init__(self, move_rules: Optional[Dict[str, List[str]]] = None):
        if move_rules:
            self.move_rules = move_rules
        else:
            self.move_rules = self.default_move_rules

    def can_move(self, state_from: str, state_to: str):
        return state_to in self.move_rules[state_from]

    async def handle_representation(
        self,
        representation: str,
        state: str,
        *args,
        **kwargs,
    ):
        """Try to call {state}_{representation} if possible;
        call default_{representation} if not"""
        handler = getattr(self, f"{state}_{representation}", None)
        if handler:
            return await handler(*args, state=state, **kwargs)
        default_handler = getattr(self, f"default_{representation}", None)
        if not default_handler:
            raise Exception(
                f"No {state}_{representation} or default_{representation} setted for fsm."
            )
        return await default_handler(state, *args, **kwargs)


