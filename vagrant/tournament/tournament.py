#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect(name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(name))
        return db
    except:
         print("Database connection failed")

def parseQuery(query, parameters=None):
    conn = connect()
    c = conn.cursor()
    c.execute(query, parameters)
    conn.commit()
    conn.close()

def fetchQuery(query, parameters=None):
    conn = connect()
    c = conn.cursor()
    c.execute(query, parameters)
    result = c.fetchall()
    conn.commit()
    conn.close()
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
    parseQuery("INSERT INTO players (name) VALUES (%s)" , (name, ))

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    query = "DROP VIEW IF EXISTS wincounter, matchcounter, standings cascade"
    parseQuery(query)

    query = "CREATE VIEW wincounter as\
    SELECT players.p_id, players.name, players.bye,\
           COUNT(winners.winner) as wins\
    FROM players LEFT JOIN winners ON players.p_id = winners.winner\
    GROUP BY players.p_id\
    ORDER BY wins DESC"

    parseQuery(query)

    query = "CREATE VIEW matchcounter as\
    SELECT p_id, COUNT(m_id) as matches\
    FROM\
        (SELECT players.p_id, matches.m_id\
        FROM players LEFT JOIN matches ON players.p_id = matches.player1\
        UNION\
        SELECT players.p_id, matches.m_id\
        FROM players LEFT JOIN matches ON players.p_id = matches.player2)\
        AS allMatches\
    GROUP BY p_id\
    ORDER BY matches DESC"

    parseQuery(query)

    query = "CREATE VIEW standings as\
    SELECT wincounter.p_id, name, wins, matches, bye\
    FROM wincounter JOIN matchcounter ON wincounter.p_id = matchcounter.p_id"

    parseQuery(query)

    return fetchQuery("SELECT p_id, name, wins, matches, bye FROM standings")

def reportMatch(winner, loser, tie):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    result = fetchQuery("INSERT INTO matches (player1, player2) \
               VALUES (%s, %s) RETURNING m_id", (winner, loser))
    m_id = result[0][0]
    if not tie:
        parseQuery("INSERT INTO winners (m_id, winner) \
                   VALUES (%s, %s)", (m_id, winner))
    else:
        parseQuery("INSERT INTO winners (m_id, winner) \
                   VALUES (%s, %s)", (m_id, winner))
        parseQuery("INSERT INTO winners (m_id, winner) \
                   VALUES (%s, %s)", (m_id, loser))

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
    ranked_players = playerStandings()
    pair_result = []
    i = 0
    # If there are odd number of players, assign one player to skip this round
    # and count as a free win
    if player_count % 2 == 1:
        skipped = False
        while i < player_count-1:
            if not skipped:
                if ranked_players[i][4] < 1: # this player haven't skipped yet
                    freeWin(ranked_players[i][0])
                    i += 1
                    skipped = True
            pair = (ranked_players[i][0], ranked_players[i][1], \
            ranked_players[i+1][0], ranked_players[i+1][1])
            pair_result.append(pair)
            i += 2
    else:
        while i < player_count-1:
            pair = (ranked_players[i][0], ranked_players[i][1], \
            ranked_players[i+1][0], ranked_players[i+1][1])
            pair_result.append(pair)
            i += 2
    return pair_result

def freeWin(playerId):
    parseQuery("UPDATE players SET bye = bye + 1 WHERE p_id = %s" %(playerId))
    result = fetchQuery("INSERT INTO matches (player1, player2) \
                       VALUES (%s, %s) RETURNING m_id", (playerId, playerId))
    m_id = result[0][0]
    parseQuery("INSERT INTO winners (m_id, winner) \
                VALUES (%s, %s)", (m_id, playerId))
