#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def parseQuery(query):
    conn = connect()
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    conn.close()

def fetchQuery(query):
    conn = connect()
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    conn.close()
    return result

def deleteMatches():
    """Remove all the match records from the database."""
    parseQuery("DELETE FROM matches")
    parseQuery("UPDATE players SET wins = 0, matches = 0")

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
    name = bleach.clean(name)
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (name) VALUES (%s)" , (name, ))
    conn.commit()
    conn.close()

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
    query = "SELECT p_id as id, name, wins, matches, bye \
             FROM players ORDER BY wins DESC"
    results = fetchQuery(query)
    ranked_players = [(str(row[0]), str(row[1]), int(row[2]), \
                       int(row[3]), bool(row[4]))
                      for row in results]
    return ranked_players

def reportMatch(winner, loser, tie):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    if not tie:
        c.execute("INSERT INTO matches (player1, player2, winner) \
                   VALUES (%s, %s, %s)", (winner, loser, winner))
        c.execute("UPDATE players SET wins = wins + 1, matches = matches + 1 \
                   WHERE p_id = %s" %(winner))
        c.execute("UPDATE players SET matches = matches + 1 \
                   WHERE p_id = %s" %(loser))
    else:
        c.execute("INSERT INTO matches (player1, player2) \
                   VALUES (%s, %s)", (winner, loser))
        c.execute("UPDATE players SET wins = wins + 1, matches = matches + 1 \
                   WHERE p_id = %s" %(winner))
        c.execute("UPDATE players SET wins = wins + 1, matches = matches + 1 \
                   WHERE p_id = %s" %(loser)) # if tie, both players win
    conn.commit()
    conn.close()

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
    parseQuery("UPDATE players SET wins = wins + 1, matches = matches + 1, \
    bye = bye + 1 WHERE p_id = %s" %(playerId))
