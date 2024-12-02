from typing import Dict, Optional, Callable, Literal
from pydantic import BaseModel

from datetime import datetime


possible_states: set = {  # for validation
    'creating_await_for_username',
    'creating_await_for_login',
    'creating_await_for_login',
    'created_await_for_username',
    'created_await_for_login',
    'task_await_for_edit',
    'new_task_await_for_title',
    'new_task_await_for_description',
}

StatesLiteral = Literal[*possible_states]


class UserResponseWrapper(BaseModel):
    """
    Manages subscription of functions.
    Function can be subscribed to any user state.
    Then, when input detected, function matched
    with current user state can be called
    """
    wrapped_functions: Optional[Dict[str, Callable]] = dict()

    def wrap_function(self, function: Callable, state: StatesLiteral):
        assert state in possible_states
        self.wrapped_functions[state] = function

    def find(self, state: StatesLiteral):
        assert state in possible_states
        assert state in self.wrapped_functions.keys()
        return self.wrapped_functions[state]

    def subscribe(self, state: StatesLiteral):
        def decorator(func):
            self.wrap_function(func, state)

            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator


class UserStates(BaseModel):
    """
    Manages user states and connection between
    wrapped functions and user statets.

    When input detected, call matched wrapped functions
    on current user state.
    """
    states: Optional[Dict[int, str]] = dict()
    wrapped_functions: UserResponseWrapper
    input_handled_timestamps: Optional[Dict[int, datetime]] = dict()
    # trace: Optional[Dict[int, Tuple[datetime, str]]] = dict()

    def clean_state(self, user_id: int):
        if self.states.get(user_id):
            self.states.pop(user_id)

    def set_state(self, user_id: int, state: StatesLiteral):
        assert state.split(":")[0] in possible_states
        self.states[user_id] = state

    async def handle_action(self, user_id: int, *args, **kwargs):
        state = self.states.get(user_id)
        if not state:
            raise UserStateNotExsists
        state = state.split(":")[0]
        result = await self.wrapped_functions.find(
            state
        )(*args, **kwargs)
        return result

    def any_state_setted(self, user_id: int):
        return bool(self.get_state(user_id))

    def get_state(self, user_id: int):
        return self.states.get(user_id)


class UserStateNotExsists(Exception):
    pass


user_response_wrapper = UserResponseWrapper()
user_states = UserStates(wrapped_functions=user_response_wrapper)
response_wrapper = user_response_wrapper

