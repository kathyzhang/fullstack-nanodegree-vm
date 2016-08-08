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
    name text
);

create table matches(
    m_id serial primary key,
    winner serial references players(p_id) ON DELETE CASCADE,
    loser serial references players(p_id) ON DELETE CASCADE,
    tie boolean
);

CREATE VIEW tiedmatches as
    (SELECT m_id, winner as p_id
    FROM matches
    WHERE tie = true and winner <> loser
    UNION
    SELECT m_id, loser as p_id
    FROM matches
    WHERE tie = true and winner <> loser);

CREATE VIEW byematches as
    SELECT m_id, winner as p_id
    FROM matches
    WHERE winner = loser;

CREATE VIEW realwinmatches as
    SELECT m_id, winner as p_id
    FROM matches
    WHERE tie = false;

CREATE VIEW lostmatches as
    SELECT m_id, loser as p_id
    FROM matches
    WHERE tie = false;

CREATE VIEW winmatches as
    SELECT *
    FROM (SELECT * FROM tiedmatches UNION
          SELECT * FROM byematches UNION
          SELECT * FROM realwinmatches) as subquery;

CREATE VIEW allMatches as
    SELECT *
    FROM (SELECT * FROM winmatches UNION
          SELECT * FROM lostmatches) as subquery;
