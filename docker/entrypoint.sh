#!/bin/bash
service ssh start

# mkdir -p $2
# mv /data.db $2/data.db

URI_AUTH=$1
ADMIN=$2
ADDRESS=$3
PORT_AUTH=$4
PORT_DIR=$5
PORT_BLOB=$6
DB_AUTH=$7
DB_DIR=$8
DB_BLOB=$9

cd /docker && pip install -r requirements.txt && python3 setup.py install 
cd ..
python3 docker/restfs_auth/server.py -a $ADMIN -p $PORT_AUTH -l $ADDRESS -d $DB_AUTH &
python3 docker/restfs_dirs/server.py $URI_AUTH -p $PORT_DIR -l $ADDRESS -s $DB_DIR &
python3 docker/restfs_blob/server.py $URI_AUTH -p $PORT_BLOB -l $ADDRESS -s $DB_BLOB &

# python3 restdir_script/server_script.py https://auth.serv.com -a admin -d /db


exec /bin/bash