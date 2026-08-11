# Exetending Kiada FastAPI app using Envoy Proxy

Adding TLS support to the app so that it can also serve clients over HTTPS.

Even the FastAPI app can be configured to do so, but an easier option is to add a reverse proxy (like Envoy) in front of the app that can receive HTTPS requests on behalf of the application.

Also I am doing this to try running multiple containers in a pod.

So the new architecture of the app looks like:

![](./image.png)

More about this in Chapter 8.