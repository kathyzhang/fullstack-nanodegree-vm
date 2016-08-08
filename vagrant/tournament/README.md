## How to run this application:
Open vagrant virtual machine: "vagrant up"  
Login: "vagrant ssh"  
Go to directory tournament in vagrant: "cd /vagrant/tournament"  
Enter database: "psql"  
Import template file to create tournament database: "\i tournament.sql"  
Exit database: "\q"  
Run test file: "python tournament_test.py"  
Exit vagrant: "logout"

## Files
* tournament.sql contains SQL commands to create database, tables and  
views upon deleting the old database if exists.
* tournament.py contains functions that update and use the database  
information. It can also use Swiss system to pair players in a tournament  
according to player ranking data fetched from the database.
* tournament_test.py contains some unit tests that test the functions in  
tournament.py
