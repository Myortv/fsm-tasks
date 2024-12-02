create table user_profile(
    telegram_id bigint not null,
    username text not null,
    login text not null,
    unique(telegram_id)


);
CREATE TYPE task_state_enum AS ENUM (
    'not_exsists',
    'creating',
    'scheduled',
    'accepted',
    'in_work',
    'awaits_user_review',
    'finished',
    'canceled',
    'suspended'
);

create table task(
    id serial primary key,
    title text,
    description text,
    user_id int references user_profile(telegram_id) on delete cascade not null,
    state task_state_enum not null,
    created_at timestamptz not null default now()
);
