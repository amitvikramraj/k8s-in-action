# Navigating the Kubernetes API and Object Model

## The API is the control surface

Almost everything in Kubernetes is an **API object** (Pods, Deployments, Services, Nodes, config, security, …).

You don’t usually tell nodes what to do directly. You create/update objects via the API; controllers and kubelets react:

```text
kubectl / API client → API Server → Objects → Controllers / Kubelets → Actual state
```

```bash
kubectl create deployment kiada --image=kiada:latest
```

This creates a Deployment object. Other components observe it and make the cluster match.

> Kubernetes is **API-driven**: cluster state is represented as objects in the API.

---

## REST API; kubectl is a client

The Kubernetes API is an HTTP **REST** API:

| HTTP     | Meaning |
|----------|---------|
| GET      | read    |
| POST     | create  |
| PUT/PATCH| update  |
| DELETE   | delete  |

Resources live at URLs, e.g. `/apis/apps/v1/namespaces/default/deployments` (collection) vs `.../deployments/kiada` (one object).

`kubectl` is just a convenient CLI client for that API — not the API itself.

---

## Resource vs object

| Term       | Meaning |
|------------|---------|
| **Object** | The entity Kubernetes manages (`Deployment/kiada`) |
| **Resource** | The API endpoint used to access it (or a collection of them) |

Like: object ≈ row/entity; resource ≈ the API view into it.

Same object can appear under different API versions historically (`apps/v1` vs older groups) — different schemas, one underlying object.

---

## Object structure

Objects are YAML/JSON:

```bash
kubectl get node <node-name> -o yaml
```

Most objects share:

| Part                  | Role |
|-----------------------|------|
| `apiVersion` + `kind` | Schema and type (`apps/v1` + `Deployment`; core group uses `v1`) |
| `metadata`            | Identity: `name`, `uid`, labels, annotations |
| `spec`                | **Desired** state — what you want |
| `status`              | **Observed** state — what Kubernetes sees |

```text
You write SPEC → Controllers act → Reality changes → STATUS updated → You read STATUS
```

Not every object has `spec`/`status`. **Events** are records that “something happened”; they aren’t reconciled.

---

## Controllers and reconciliation

An object in the API is data. A **controller** watches it and runs a loop:

1. Read desired state  
2. Observe actual state  
3. Diff  
4. Act  
5. Update status  
6. Repeat  

Example: Deployment wants `replicas: 3`, sees 2 pods → creates one more → updates status.

> Kubernetes is a set of **continuous control loops**, not a one-shot command executor.

---

## Node objects

Each machine is a **Node** object:

```bash
kubectl get nodes
kubectl get node <name> -o yaml
```

Usually created by the **Kubelet** registering with the API server (not by you).

**`spec`** — node config (e.g. `podCIDR`, taints).  
**`status`** — machine reality:

| Field         | Meaning |
|---------------|---------|
| `addresses`   | IPs / hostname |
| `capacity`    | Total resources |
| `allocatable` | What Kubernetes can schedule |
| `conditions`  | Health signals |
| `images`      | Cached images |
| `nodeInfo`    | OS, kernel, runtime, component versions |

---

## Status conditions

Many objects expose independent health aspects under `status.conditions`:

```yaml
status:
  conditions:
    - type: Ready
      status: "True"
      reason: KubeletReady
      message: kubelet is posting ready status
```

Node examples: `Ready`, `MemoryPressure`, `DiskPressure`, `PIDPressure` — each `True` / `False` / `Unknown`.

`False` isn’t always bad (`MemoryPressure=False` = not under pressure).

Useful fields: `type`, `status`, `reason`, `message`, `lastHeartbeatTime` (last update), `lastTransitionTime` (last state change).

Why many conditions instead of one `status: Healthy`? Aspects are independent (Ready but DiskPressure), and new conditions can be added without breaking old clients.

> When something misbehaves, check `status.conditions` early.

---

## Exploring schemas: `kubectl explain`

```bash
kubectl explain node
kubectl explain node.spec
kubectl explain node.status.conditions
kubectl explain pods --recursive   # full field tree
```

Prefer this before searching the web for unfamiliar YAML fields.

---

## `kubectl get` vs `kubectl describe`

| Command | Think |
|---------|--------|
| `kubectl get … -o yaml` | Show me the **object’s data** |
| `kubectl describe …` | Human **diagnostic** view |

`describe` may pull related objects too (pods on a node, events) — it’s aggregated, not just pretty YAML.

---

## Talking to the API without kubectl

```bash
kubectl proxy   # e.g. 127.0.0.1:8001
curl http://127.0.0.1:8001/api/v1/nodes
```

Reinforces: kubectl is one client; the API is HTTP.

---

## Events

Controllers also emit **Events** (Normal / Warning) about actions and problems: scheduled, pulled image, started, insufficient resources, etc.

Events are **separate API objects**, not fields inside the Pod/Node. `kubectl describe` just shows related ones.

```bash
kubectl get events    # or: kubectl get ev
kubectl get ev -o wide
kubectl get ev --field-selector type=Warning
```

| Property   | Meaning |
|------------|---------|
| Type       | Normal / Warning |
| Reason     | Machine-facing code |
| Source     | Who emitted it |
| Object     | What it’s about |
| Message    | Human explanation |
| First/Last seen, Count | When / how often |

```text
Condition → What state is it in now?
Event     → What happened recently?
```

Events are **short-lived** (often ~1 hour) — not a permanent audit log. Inspect them while they’re still there.

---

## Useful commands

```bash
kubectl get nodes
kubectl get node <name> -o yaml|json
kubectl describe node <name>

kubectl explain node
kubectl explain node.status.conditions
kubectl explain pods --recursive

kubectl proxy

kubectl get events
kubectl get ev -o wide
kubectl get ev --field-selector type=Warning

kubectl get node <name> -o json | jq '.status.conditions'
```

---

## Debugging habit

```text
1. SPEC              → What did I ask for?
2. STATUS/CONDITIONS → What does Kubernetes observe?
3. EVENTS            → What happened while it tried?
```

```bash
kubectl get pod <pod> -o yaml      # spec + status
kubectl describe pod <pod>         # conditions + related events
kubectl get ev --field-selector type=Warning
```

---

## One-line mental model

You declare **what** you want in `spec`. Controllers continuously reconcile reality toward that. `status` reports the result; **events** explain the journey.
