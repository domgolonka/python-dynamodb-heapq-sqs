#!/bin/bash
zoostring=$1
input_q=$2
output_q=$3
w_capacity=$4
r_capacity=$5
dbase_names=$6
dbabse_proxy=$7
base_port=$8



echo $zoostring
echo $input_q=$2
echo $output_q
echo $w_capacity
echo $r_capacity
echo $dbase_names
echo $dbabse_proxy
echo $base_port


gnome-terminal -e ./frontend.py $input_q
gnome-terminal -e ./backend.py $output_q
gnome-terminal -e ./database_backend.py $zoostring $input_q $output_q $w_capacity $r_capacity $dbase_names $dbabse_proxy $base_port

