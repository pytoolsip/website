#！/bin/sh

# kill process
ps -ef | grep 'python3 manage.py runserver 172.16.0.8:8000' | awk '{print $2}' | xargs kill -9

# run process
nohup python3 manage.py runserver 172.16.0.8:8000 &
