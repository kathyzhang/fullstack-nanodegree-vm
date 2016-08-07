rdb-fullstack
=============

Common code for the Relational Databases and Full Stack Fundamentals courses

## Project Tournament:
* A Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament using the Swiss system for pairing up players in each round.
* Swiss system: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

#### How to run this application:
Open vagrant virtual machine: "vagrant up"  
Login: "vagrant ssh"  
Go to directory tournament in vagrant: "cd /vagrant/tournament"  
Enter database: "psql"  
Import template file to create tournament database: "\i tournament.sql"  
Exit database: "\q"  
Run test file: "python tournament_test.py"  
