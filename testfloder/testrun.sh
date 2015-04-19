#!/bin/bash
zoostring=$1
input_q=$2
output_q=$3
w_capacity=$4
r_capacity=$5
dbase_names=$6
dbabse_proxy=$7
base_port=$8
num_db=0


echo $zoostring
echo $input_q
echo $output_q
echo $w_capacity
echo $r_capacity
echo $dbase_names
echo $dbabse_proxy
echo $base_port

IFS=, WORD_LIST=($dbase_names)
for word in ${WORD_LIST[@]}; do
 num_db=$(($num_db+1))
done

echo ""
echo ""


#gnome-terminal -e  ./../frontend/frontend.py $input_q; $SHELL
gnome-terminal -e "python ./../frontend/frontend.py $input_q"
echo "lalalalal"
#gnome-terminal -e "./backend.py $output_q"
#gnome-terminal -e "./database_backend.py $zoostring $input_q $output_q $w_capacity $r_capacity $dbase_names $num_db $dbabse_proxy $base_port"

