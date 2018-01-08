drop table if exists flats;
    create table flats (
    id integer primary key autoincrement,
    timestamp text not null,
    price NUMERIC not null,
    commune text not null,
    flat text not null
);
