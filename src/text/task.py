from text.base import FromTomlFile


class TaskMessages(FromTomlFile):
    cant_move_to_this_state: str

    prompt_input__description: str
    prompt_input__title: str

    task_created: str
    task_discard: str
    task_list: str

    not_exsists__edit: str
    creating__edit: str
    scheduled__edit: str
    accepted__edit: str
    in_work__edit: str
    awaits_user_review__edit: str
    finished__edit: str
    canceled__edit: str
    suspended__edit: str

    not_exsists__general: str
    creating__general: str
    scheduled__general: str
    accepted__general: str
    in_work__general: str
    awaits_user_review__general: str
    finished__general: str
    canceled__general: str
    suspended__general: str

    not_exsists__move_state: str
    creating__move_state: str
    scheduled__move_state: str
    accepted__move_state: str
    in_work__move_state: str
    awaits_user_review__move_state: str
    finished__move_state: str
    canceled__move_state: str
    suspended__move_state: str

    input_prompt_title: str
    input_prompt_description: str


class TaskKeyboard(FromTomlFile):
    inline__edit: str
    inline__move_state: str

    inline__create: str
    inline__discard: str
    inline__description: str

    inline__title: str
    inline__right: str
    inline__left: str

    inline__not_exsists: str
    inline__creating: str
    inline__scheduled: str
    inline__accepted: str
    inline__in_work: str
    inline__awaits_user_review: str
    inline__finished: str
    inline__canceled: str
    inline__suspended: str


task_messages = TaskMessages('resources/task.toml')
task_keyboard = TaskKeyboard('resources/task.toml')
