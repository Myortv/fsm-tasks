from text.base import FromTomlFile


class UserMessages(FromTomlFile):
    not_exsists__user_create: str
    creating__user_create: str
    created__user_update: str

    create_user: str
    update_user_not_full_info: str
    user_info: str

    username_updated: str
    login_updated: str

    input_prompt_login: str
    input_prompt_username: str


class Keyboard(FromTomlFile):
    inline_username: str
    inline_login: str
    inline_create_user: str


user_messages = UserMessages('resources/user.toml')
user_keyboard = Keyboard('resources/user.toml')
