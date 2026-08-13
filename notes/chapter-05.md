# Running Applications with Pods

## 1. Pods: Kubernetes' Unit for Running Applications

A **Pod** is the smallest unit Kubernetes deploys and manages. It contains **one or more closely related containers that always run together on the same node**.

```text
Worker Node
┌─────────────────────────────────────┐
│ Pod A                               │
│ ┌───────────┐   ┌───────────────┐   │
│ │ Main App  │   │ Sidecar       │   │
│ │ Container │   │ Container     │   │
│ └───────────┘   └───────────────┘   │
└─────────────────────────────────────┘

A Pod never spans multiple nodes.
```

Usually, a Pod contains **one application container**. Multiple containers belong in the same Pod only when they form one tightly coupled unit.

### Why not run several processes in one container?

Containers are designed around the idea of **one main process per container**:

* logs from `stdout`/`stderr` remain attributable to one process;
* the container runtime monitors and restarts the container's **root process**, not arbitrary child processes;
* process lifecycle and health management remain simple.

If two processes need to cooperate closely, run them in **separate containers inside one Pod**, rather than stuffing them into one container.


## 2. What Containers in a Pod Share

Containers remain separate containers, but Kubernetes makes them behave almost like processes on the same machine by sharing several Linux namespaces.

```text
                         POD
┌────────────────────────────────────────────────────┐
│                                                    │
│  Container A                 Container B           │
│  ┌──────────────┐           ┌──────────────┐       │
│  │ own root FS  │           │ own root FS  │       │
│  └──────────────┘           └──────────────┘       │
│           │                       │                │
│           └──── optional Volume ──┘                │
│                                                    │
│  Shared:                                           │
│  ├── Network namespace → IP, interfaces, ports     │
│  ├── UTS namespace     → hostname                  │
│  └── IPC namespace     → IPC mechanisms            │
│                                                    │
│  PID namespace → separate by default; can share    │
└────────────────────────────────────────────────────┘
```

### Shared networking is especially important

All containers in a Pod have:

* the **same Pod IP**;
* the same network interfaces;
* the same port namespace;
* access to each other through `localhost`.

Therefore:

```text
App container:    localhost:8080
                       ▲
                       │ HTTP
                       │
Envoy sidecar:    localhost:8443
```

Two containers in the same Pod **cannot listen on the same port**.

Different Pods can use identical port numbers because each Pod has its own network namespace.

### Filesystems are different

Each container has its own Mount namespace/filesystem.

If containers need to share files, Kubernetes can mount the **same volume** into both containers.

### Processes

Containers normally have separate PID namespaces, so they can't see or signal each other's processes.

A Pod can instead use:

```yaml
spec:
  shareProcessNamespace: true
```

to give its containers a shared process namespace.


## 3. Choosing the Correct Pod Boundary

The Pod is also the **unit of scheduling and horizontal scaling**.

"Unit of scheduling" means that Kubernetes schedules a Pod onto a Node as a whole, not the individual containers inside that Pod.

Kubernetes scales:

```text
Pod
├── Container A
└── Container B
```

into:

```text
Pod 1             Pod 2             Pod 3
├── A              ├── A              ├── A
└── B              └── B              └── B
```

It does **not** independently replicate `A` or `B`.

This is why something like:

```text
Frontend + Database
```

usually shouldn't be one Pod.

They:

* don't need to run on the same node;
* have different scaling requirements;
* are independent components;
* may need different amounts of resources.

Use separate Pods:

```text
Frontend Pods                     Database Pod
┌──────────┐                      ┌──────────┐
│Frontend 1│                      │ Database │
└──────────┘                      └──────────┘
┌──────────┐
│Frontend 2│
└──────────┘
┌──────────┐
│Frontend 3│
└──────────┘
```

### When should containers share a Pod?

Put containers together only when they:

1. must run on the **same host**;
2. should be managed as **one unit**;
3. form one logical application component;
4. need to be **scaled together**;
5. can fit together on one node.

> **Rule of thumb:** Use separate Pods unless there is a specific reason the containers must live together.



## 4. Creating and Inspecting Pods

Pods are normally described declaratively with YAML and applied to the API.

A minimal Pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kiada
spec:
  containers:
  - name: kiada
    image: luksa/kiada:0.1
    ports:
    - containerPort: 8080
```

Apply it:

```bash
kubectl apply -f pod.kiada.yaml
```

`apply` can create an object or update an existing object. Some Pod fields are immutable; changing those requires deleting and recreating the Pod.

You can also generate starter YAML:

```bash
kubectl run kiada \
  --image=luksa/kiada:0.1 \
  --dry-run=client -o yaml > pod.yaml
