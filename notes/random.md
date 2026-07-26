The Core Concept: Ingress vs Gateway API
In Kubernetes, when you want to expose a service to external traffic (outside the cluster), there are two standard approaches:

Ingress (the legacy way): A single Ingress resource combines infrastructure concerns (which load balancer, TLS certs) and routing concerns (which hostname/path goes to which service) into one object. The cluster needs an Ingress Controller (like nginx-ingress) to implement it.

Gateway API (the successor): Splits the responsibility into two layers:

Gateway -- owned by the platform/infra team. Defines the load balancer, listeners, and TLS certificates. This is shared across many apps.
HTTPRoute -- owned by the application team. Says "for requests matching this hostname/path, send traffic to my Service." It attaches to an existing Gateway via parentRefs.

-----

https://www.reddit.com/r/kubernetes/comments/1sivn22/every_kubernetes_tool_explained_in_one_post_and/

Every Kubernetes Tool Explained In One Post (And Why They Exist)
The Kubernetes Ecosystem Has a Story. Every tool exists because Kubernetes alone wasn’t enough.

You run everything with kubectl. Get pods, describe, logs, exec, delete, apply, 50 times a day across 5 namespaces. It works, but it is slow and painful, specially -n namespcae in every command.

>> So you use K9s or Lens. A terminal UI that shows your entire cluster in one view. It lets you switch namespaces, different clusters, and tail logs, exec inside pod, and do everything you need.

You deploy with kubectl apply from your laptop. Someone changes a deployment directly on the cluster, and what is running no longer matches what is in Git. That is drift, and it is silent until prod breaks.

>> So you use ArgoCD. Git becomes the single source of truth, every change syncs to the cluster automatically, and if anyone touches a deployment manually ArgoCD overrides it back.

Your Kafka consumer has 200,000 messages piling up, CPU is at 5 percent, and HPA sees no reason to scale. The queue keeps growing, and users are waiting.

>> So you use KEDA. It scales pods on queue depth, SQS message count, or Prometheus metrics, and not just CPU. The backlog clears.

HPA adds pods during a spike, but the nodes are full, and new pods sit in Pending. HPA did its job, but the cluster had nowhere to put them.

>> So you use Karpenter. A new node appears in seconds when pods are stuck in Pending and disappears when the load drops. You only pay for what you use.

Every pod can talk to every other pod by default. Your payment service can reach your database, your internal tool can reach your logging service and nothing is blocked unless you block it.

>> So you use Network Policies. Your database only accepts traffic from the app, everything else is denied and the blast radius of a compromised pod shrinks dramatically.

You have 20 microservices, one starts responding slowly and retries pile up across 4 other services. A cascade begins and you have no visibility into where it started because all traffic is invisible.

>> So you use a Service Mesh. Istio or Linkerd puts a sidecar proxy next to every pod, gives you mTLS between every service, retries, circuit breaking and traffic metrics without touching a single line of app code.

Your secrets are Base64 encoded in Kubernetes, sitting in etcd and readable by anyone with kubectl access. You want them in Vault or AWS Secrets Manager but you do not want to rewrite your app to fetch them.

>> So you use the Secrets Store CSI Driver. Secrets live in Vault or AWS Secrets Manager and get mounted directly into your pod as files. The secret never lives in Kubernetes.

A developer ships a container running as root, another ships with no resource limits and you find out after the incident. Every time.

>> So you use Kyverno. Policies enforced at admission before anything enters the cluster, no root containers, no images without a digest and no deployments without limits.

Something is wrong. Pods are restarting, latency is spiking and memory is climbing but you have no numbers, no history and no way to know when it started.

>> So you use Prometheus and Grafana. Prometheus scrapes metrics from every pod, node and component and Grafana turns those numbers into dashboards. You see the spike, the exact time it started and which service caused it.

Grafana shows the spike but not which request triggered it, which service it hit first or where it slowed down. Logs give you fragments and metrics give you totals. Neither gives you the full story.

>> So you use Jaeger. It follows one request across every service it touches, shows you latency per hop and the exact failure point. The needle in the haystack, found in seconds.

