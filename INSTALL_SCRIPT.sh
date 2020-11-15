#https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough

# pre-req: install azure CLI
# pre-req: az aks install-cli

az login

az group create --name Bingo_game --location westus

az aks create --resource-group Bingo_game --name BingoCluster --node-count 1 --enable-addons monitoring --generate-ssh-keys

az acr create -n BingoRegistry -g Bingo_game --sku basic

az aks update -n BingoCluster -g Bingo_game --attach-acr BingoRegistry

az aks get-credentials --resource-group Bingo_game --name BingoCluster

kubectl apply -f bingo.yaml