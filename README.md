# Bingo_RL

## Building and testing

1. Build the docker container image:
```
docker build . -t bingo:latest
```

2. Run the docker container image:
```
docker run -it bingo:latest /bin/bash
```

3. Run the python app:
```
python app.py
```

## End to end workflow

1. Build and test locally (see Building and testing section)
```
docker build . -t bingo:latest
```

2. Push the docker image to container registry
```
az acr login --name BingoRegistry
docker tag bingo:latest bingoregistry.azurecr.io/bingo:latest
docker push bingoregistry.azurecr.io/bingo:latest
```

3. Run the image from containter registry:

```
docker run bingoregistry.azurecr.io/bingo:latest
```

###
For running the yaml script in Azure Kubernets service 
Run the install.sh if on Linux or copy paste everything in cmd line

kubectl commands
kubectl delete -f bingo.yaml #Deleteing old pods
kubectl apply -f bingo.yaml #Create the pods and service as specified in the yaml
kubectl get pods #The kubernetes pods with its status
kubectl logs -f {podname} #For logs
