# Exetending Kiada FastAPI app using Envoy Proxy

Adding TLS support to the app so that it can also serve clients over HTTPS.

Even the FastAPI app can be configured to do so, but an easier option is to add a reverse proxy (like Envoy) in front of the app that can receive HTTPS requests on behalf of the application.

Also I am doing this to try running multiple containers in a pod.

So the new architecture of the app looks like:

![](./image.png)

More about this in Chapter 8.

Read the [deployment.yaml manifest](../manifests/deployment.yaml) to know more. To test the changes:

```shell
curl -L https://127.0.0.1:8443 --insecure
# OR
curl -Lk https://127.0.0.1:8443
# ^^^short for `--insecure`` flag is `-k` flag

Kiada version 0.1.0
Request processed by "kiada-74987687d8-k5b95"
Client IP: 127.0.0.1
```

> NOTE: If it does not work, try deleting the LoadBalancer Service and re-deploying.
> `cloud-provider-kind` doesn't reliably update the port mapping, if ports are added later.

>>We are using a local CLI tool [`cloud-provider-kind`](https://kind.sigs.k8s.io/docs/user/loadbalancer/) to provision the LoadBalancer in the `kind` cluster.