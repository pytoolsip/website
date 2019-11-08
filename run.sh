#！/bin/sh

# kill process
ps -ef | grep 'python3 manage.py runserver xxx.xxx.xxx.xxx:xxx' | awk '{print $2}' | xargs kill -9

# run process
nohup python3 manage.py runserver xxx.xxx.xxx.xxx:xxx &
