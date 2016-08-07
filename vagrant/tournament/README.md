## How to run this application:
Open vagrant virtual machine: "vagrant up"  
Login: "vagrant ssh"  
Go to directory tournament in vagrant: "cd /vagrant/tournament"  
Enter database: "psql"  
Import template file to create tournament database: "\i tournament.sql"  
Exit database: "\q"  
Run test file: "python tournament_test.py"  
