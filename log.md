docker build --no-cache -t ocean-operator:latest .
docker tag ocean-operator:latest micgoldberg/ocean-operator:latest
docker login
docker push micgoldberg/ocean-operator:latest

kubectl create namespace argocd
export ARGOCD_VERSION=v2.12.0
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/$ARGOCD_VERSION/manifests/core-install.yaml
kubectl config set-context --current --namespace=argocd # change current kube context to argocd namespace

kubectl apply -f argo-cd-app.yaml

argocd login --core
argocd admin dashboard -n argocd

kubectl apply -f oceanvngs-clusterrole.yaml

kubectl apply -f oceanvngs-clusterrolebinding.yaml

kubectl apply -f crd-oceanvng.yaml

kubectl apply -f ocean-operator-deployment.yaml




kubectl delete -f ocean-operator-deployment.yaml
