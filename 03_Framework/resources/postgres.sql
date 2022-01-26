create table errors
(
    id         integer   default nextval('errors_id_seq_1'::regclass) not null
        constraint errors_pk
            primary key,
    source     text,
    message    text,
    site_id    integer,
    time       timestamp default now(),
    browser_id text,
    visit_id   text,
    backup     text
);

alter table errors
    owner to measurement;

create unique index errors_id_uindex
    on errors (id);

create table sites
(
    id                                       integer default nextval('sites_id_seq'::regclass) not null
        constraint sites_pk
            primary key,
    rank                                     integer,
    site                                     text,
    subpages                                 text,
    scheme                                   text,
    subpages_count                           integer,
    state_scheme                             integer,
    state_subpages                           integer,
    site_state                               text,
    ready                                    boolean,
    state_chrome_desktop_ger                 integer default '-1'::integer,
    state_chrome_desktop_usa                 integer default '-1'::integer,
    state_chrome_desktop_jp                  integer default '-1'::integer,
    state_chrome_interaction_ger             integer default '-1'::integer,
    state_chrome_interaction_usa             integer default '-1'::integer,
    state_chrome_interaction_jp              integer default '-1'::integer,
    state_chromeheadless_desktop_ger         integer default '-1'::integer,
    state_chromeheadless_desktop_usa         integer default '-1'::integer,
    state_chromeheadless_desktop_jp          integer default '-1'::integer,
    state_chromeheadless_interaction_ger     integer default '-1'::integer,
    state_chromeheadless_interaction_usa     integer default '-1'::integer,
    state_chromeheadless_interaction_jp      integer default '-1'::integer,
    state_openwpm_desktop_ger                integer default '-1'::integer,
    state_openwpm_desktop_usa                integer default '-1'::integer,
    state_openwpm_desktop_jp                 integer default '-1'::integer,
    state_openwpm_interaction_ger            integer default '-1'::integer,
    state_openwpm_interaction_usa            integer default '-1'::integer,
    state_openwpm_interaction_jp             integer default '-1'::integer,
    state_openwpmheadless_desktop_ger        integer default '-1'::integer,
    state_openwpmheadless_desktop_usa        integer default '-1'::integer,
    state_openwpmheadless_desktop_jp         integer default '-1'::integer,
    state_openwpmheadless_interaction_ger    integer,
    state_openwpmheadless_interaction_usa    integer default '-1'::integer,
    state_openwpmheadless_interaction_jp     integer default '-1'::integer,
    timeout                                  integer,
    state_chrome_repeated_ger                integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_1  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_2  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_3  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_4  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_5  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_6  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_7  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_8  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_9  integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_10 integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_11 integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_12 integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_13 integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_14 integer default '-1'::integer,
    state_chrome_desktop_ger_repeated_day_15 integer default '-1'::integer
);

alter table sites
    owner to measurement;

create unique index sites_id_uindex
    on sites (id);

create table visits
(
    id                integer default nextval('visits_id_seq_1'::regclass),
    site_id           integer,
    subpage_id        integer,
    url               text,
    start_time        timestamp,
    finish_time       timestamp,
    state             integer,
    browser_id        text,
    timeout           integer,
    push_request      integer,
    push_response     integer,
    push_cookie       integer,
    push_localstorage integer,
    visit_id          text
);

alter table visits
    owner to measurement;

create table tranco_list
(
    id                       integer default nextval('tranco_list_id_seq'::regclass) not null,
    rank                     integer,
    site                     text,
    subpages                 text,
    scheme                   text,
    subpages_count           integer,
    state_scheme             integer,
    state_subpages           integer,
    site_state               text,
    ready                    boolean,
    state_chrome_desktop_ger integer default '-1'::integer
);

alter table tranco_list
    owner to measurement;

