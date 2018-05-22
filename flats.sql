drop table if exists flats;
    create table flats (
    id integer primary key autoincrement,
    timestamp text not null,
    commune text not null,
    address text,
    rooms integer,
    bathroom integer,
    size integer,
    price NUMERIC not null,
    flat text not null
);
