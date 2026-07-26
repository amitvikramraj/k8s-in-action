# Deploying a Kubernetes Cluster

## Running a Cluster locally

### Kubernetes in Docker Desktop

Docker desktop by default provides a single node Kubernetes Cluster.

![](./images/chapter-03/k8s-in-docker.png)

* Docker Desktop sets up a Linux VM that hosts the Docker Daemon and all the containers.
* This VM also runs the Kubelet—the Kubernetes agent that manages the node.
* The components of the control plane run in containers, as do all the applications you deploy.

At the time of writing, Docker Desktop provides no command to log into the VM if you want to explore it from the inside. However, you can run a special container configured to use the VM’s namespaces to run a remote shell, which is virtually identical to using SSH to access a remote server.

```shell
docker run --net=host --ipc=host --uts=host --pid=host --privileged \
  --security-opt=seccomp=unconfined -it --rm -v /:/host alpine chroot /host
```

* The container is created from the `alpine` image.

* The `--net`, `--ipc`, `--uts`, and `--pid` flags make the container use the host’s namespaces instead of being sandboxed, and the `--privileged` and `--security-opt` flags give the container unrestricted access to all sys-calls.

* The `-it` flag runs the container interactive mode, and the `--rm` flags ensures the container is deleted when it terminates.

* The `-v` flag mounts the host’s root directory to the `/host` directory in the container. The `chroot /host` command then makes this directory the root directory in the container.

After you run the command, you are in a shell that’s effectively the same as if you had used SSH to enter the VM. Use this shell to explore the VM—try listing processes by executing the `ps aux` command or explore the network interfaces by running `ip addr`.


### Minikube

Minikube is another tool to locally run a kubernetes cluster.

![](./images/chapter-03/minikube.png)

```shell
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-darwin-arm64 && sudo install minikube-darwin-arm64 /usr/local/bin/minikube

# start a single node cluster
minikube start

# If you use Linux, you can reduce the resource footprint of Minikube by creating the cluster without a VM.
minikube start --vm-driver none

# check status
minikube status

# to log into the Minikube VM
minikube ssh
```

The architecture of the system is practically identical to how Docker Desktop runs a clutser. The control plane components run in containers in the VM or directly in your host OS (in case of Linux) if you used the `--vm-driver none` option to create the cluster. The Kubelet runs directly in the VM’s or your host’s operating system. It runs the applications you deploy in the cluster via the Docker Daemon.

### Using kind (Kubernetes in Docker)

![](./images/chapter-03/kind.png)

* Instead of running Kubernetes in a VM or directly on host OS, kind runs each K8s cluster node inside a container.

* This feature allows it to easily create multi-node cluster by starting several container.

* And the application we deploy run inside these node containers.

* Running kubernetes using kind means that all K8s componentes run in the host OS as well as the applications we deploy to the cluster also run in the host OS. (in case on non-Linux machines in the VM running docker daemon)

* This makes kind the perfect tool for development and testing, as everything runs locally, and you can debug running processes as easily as when you run them outside of a container. 

```shell
# start single node cluster
kind create cluster

# create multi-node cluster
cat <<-EOF | kind create cluster --config -
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
    - role: control-plane
    - role: worker
    - role: worker
EOF

# `--config -` tells kind to read config from stdin
# <<-EOF preserves the leading tab spaces

# List worker nodes
$ kind get nodes
kind-worker2
kind-control-plane
kind-worker

# list all node using kubectl
$ kubectl get nodes -A --context kind-kind      
NAME                 STATUS   ROLES           AGE   VERSION
kind-control-plane   Ready    control-plane   40s   v1.35.0
kind-worker          Ready    <none>          26s   v1.35.0
kind-worker2         Ready    <none>          26s   v1.35.0

# Since each node runs as a container, you can also see the nodes by listing the running containers using:
$ docker ps                                                            
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS          PORTS                       NAMES
e4dbf9a7e195   kindest/node:v1.35.0   "/usr/local/bin/entr…"   59 seconds ago   Up 56 seconds                               kind-worker2
d0ec3c431c1a   kindest/node:v1.35.0   "/usr/local/bin/entr…"   59 seconds ago   Up 56 seconds   127.0.0.1:50692->6443/tcp   kind-control-plane
2470f4bc33e6   kindest/node:v1.35.0   "/usr/local/bin/entr…"   59 seconds ago   Up 56 seconds                               kind-worker

# delete a cluster
kind delete cluster --name <defaults to kind>
```

Unlike Minikube, where you use `minikube ssh` to log into the node if you want to explore the processes running inside of it, with kind, you use `docker exec`.

E.g: to enter the node called kind-control-plane, run

```shell
docker exec -it kind-control-plane bash
```

Instead of using Docker to run containers, nodes created by kind use the CRI-O container runtime as a lightweight alternative to Docker.

