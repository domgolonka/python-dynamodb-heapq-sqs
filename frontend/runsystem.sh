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

#IFS=, WORD_LIST=($dbase_names)
#for word in ${WORD_LIST[@]}; do
 #num_db=$(($num_db+1))
#done

gnome-terminal -e "python ./frontend.py $input_q $output_q"
gnone-terminal -e "python ./backend.py $output_q"

gnome-terminal -e "python ./database_backend.py cloudsmall1.cs.surrey.sfu.ca $input_q $output_q $w_capacity $r_capacity $dbase_names $dbabse_proxy $base_port DB1 $num_db"
gnome-terminal -e "python ./database_backend.py cloudsmall1.cs.surrey.sfu.ca $input_q $output_q $w_capacity $r_capacity $dbase_names $dbabse_proxy $base_port DB2 $num_db"
gnome-terminal -e "python ./database_backend.py cloudsmall1.cs.surrey.sfu.ca $input_q $output_q $w_capacity $r_capacity $dbase_names $dbabse_proxy $base_port DB3 $num_db"

