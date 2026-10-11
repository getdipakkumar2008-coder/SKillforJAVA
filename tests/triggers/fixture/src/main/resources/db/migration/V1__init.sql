create table customers (id bigserial primary key, name varchar(200) not null, email varchar(200));
create table products (id bigserial primary key, name varchar(200) not null, price numeric(12,2) not null);
create table orders (id bigserial primary key, customer_id bigint not null references customers(id), status varchar(30) not null, total numeric(12,2));
create table order_lines (id bigserial primary key, order_id bigint not null references orders(id), product_id bigint not null references products(id), quantity int not null);
create table invoices (id bigserial primary key, owner_id bigint not null, amount numeric(12,2) not null, pdf_path varchar(500));
create table events (id bigserial primary key, aggregate_id bigint, type varchar(100), payload text, created_at timestamp not null);
create table users (id bigserial primary key, email varchar(200) not null);
