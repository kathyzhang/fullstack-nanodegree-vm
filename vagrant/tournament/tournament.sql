-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

create table players(
    p_id serial primary key,
    name text,
    bye integer default 0
);

create table matches(
    m_id serial primary key,
    player1 serial references players(p_id) ON DELETE CASCADE,
    player2 serial references players(p_id) ON DELETE CASCADE
);

create table winners(
    m_id serial references matches(m_id) ON DELETE CASCADE,
    winner serial references players(p_id) ON DELETE CASCADE
);
