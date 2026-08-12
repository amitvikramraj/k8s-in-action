# Kiada Init Containers

Running two demo init container in Kiada Deployment to see how `initContainers` work in Kubernetes.

1. The first one emulates an initialization procedure and runs for 5 seconds and prints lines to stdout.

2. The secong one performs a network connectivity test using `ping` command to check if a specific IP address is reachable with the pod. Defaults to `1.1.1.1`.

3. There is a third container as well that runs as a sidecar container, reporting number of bytes in and out every 10 seconds from the Pod's network interface (eth0).
