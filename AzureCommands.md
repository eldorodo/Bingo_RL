## Login to Azure cli

```
az login
az account list --output table
az account set --subscription "Visual Studio Enterprise"
```

## Create Azure container registry:

Source: https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-azure-cli
```
az group create --name Bingo_game --location westus
```

```
az acr create --resource-group Bingo_game --name BingoRegistry --sku Basic
```
From the output, note the acr login server:
"loginServer": "bingoregistry.azurecr.io",

Login to the created container registry
```
az acr login --name BingoRegistry
```

## To push a docker images to container registry

```
docker tag bingo:latest bingoregistry.azurecr.io/hello-world:latest
docker push bingoregistry.azurecr.io/bingo:latest
```

## To remove the docker image
```
docker rmi bingoregistry.azurecr.io/bingo:latest
```

## To list ACR images in a container registry:
```
az acr repository list --name bingoregistry --output table
```

## Run the image from containter registry:
```
docker run -it bingoregistry.azurecr.io/bingo:latest /bin/bash
```

## To delete resource group:
```
az group delete --name myResourceGroup
```



