#!/bin/bash
zoostring=$1
input_q=$2
output_q=$3
w_capacity=$4
r_capacity=$5
dbase_names=$6
dbabse_proxy=$7
base_port=$8
num_db=1


echo $zoostring
echo $input_q
echo $output_q
echo $w_capacity
echo $r_capacity
echo $dbase_names
echo $dbabse_proxy
echo $base_port


#for word in ${WORD_LIST[@]}; do
 #num_db=$(($num_db+1))
#done

echo $num_db

echo $zoostring
echo ""
echo ""
echo i get here
gnome-terminal -e "python ./../database_backend.py $zoostring $input_q $output_q $dbase_names $base_port DB2 $num_db"
#gnome-terminal -e "python ./../database_backend.py $zoostring $input_q $output_q $dbase_name  $base_port DB1 $num_db"
echo ""
echo ""
#python ./../frontend/database_backend.py $zoostring $input_q $output_q $dbase_names $dbabse_proxy $dbabse_proxy $base_port DB2 $num_db
#gnome-terminal -e "python ./../proxy.py  7777 DB1"
# gnome-terminal -e "python ./../frontend/database_backend.py good $dbabse_proxy $dbabse_proxy; $SHELL"
 #gnome-terminal -e "python ./../frontend/database_backend.py okay $dbabse_proxy $dbabse_proxy; $SHELL"



#gnome-terminal -e  ./../frontend/frontend.py $input_q; $SHELL

#gnome-terminal -e "./backend.py $output_q"
#gnome-terminal -e "./database_backend.py $zoostring $input_q $output_q $w_capacity $r_capacity $dbase_names $num_db $dbabse_proxy $base_port"