The crictl CLI tool is used to interact with CRI-O. Its use is very similar to that of the docker tool.

After logging into the node, list the containers running in it by using `crictl ps` instead of docker ps. Here’s an example of the command and its output:

```shell    
root@kind-control-plane:/# crictl ps
CONTAINER           IMAGE               CREATED             STATE               NAME                      ATTEMPT             POD ID              POD                                          NAMESPACE
ccf2b7e936606       909b40d32940f       2 minutes ago       Running             local-path-provisioner    0                   d82928158bd0c       local-path-provisioner-67b8995b4b-lnrqg      local-path-storage
d5ce443ec3353       e08f4d9d2e6ed       2 minutes ago       Running             coredns                   0                   a9b7859fc3b6d       coredns-7d764666f9-mlnjx                     kube-system
c5a86d6074da7       e08f4d9d2e6ed       2 minutes ago       Running             coredns                   0                   209b090f13478       coredns-7d764666f9-2xldb                     kube-system
e82dc373af069       c96ee3c174987       2 minutes ago       Running             kindnet-cni               0                   cbde80ae133a8       kindnet-ptfxb                                kube-system
16302fcb47701       de369f46c2ff5       2 minutes ago       Running             kube-proxy                0                   f1eb87f53cd4b       kube-proxy-54chl                             kube-system
f4da7bdd4a750       271e49a0ebc56       3 minutes ago       Running             etcd                      0                   c4ae7e452a726       etcd-kind-control-plane                      kube-system
dddd45682e397       c3fcf259c473a       3 minutes ago       Running             kube-apiserver            0                   d3b4977042e72       kube-apiserver-kind-control-plane            kube-system
07c7bf34574ef       88898f1d1a62a       3 minutes ago       Running             kube-controller-manager   0                   cfc4f3d37e024       kube-controller-manager-kind-control-plane   kube-system
f0f994206ebff       ddc8422d4d35a       3 minutes ago       Running             kube-scheduler            0                   66d0f7fd74f10       kube-scheduler-kind-control-plane            kube-system
```

## Interacting with Kubernetes

kubectl communicates with the Kubernetes API server, which is part of the Kubernetes Control Plane. The control plane then triggers the other components to do whatever needs to be done based on the changes you made via the API.

![](./images/chapter-03/kubectl.png)

kubectl loads it configuration from a config file called _kubeconfig_.


# Deploying an Application in a Cluster

## Running your first application

Two ways to deploy:

* **Declarative** — write YAML/JSON that describes the desired objects, then `kubectl apply`.
* **Imperative** — create objects with one-line commands like `kubectl create deployment` (easier when learning).

### Deployments

A **Deployment** is the object that represents an application running in the cluster. Creating one tells Kubernetes: “keep this many replicas of this container image running.”

```shell
$ kubectl create deployment kiada --image=kiada:latest
deployment.apps/kiada created
```

You specify:

1. Object type: Deployment
2. Name: `kiada`
3. Container image: `kiada:latest` (either from local docker daemon or pulled from Docker Hub by default)

This stores the object in the Kubernetes API — your **desired state**. Kubernetes then works to make the **actual state** match it.

```shell
$ kubectl get deployments
NAME    READY   UP-TO-DATE   AVAILABLE   AGE
kiada   0/1     1            0           6s
```

* `UP-TO-DATE` — how many replicas match the desired pod template
* `READY` / `AVAILABLE` — how many are actually ready to serve traffic

### Pods (not containers)

```shell
$ kubectl get containers
error: the server doesn't have a resource type "containers"
```

Containers are **not** a top-level Kubernetes object. The smallest deployable unit is a **pod**.

A **pod** is a group of one or more co-located containers that:

* Run on the **same worker node**
* Share Linux namespaces (network, UTS, and others depending on the pod spec)
* Share one IP, hostname, and port space — like a small logical computer for one application

![](./images/chapter-03/deployment.png)

Pods are scheduled across worker nodes. Containers in the same pod see each other as if alone on a machine; they don’t see processes from other pods, even on the same node.

### Listing and inspecting pods

Creating a Deployment creates one or more pods under it:

```shell
$ kubectl get pods
NAME                     READY     STATUS    RESTARTS   AGE
kiada-9d785b578-p449x    0/1       Pending   0          1m
```

Typical lifecycle:

1. **Pending** — scheduled (or waiting to be); node may still be pulling the image
2. **Running** — container created and started

If the image can’t be pulled (private registry, wrong name, etc.), `STATUS` shows the failure. Use `kubectl describe pod <name>` and check the **Events** section for scheduling, pull, create, and start details.

```shell
$ kubectl describe pod kiada-9d785b578-p449x
# ... look at Events at the bottom:
# Scheduled → Pulling → Pulled → Created → Started
```
