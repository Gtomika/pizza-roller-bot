docker pull public.ecr.aws/lambda/python:3.12
docker run --name amzn -d -t --rm public.ecr.aws/lambda/python:3.12 /bin/bash

# clean the contents of the root folder in the container first
docker exec amzn bash -c 'rm -rf /root/*'

# copy the required files in the container
docker cp requirements-lambda.txt amzn:/root/requirements-lambda.txt
docker cp build_lambda_artifacts.py amzn:/root/build_lambda_artifacts.py
# TODO do not copy 'local_testing.py' files
docker cp src amzn:/root/src

# install the required packages in the container
docker exec amzn bash -c '
cd /root
export SKIP_LAYER_BUILDING=0
python build_lambda_artifacts.py
'

# copy the artifacts from the container to the host
rm -rf artifacts
mkdir artifacts
docker cp amzn:/root/artifacts .