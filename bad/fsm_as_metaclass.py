

# class Test(type):
#     """222222222222222222222"""
#     def __new__(
#         cls,
#         name: str,
#         parents: Any,
#         attrs: Any,
#     ):
#         """help me 111111111"""
#         # attrs["something"]: List[str] = ["asdf", "fdsa"]
#         cls = super().__new__(cls, name, parents, attrs)
#         cls.some_method = classmethod(some_method)
#         # return type.__new__(cls, name, parents, attrs)
#         return cls

# def some_method():
#     pass

# class NewClass(metaclass=Test):
#     pass

# item = NewClass()
# print(item.something)
# class FSM(type):
#     """Meta class to create pseudo-FSM classes
#     This FSM implementation used only to create representation
#     methods for various objects (to display in pyrogram chats)
#     depending on states and check state change rules.
#     This FSM not store any state itself to avoid sync issues
#     """
#     def __new__(
#         cls,
#         name: str,
#         parents: Any,
#         attrs: Any,
#         states: IntEnum,
#         representation_methods: List[str],
#     ):
#         """Create FSM class to support specific objects
#         states: enum of possible class states
#         representation_methods: representations in which fsm object can be rendered.
#             for example, here can be "short", "long" and "edit" representations
#             to render item in different ways depending on it's state
#         """
#         for representation in representation_methods:
#             attrs[f"handle_{representation}"] = cls.create_representation_state_handler(
#                 representation
#             )
#             for state in states.__members__:
#                 method_name = f"{state}_{representation}"
#                 if method_name not in attrs:
#                     if f"default_{representation}" in attrs:
#                         attrs[method_name] = cls.default_method(f"default_{representation}")
#                     else:
#                         raise Exception(
#                             f"No {state}_{representation} found, No default for this representation (default_{representation}) setted.\nConsider adding {state}_{representation} or default_{representation} methods." 
#                         )
#                         # attrs[method_name] = cls.default_representation(state)

#         if "move_rule" not in attrs and "move" not in attrs:
#             raise Exception(
#                 "No move rules setted. Add move_rule as property or move as method"
#             )
#         if "move" not in attrs:
#             attrs["move"] = cls.create_move_method(states)
#         return type.__new__(cls, name, parents, attrs)

#     @staticmethod
#     def create_representation_state_handler(
#         representation: str,
#     ):
#         """create methods for provided representation
#         that will resolved based on provided state
#         If no state specific representation setted, default
#         one will be used
#         """
#         def handle_representation(self, state: str, *args, **kwargs):
#             """asdfasf>>>>>>>>>>>>"""
#             func = getattr(self, f"{state}_{representation}")
#             if func:
#                 return func(*args, **kwargs)
#             return getattr(self, f"default_{representation}")(*args, **kwargs)
#         return handle_representation

#     @staticmethod
#     def default_method(representation_name: str):
#         """create default method for representation
#         This method will be used if no state methods setted
#         """
#         def handle_default_representation(self, *args, **kwargs):
#             """docstring"""
#             return getattr(self, representation_name)(*args, **kwargs)
#         return handle_default_representation

#     @staticmethod
#     def create_move_method(states: IntEnum):
#         """create "move_possible" method.
#         This method will try to check is it possible to
#         move from one state to another.
#         """
#         def move_possible(self, move_to_state: str, current_state: str):
#             """check is state move is possible at all"""
#             if not move_to_state in states.__members__:
#                 raise Exception("No such state defined")
#             if move_to_state in self.move_rule[current_state]:
#                 return True
#             return False
#         return move_possible


# class AbstractFSM(ABC):
#     pass

