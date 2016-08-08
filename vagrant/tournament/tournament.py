#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

_ranked_players = []


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("Database connection failed")


def parseQuery(query, parameters=None):
    db, cursor = connect()
    cursor.execute(query, parameters)
    db.commit()
    db.close()


def fetchQuery(query, parameters=None):
    db, cursor = connect()
    cursor.execute(query, parameters)
    result = cursor.fetchall()
    db.commit()
    db.close()
    return result


def deleteMatches():
    """Remove all the match records from the database."""
    parseQuery("DELETE FROM matches")


def deletePlayers():
    """Remove all the player records from the database."""
    parseQuery("DELETE FROM players")


def countPlayers():
    """Returns the number of players currently registered."""
    return fetchQuery("SELECT count(players) as num FROM players")[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    parseQuery("INSERT INTO players (name) VALUES (%s)", (name, ))


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    query = "SELECT p_id, name, coalesce(wins, 0) wins,\
                    coalesce(matches, 0) matches, coalesce(bye, 0) bye\
             FROM (players left join\
                      (SELECT p_id as p, COUNT(m_id) as matches\
                       FROM allMatches\
                       GROUP BY p) as matchcounter\
                   on players.p_id = matchcounter.p left join\
                      (SELECT p_id as p, COUNT(m_id) as wins\
                       FROM winmatches\
                       GROUP BY p) as wincounter\
                   on players.p_id = wincounter.p left join\
                      (SELECT p_id as p, COUNT(m_id) as bye\
                       FROM byematches\
                       GROUP BY p) as byecounter\
                   on players.p_id = byecounter.p)\
                   as subquery\
             ORDER BY wins DESC"

    result = fetchQuery(query)
    return result


def reportMatch(winner, loser, tie):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    parseQuery("INSERT INTO matches (winner, loser, tie) \
               VALUES (%s, %s, %s)", (winner, loser, tie))


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    player_count = countPlayers()
    global _ranked_players
    _ranked_players = playerStandings()
    pair_result = []
    i = 0
    # If there are odd number of players, assign one player to skip this round
    # and count as a free win
    if player_count % 2 == 1:
        skipped = False
        while i < player_count-1:
            if not skipped:
                bye = _ranked_players[i][4]
                if bye < 1:  # this player haven't skipped yet
                    pid = _ranked_players[i][0]
                    reportMatch(pid, pid, True)
                    i += 1
                    skipped = True
            pair_result.append(getPair(i))
            i += 2
    else:
        while i < player_count-1:
            pair_result.append(getPair(i))
            i += 2
    return pair_result

def getPair(i):
    pid1 = _ranked_players[i][0]
    name1 = _ranked_players[i][1]
    pid2 = _ranked_players[i+1][0]
    name2 = _ranked_players[i+1][1]
    return (pid1, name1, pid2, name2)
