# Деплой
1. Клонирование проекта
2.  Создание .env файла
3.  Создание logfile
4. Сборка/запуск


### Клонирование проекта
```bash
git clone
```


### дотенв
Минимальный формат .env файла выглядит так:
```.env
PYROGRAM_API_ID=
PYROGRAM_API_HASH=""
PYROGRAM_BOT_TOKEN=""
```
Полные настройки можно найти в `src/core/configs.py`

### logifile
Нужно создать директорию для логов и первый файл для логов:
```bash
mkdir ...logs
touch ...logs/logfile
```
### Сборка/запуск
```bash
docker compose build
docker compose run
```
Первый запуск может закончиться падением -- это происходит из-за того, что постгресс занят созданием базы данных и основном приложение не дожидаясь, падает. Просто перезапустите после успешного создания базы данных.

```bash
docker compose restart pyrogram_bot
```


# Обзор задачи
В задаче было сказано создать бота для создания и управления задачами. Также бот ожидает первым действием регистрацию пользователя с юзернеймом и логином.
Так как в задаче было упомянуто использования fsm, для большей наглядности, я дал задачам статус и возможность менять статус, с разными статусами в которые можно перейти из текущего.


# Обзор технологий
База данных -- postgres (стандартный стек, поддержка множественной записи, в общем no-brain вариант)
Для работы с данными -- pydantic (консинстентая работа с данными, обработка инпута, взял потому что быстрый и удобно расширяет dataclasses с возможностью валидировать поля например)
Для работы с настройками -- pydantic-settings (загрузка настроек, поддерживает разные типы файлов с настройками)
Для работы с текстами -- toml (просто более человечный способ хранить текст чем json)
Враппер для постреса -- asyncpg (одна из наиболее популярных асинхронных обёрток)


# Архитектура

Основная логика проекта лежит в `src/bot/`.




# Обзор

## Обзор FSM:


Хотя FSM может показаться удачным для организации работы ботов, он также приносит одну из наиболее сложных проблем для решения. И эта проблема описывается прямо в названии:
> Finite **STATE** machine

Дело в том, что fsm становится ещё одним местом, где хранится состояние наших данных и неизбежно он будет де-синхронизироваться со стейтом самой базы данных (true state).


На самом деле проблема десинхронизации довольно известна и встречается повсеместно в веб разрабоке -- это дeсинхронизация стейта между фронтендом и бэкендом,
когда какие-то крупные фреймворки вроде реакта хранят данные на фронте и пытаются отображать фронтенд в соответствии с ними.


Конечно, есть разные подходы для решения этой проблемы, но один из них с которыми я хорошо знаком -- htmx. Его решение этой проблемы: не решать проблему
а избавиться от неё фундаментально -- не храня состояние на фронтенде.

Вдохновившись этой идеей, я сделал fsm, которая не хранит состояние сама. Для чего же она используется, если не хранить стейт?

1. Для управления стейтом
2. Для вывода данных основываясь на стейте данных

## Управление состоянием
`src/fsm/base.py` Предоставляет простой класс-родитель для FSM классов в  `src/fsm/user.py` `src/fsm/task.py`.
Помогает с управлением состояний он тем образом, что создаёт простой интерфейс для проверки валидности перехода объекта из одного стейта в другое.


```python
# from src/fsm/user.py
class UserFSM(FSM):
    """FSM to manage user representations"""
    default_move_rules = {
        UserPrototypeState.not_exsists.name: [
            UserPrototypeState.creating.name
        ],
        UserPrototypeState.creating.name: [
            UserPrototypeState.created.name
        ],
        UserPrototypeState.created.name: [],
    }
...
  
# from src/fsm/base.py
class FSM():
    ...
    def can_move(self, state_from: str, state_to: str):
        return state_to in self.move_rules[state_from]
...
```


В нашем классе, который работает с конкретным типом данных, мы описваем в переменной класса `default_move_rules` из какого в какие
стейты мы можем переводить объект.

Родительский класс же предоставляет простой метод, который фактически проверят, может ли стейт быть переведён.
Хотя этот подход не создаёт прямых ограничений для перехода состояний объекта, всё ещё является достаточным, чтобы предотвратить невозможные переводы, если учитывать, что функция для перевода стейта выглядит так:


```python
# from src/repository/task.py
async def move_state(task_id: int, state: str) -> TaskInDB | None:
    """Use this to ensure status changes is valid"""
    async with DatabaseConnection(postgres_manager) as conn:
        async with conn._wrapped_connection.transaction():
            result = await conn.fetchrow(
                "select * from task where id = $1 for update",
                task_id,
            )
            if not result:
                return
            task = TaskInDB(**result)
            if not task_fsmlike_wrapper.can_move(
                task.state.name,
                state,
            ):
                return
            await conn.fetchrow(
                'update task set state = $1 where id = $2',
                state,
                task_id,
            )
    if result:
        return TaskInDB(**result)  
```

## Вывод/подготовка данных

Мало того, что данные могут иметь разное состояние, но также они могут выводиться в разном виде.
Например, задачу (task) можно вывести в общем виде, где просто видны данные задачи, но также и в виде для редактирования,
где в самом сообщении телегарм бота хотелось бы видеть какую-то инструкцию и inline buttons для редактирования полей.

Такие варианты вывода, я назвал `representations`. `FSM` позволяет создавать разные репрезентации данных и связывает их
с разными состояниями, опционально вызывая стандартный (default) обработчик.

Например, мы хотим general репрезентацию, чтобы выводить просто данные объекта.
Для этого мы напишем:


