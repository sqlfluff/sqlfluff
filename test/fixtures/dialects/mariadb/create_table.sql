CREATE TABLE `foo` (
  b VARCHAR(255) BINARY,
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table `tickets` (
    `id` serial primary key,
    `material_number` varchar(255) default null,
    `material_name` varchar(255) default null,
    `date_created` date not null default (current_date),
    `date_closed` date default null
);

create table _ (a int);
