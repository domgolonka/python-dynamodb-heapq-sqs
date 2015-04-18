gnome-terminal -e "./frontend.py localhost 8080 DB1 2 7777 localhost DB1"
gnome-terminal -e "./frontend.py localhost 8081 DB2 2 7777 localhost DB1"
gnome-terminal -e "./proxy.py  7777 DB1,DB2 DB1 DB1"
