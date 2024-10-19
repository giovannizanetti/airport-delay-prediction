PORT=$1
docker run -d -p $PORT:8080 --name airport_api airport_delay_api 