```

### `containerPort` does not open a port

This field:

```yaml
ports:
- containerPort: 8080
```

is primarily **metadata/documentation**.

If an application listens on `8080`, it can receive connections even if `containerPort: 8080` isn't declared.

Declaring it is still useful because:

* people inspecting the Pod know which ports the application uses;
* ports can be given names;
* those names become useful when Services are introduced.

### What happens after creation?

The manifest you write is only the requested configuration. Reading the Pod back:

```bash
kubectl get pod kiada -o yaml
```

shows many additional fields added by Kubernetes, including the Pod's `status`.

Useful views:

```bash
kubectl get pod kiada
kubectl get pod kiada -o wide
kubectl describe pod kiada
```

Events show the startup sequence:

```text
Scheduled
   ↓
Pulling image
   ↓
Pulled
   ↓
Created container
   ↓
Started container
```



# 5. Accessing a Pod

Every Pod gets an IP address:

```bash
kubectl get pod kiada -o wide
```

Pod IPs normally belong to the **cluster network**, so your laptop usually can't reach them directly.

There are several useful ways to test connectivity.

### From a cluster node

```bash
curl <pod-ip>:8080
```

Useful when debugging the shortest network path between the node and Pod.

### From another Pod

```bash
kubectl run \
  --image=curlimages/curl \
  -it --restart=Never --rm \
  client-pod \
  curl <pod-ip>:8080
```

This answers:

> Can another Pod reach this Pod?

That's especially useful when network isolation/policies are involved.

### From your machine with port forwarding

Usually the most convenient development/debugging method:

```bash
kubectl port-forward pod/kiada 8080:8080
```

Then:

```bash
curl localhost:8080
```

The traffic path is roughly:

```text
curl
 │
 ▼
kubectl port-forward
 │
 ▼
API Server
 │
 ▼
Kubelet on Pod's node
 │
 ▼
Pod / Container
```

Port forwarding is convenient, but because it crosses several Kubernetes components, its failure doesn't necessarily mean ordinary Pod networking is broken.

### Through the API server

HTTP applications can also be proxied directly:

```bash
kubectl get --raw \
  /api/v1/namespaces/default/pods/kiada/proxy/
```

This is mainly useful for developers/admins rather than application clients.



# 6. Observing and Debugging Containers

## Logs

Containerized applications should normally log to:

```text
stdout
stderr
```

The runtime captures these streams and Kubernetes exposes them through:

```bash
kubectl logs kiada
```

Useful variants:

```bash
# Follow logs
kubectl logs kiada -f

# Include timestamps
kubectl logs kiada --timestamps

# Last two minutes
kubectl logs kiada --since=2m

# Last 10 lines
kubectl logs kiada --tail=10

# Logs from previous container instance after restart
kubectl logs kiada --previous
```

Logs are **per container**, not really per Pod.

For multi-container Pods:

```bash
kubectl logs kiada-ssl -c envoy
kubectl logs kiada-ssl -c kiada

# All containers
kubectl logs kiada-ssl --all-containers
```

### Log lifetime

A restarted container gets a new log file. `--previous` lets you inspect the previous instance.

Pod deletion removes its local container logs, and logs may also be rotated.

Therefore:

> `kubectl logs` is useful for debugging, but permanent logs require a centralized logging system.



## `exec`: run commands inside a container

Run one command:

```bash
kubectl exec kiada -- ps aux
```

or start an interactive shell:

```bash
kubectl exec -it kiada -- bash
```

Think of `kubectl exec` roughly as:

```text
SSH-like command execution
into a container
```

For a multi-container Pod:

```bash
kubectl exec -it kiada-ssl -c envoy -- bash
```



## `attach`: connect to the application's existing process

`exec` creates another process.

`attach` connects to the **stdin/stdout/stderr of the container's existing main process**.

```text
kubectl exec
    │
    └── starts another process

kubectl attach
    │
    └── connects to existing process
```

To allow an application to read stdin:

```yaml
containers:
- name: kiada
  stdin: true
```

Then:

```bash
kubectl attach -i kiada
```

`stdinOnce: true` can be used if stdin should remain available only for the first attach session.



## Copying files

```bash
# Container → local machine
kubectl cp kiada:/html/index.html /tmp/index.html

# Local machine → container
kubectl cp /tmp/index.html kiada:/html/
```

This can be useful during development/debugging, but modifying production containers manually isn't normal Kubernetes practice.

The chapter notes that `kubectl cp` depends on `tar` being available in the container.



# 7. Ephemeral Containers: Debugging Minimal Production Images

Production images are often intentionally minimal:

```text
Application binary
        +
 required libraries
        +
 almost nothing else
