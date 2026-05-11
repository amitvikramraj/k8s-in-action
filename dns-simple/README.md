# Notes from DNS Simple Comics

1. [How HTTPS Works!](./how-https-works.md)
2. [How DNS Works](./how-dns-works.md)

## Journey of a Request

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser
    participant OSCache as Browser / OS Cache
    participant Resolver as DNS Resolver
    participant Root as Root Server
    participant TLD as .COM TLD Server
    participant AuthNS as Authoritative Name Server
    participant Server as Web Server
    participant CA as Certificate Authority / Root Store

    User->>Browser: Enter https://dnsimple.com
    Browser->>OSCache: Do we know the IP address?
    alt IP address is cached
        OSCache-->>Browser: Return cached IP address
    else IP address is not cached
        Browser->>Resolver: Resolve dnsimple.com
        Resolver->>Root: Where is .com?
        Root-->>Resolver: Ask the .COM TLD server
        Resolver->>TLD: Where is dnsimple.com?
        TLD-->>Resolver: Ask the authoritative name servers
        Resolver->>AuthNS: What is the IP for dnsimple.com?
        AuthNS-->>Resolver: Return DNS record with IP address
        Resolver-->>Browser: Return IP address and cache it
    end

    Browser->>Server: Open TCP connection to the IP address
    Browser->>Server: ClientHello with TLS versions, cipher suites, key-share, client random
    Server-->>Browser: ServerHello with chosen TLS version, cipher suite, key-share, certificate
    Browser->>CA: Validate certificate chain against trusted roots
    CA-->>Browser: Certificate is trusted
    Note over Browser,Server: Both sides generate matching session keys from the client random, server random, and shared secret derived from their key-shares
    Browser->>Server: Encrypted Finished message proving it has the session keys
    Server-->>Browser: Encrypted Finished message proving it has the session keys
    Note over Browser,Server: The secure TLS connection is now ready
    Browser->>Server: Encrypted HTTPS request
    Server-->>Browser: Encrypted HTTPS response
```

**TLS Handshake Clarifications:**

* The browser and server each create a temporary private/public key pair for this connection.

* The **key-share** is the public part of that temporary key pair.
  * Browser sends its public key-share to the server.
  * Server sends its public key-share to the browser.
  * Their private keys are never sent over the network.

* Both sides use Diffie-Hellman style math to generate the same **shared secret**:
  * Browser uses its private key + server's public key-share.
  * Server uses its private key + browser's public key-share.
  * An eavesdropper can see both public key-shares, but cannot calculate the shared secret without a private key.

* The **session keys** are generated from the shared secret plus handshake data like the client random, server random, and the handshake transcript.
  * The **handshake transcript** is the ordered record of the actual handshake messages exchanged so far, such as `ClientHello`, `ServerHello`, and the server certificate.
  * Including it ties the generated keys to this exact TLS negotiation and helps detect if any handshake message was changed.
  * Session keys are also never sent over the network.
  * They are symmetric keys, meaning both sides use matching keys to encrypt and decrypt the HTTPS traffic.

* The **Finished** messages prove both sides generated the same session keys.
  * The browser sends an encrypted/authenticated summary of the handshake.
  * The server verifies it using its own session keys.
  * Then the server does the same, and the browser verifies it.
  * If verification succeeds on both sides, the TLS connection is secure and ready for HTTPS.


## References

* [DNS Simple](https://dnsimple.com/comics)
* [**Cloudfare**](https://www.cloudflare.com/en-gb/learning/): The Cloudflare learning blogs are really good.
  * Learn about SSL
  * Learn about DNS
  * Other Blogs