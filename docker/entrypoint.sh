#!/bin/bash
service ssh start

# mkdir -p $2
# mv /data.db $2/data.db

cd /docker && python3 setup.py install 
cd ..
python3 docker/restfs_auth/server.py -a admin &
python3 docker/restfs_dirs/server.py -a admin &
cd ../auth_api && python3 setup.py install
python3 ./auth_src/server.py -d $2 -a $3 -l $4 -p 3001  &

# python3 restdir_script/server_script.py https://auth.serv.com -a admin -d /db


exec /bin/bash