```

This improves security and image size but may leave you without:

* a shell;
* `curl`;
* `tcpdump`;
* networking utilities;
* other debugging tools.

Instead of rebuilding the application image, add an **ephemeral debug container** to the existing Pod:

```bash
kubectl debug kiada -it --image=nicolaka/netshoot
```

```text
Existing Pod
┌──────────────────────────────────────┐
│ App Container                       │
│                                     │
│ + Ephemeral Debug Container         │
│   curl / tcpdump / ip / netcat ...  │
└──────────────────────────────────────┘
```

The important benefit is that you can inspect the **actual problematic Pod** without recreating it.

If you also need visibility into processes from the other containers:

```yaml
shareProcessNamespace: true
```

Ephemeral containers are therefore preferable to permanently installing debugging tools in every production image.



# 8. Sidecars: Extending an Application

A **sidecar** is a supporting container that complements the Pod's primary application. 

Examples include:

* TLS/reverse proxies;
* log processors/collectors;
* content synchronization agents;
* communication adapters;
* data processors.

The chapter's example adds Envoy:

```text
              HTTPS :8443
                   │
                   ▼
             ┌──────────┐
             │  Envoy   │  Sidecar
             └────┬─────┘
                  │ HTTP via localhost:8080
                  ▼
             ┌──────────┐
             │  Kiada   │  Main application
             └──────────┘

              SAME POD
```

Because the containers share the Pod's network namespace, Envoy can simply forward requests to:

```text
localhost:8080
```

This can extend an application without modifying its code.

The trade-off is additional:

* CPU;
* memory;
* latency;
* operational complexity.

### Regular containers start together

If a Pod contains:

```yaml
containers:
- name: kiada
- name: envoy
```

Kubernetes starts them **in parallel**. You cannot use the regular `containers` list to express:

```text
Start A
then start B
```

That requirement leads to init containers.



# 9. Init Containers and Startup Ordering

**Init containers** perform work before the Pod's regular containers start.

They are executed **sequentially**:

```text
Pod starts
   │
   ▼
Init Container 1
   │ must complete successfully
   ▼
Init Container 2
   │ must complete successfully
   ▼
Main containers
   ├─────────────► App
   └─────────────► Envoy
       start together
```

Manifest:

```yaml
spec:
  initContainers:
  - name: init-demo
    image: ...

  - name: network-check
    image: ...

  containers:
  - name: kiada
    image: ...
```

Typical uses:

* generate/download configuration;
* initialize shared volumes;
* fetch certificates or keys;
* modify shared network configuration;
* wait until another service becomes available;
* notify an external service before startup.

### Why separate initialization from the application?

It:

* keeps initialization logic out of the main image;
* allows initialization images to be reused;
* guarantees initialization completes before main containers start;
* can improve security.

For example, credentials needed only for registration can exist in the init container instead of the long-running application container.

While starting, Pod status may progress roughly through:

```text
Pending
   ↓
Init:0/2
   ↓
Init:1/2
   ↓
PodInitializing
   ↓
Running
```

Init-container logs are inspected just like normal container logs:

```bash
kubectl logs <pod> -c <init-container>
```

`kubectl exec` works while an init container is still running, but once it finishes there is no running container to enter.



# 10. Kubernetes Native Sidecar Containers

Sometimes a supporting container must:

* start **before** some init containers;
* remain alive during the entire Pod lifetime;
* stop **after** the main containers.

A normal sidecar can't guarantee this ordering.

Kubernetes supports **native sidecars** by defining them under `initContainers` with:

```yaml
restartPolicy: Always
```

Example:

```yaml
spec:
  initContainers:
  - name: init-demo
    image: ...

  - name: traffic-meter
    image: ...
    restartPolicy: Always

  - name: network-check
    image: ...

  containers:
  - name: kiada
    image: ...
```

Their lifecycle differs from ordinary init containers:

```text
init-demo
   │ completes
   ▼
traffic-meter (native sidecar)
   │ starts and KEEPS RUNNING
   ▼
network-check
   │ completes
   ▼
main container(s) start
   │
   │
traffic-meter keeps running
```

Unlike a normal init container, Kubernetes **doesn't wait for the native sidecar to terminate** before continuing.

It is restarted if it exits and stays alive while the Pod runs.

### Shutdown ordering

Regular containers are stopped first.

Native sidecars are stopped afterward:

```text
Main containers
      │
      ▼
    STOP
      │
      ▼
Native sidecars
      │
      ▼
    STOP
```

> Kubernetes terminates native sidecars in the reverse order of their appearance in the initContainers list.

This matters for infrastructure such as:

* network proxies;
* traffic monitoring;
* log collectors.

A logging sidecar shouldn't disappear before the application produces its final log messages.

The chapter's rule is essentially:

> If the Pod depends on the sidecar being available for its correct startup or shutdown behavior, use a native sidecar. Otherwise, an ordinary additional container may be sufficient.