```python
# from src/fsm/tasks.py
class TaskFSM(FSM):
    """FSM for tasks"""
  ...
    async def handle_general(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """general api func to handle general representation"""
        return await self.handle_representation(
            "general",
            state,
            *args,
            task=task,
            **kwargs
        )

    async def default_general(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        """default (all states) handler for general representation"""
        return (
            task_messages.get(f"{state}__general").format(
                ...
            ),
            InlineKeyboardMarkup(
                ...
            )
        )
  
```

`handle_general` -- методы, начинающиеся с "handle_" можно рассматривать как api методы, которые предполагаются для использования в коде.
В нашем случае, `handle_general` вызывает `self.handle_representation`, передавая все входные аргументы. В таком случае, FSM попробует
определить, какой метод вызывать для каждого стейта: если спецефичный для стейта метод назначен, будет вызываться он, иначе будет
вызываться стандартный метод для этой репрезентации.

Стандартный метод определён ниже, это `default_general`. Соответственно, он будет вызываться, если никакой спецефичный для стейта
метод не определён. Давайте определим спецефичный метод для состояния "pending":

```python
...
    async def pending_general(
        self,
        state: str,
        task: TaskPrototype | TaskInDB,
        *args,
        **kwargs,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        #some logic here
...
  
```

> Спецефичные для состояния методы называются по принципу `{state}_{representation}`. Убедитесь, что название соответсвует
этому правилу, потому что иначе FSM не вызовет этот метод.


Таким образом, FSM организовывает репрезентации данных в разных стейтах и для разных применений.


## Краткий обзор остального кода
### База данных
Функции для взаимодействия с базой данных находятся в `src/repository/`.
В `src/repository/db.py` лежат поддерживаюшие классы и методы. В основном это интерфейсы и классы-обёртки для asyncpg,
позволяющие в случае чего с меньшими проблемами поменять движок или базу данных.
Внимания заслуживает только `DatabaseManager`, который отвечает за управлением подключениями к базе данных и в нашем случае
используется для работы с пулом а также `DatabaseConnection`, который является контекстным менеджером и работает с
`DatabaseManager`.

В основном, поддерживающий код писался с интенцией сделать переход с движка или базы данных менее болезненными.


### Бот
Код связанный с логикой бота находится в `src/bot/`.
Весь код внутри модулей находится внутри init функций решения проблем с передачей app внутрь этих модулей, что позволяет (с оговорками)
использовать возможность pyrogram запускать несколько инстансов клиентов.


Оговоркой же является обработка пользовательского инпута.


#### Пользовательский инпут
Библиотечный код для работы с вводом лежит в `src/utils/user_states.py`. Если пробегаться по этому файлу вкратце, то код здесь
позволяет привязовать функции к определённым состояниям. Когда в другом месте пользователь получает какое-то состояние, следующий раз
он введёт текст и отправит его, связанная с этим состоянием функция будет вызвана.

#### Текст
Весь текст бота хранится в `resourses/` внутри `.toml` файлов. Код для работы с текстом лежит в `src/text/base.py`.
Фактически, содержимое `.toml` выгружается в модели pydantic.


# Функционал

### Регистрация
Первым делом при заходе в бота, вас встретят с просьбой зарегестрироваться. Вы не сможете пройти дальше без регистрации.
Вам отправят сообщение с двумя inline кнопками.
Нажимая на каждую, вам предложат ввести данные. После ввода появится то же сообщение, но количество кнопок будет меньше (не предложат повторно вводить)
Когда все кнопки были нажаты, вам предложат создать аккаунт, после чего вы увидите приветственное сообщение и у вас появится клавиатура.

#### /start
Показвает экран регистрации, если вы ещё не зарегестрировались. Показвает приветственное сообщение, если зарестрировались.

### Меню
#### Новая задача
Нажимая в нижнем меню на кнопку новая задача, вам покажут сообщение с двумя inline кнопками. Нажимая на них, вы получите предложение ввести и отправить данные.
Если вы случайно перейдёте в другое меню или сделаете что-то другое, ввод сохраниться. После первого ввода, появится кнопка для сброса всего ввода.
Когда вы введёте все данные, появится кнопка для создания задачи.

#### Все задачи
Нажимая на все задачи, будет выведен список всех ваших задач. Список ограничевается 10 задачами, если у вас больше 10 задач, внизу списка появится кнопка для навигации по страницам.
На первой странице всегда будет видна только кнопка "вправо", на последней странице -- только кнопка "влево"

Нажимая на кнопку с названием задачи, вы получите сообщение с содержимым задачи и две кнопки. Первая откроет меню редактирования, вторая откроет меню изменения состояния.
Нажав на меню редактирования, вы увидите кнопки с полями доступными для редактирования. Нажав на них, вам предложат ввести новые данные.
Нажав на меню перемещения состояния, вы увидите список кнопок с доступными состояниями. Нажав на состояние, вы измените состояние задачи.
Вернувшись в это меню, вы можете увидеть новые возможные состояния для изменения.
Если нажать на кнопку состояния, в которое нельзя перейти вам сообщат что это невозможно.

#### Мой аккаунт
Нажимая на мой аккаунт, вы получите данные своего аккаунта с кнопками полей. Нажимая на них, вы получите предложение для ввода данных. Введя данные, вы обновите данные аккаунта.

#### Правила
Выводит сообщения с правилами использования


# SQL
Честно говоря я на этом этапе столько воды налил. Особо никаких интересных запросов нет -- просто запись данных в базу. Сами данные в базе простые. Единственное что следует отметить -- 
для изменения состояния используется транзакция. На этом всё, фактически.