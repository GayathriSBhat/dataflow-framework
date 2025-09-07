## Run tests

# File mode:

python main.py -c pipeline.yml -i sample_logs.txt


# Stdin (docker) mode:

docker logs -f my_container | python main.py -c pipeline.yml