from text.base import FromTomlFile


class SystemMessages(FromTomlFile):
    start_command_message: str
    unhandled_input: str
    rules: str


class SystemKeyboard(FromTomlFile):
    user_info: str
    new_task: str
    all_tasks: str
    rules: str


system_messages = SystemMessages('resources/system.toml')
system_keyboard = SystemKeyboard('resources/system.toml')
