from apache/superset:1.5.0

user root

run pip install --upgrade pip
run pip install gevent redis

env PYTHONPATH /etc/superset/:$PYTHONPATH
env PREFERRED_URL_SCHEME https

copy ./support/superset/superset_config.py /etc/pythonpath/superset_config.py
copy ./support/superset/init_superset.sh /usr/bin/init_superset.sh

cmd ["/usr/bin/init_superset.sh"]
user superset
