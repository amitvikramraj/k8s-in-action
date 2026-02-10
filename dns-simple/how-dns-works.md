# How DNS Works?

> *Notes from the comic [howdns.works](https://howdns.works/) by [DNS Simple](https://dnsimple.com/comics)*

> *ref: [Cloudflare's DNS Blog](https://www.cloudflare.com/en-gb/learning/dns/what-is-dns/) – More detailed explanation of DNS*

## What is DNS?

* Computers and other devices communicate using IP addresses to identify each other on the internet.

* But IP addresses are hard to remember – so we use human readable names of websites like dnsimple.com

* DNS(Domain Name System) maps the website name to its IP address.

**What happens when you make a request in your browser?**

* User opens a browser and types a domain (eg: dnsimple.com)

* Browser and OS first checks their local cache to see if they have the IP addr. for this domain.

* If not, the OS asks a **DNS Resolver** to find it.

* DNS Resolver is the server that begins the lookup process

## DNS Resolver

* DNS Resolver first checks it's cache to see if it has the IP addr. for the domain

* If not, it starts by asking the **"Root Server."**

* The resolver server is usually your ISP(Internet Service Provider) that knows where to locate the root server.

* The root server know where to locate the `.COM` TLD Server (Top-Level Domain).

## Top of the Heirarchy

* The root server gives the location of `.COM` TLD server which the resolver stores in its cache for future use.

* This root server is just one of the 13 root name servers that exist today which are scattered around the globe and operated by 12 independent organisations.
  
  * Root servers sit at the top of the DNS Hierarchy

    ```mermaid
    graph TB
        Root["Root Server (.)"] --> COM[".com"]
        Root --> ORG[".org"]
        Root --> NET[".net"]
        Root --> EDU[".edu"]
        Root --> Other["... other TLDs"]

        COM --> D1["dnsimple.com"]
        COM --> D2["other-domains.com"]
        ORG --> D3["example.org"]
        NET --> D4["example.net"]
    ```

  * These root servers are named as `[letter].root-server.net` where `[letter]` ranges from A to M.
  
  * This doesn't mean that we have only 13 physical servers to support the whole internet!
  
  * Each organisation provides multiple physical servers distributed around the globe.


## TLDs: .HOT .PIZZA .COM

* Once the resolver gets the address of the TLD domain, it queries the `.COM` TLD server for `dnsimple.com`.

* TLD server doesn’t know the IP itself, but knows the **authoritative name servers** for the domain (`ns1.dnsimple.com`, `ns2.dnsimple.com`, etc.).
  * **Authoritative Name Servers (NS)**: Servers that have the actual DNS records for a domain.

* Resolver stores the list of name servers and continues.

* **

* The coordination of most top-level domains (TLDs) belong to the Internet Corporation for Assigned Names and Numbers (ICANN)
* The .COM TLD was one of the first created in 1985.
* Other type of TLDs include:
  * country code TLDs(like .jp, .in, etc),
  * international country code TLDs (.ykp)
  * Generic TLDs: .net, .org, .edu, etc
  * Infrastructure TLDs: .ARPA, mostly used for reverse DNS lookups.
    * Given the IP address it looks up the assosiated domain

## Respect my authority!

* A domain’s **registrar** tells the TLD registry which name servers are authoritative when the domain is registered.
    * **Registrar**: Service where you purchase your domain.

    * **TLD Registry**: Organization that manages all domains under a TLD (e.g., .COM).

* Resolver contacts one of the authoritative name servers for `dnsimple.com` and gives it the IP address of that domain.

* Multiple authoritative servers exist for distribution & redundancy.

<details>
<summary>Example of <code>WHOIS</code> lookup for <code>dnsimple.com</code></summary>

```shell
╭─amit@mac ~
╰─$ whois dnsimple.com
% IANA WHOIS server
% for more information on IANA, visit http://www.iana.org
% This query returned 1 object

refer:        whois.verisign-grs.com

domain:       COM

organisation: VeriSign Global Registry Services
address:      12061 Bluemont Way
address:      Reston VA 20190
address:      United States of America (the)

contact:      administrative
name:         Registry Customer Service
organisation: VeriSign Global Registry Services
address:      12061 Bluemont Way
address:      Reston VA 20190
address:      United States of America (the)
phone:        +1 703 925-6999
fax-no:       +1 703 948 3978
e-mail:       info@verisign-grs.com

contact:      technical
name:         Registry Customer Service
organisation: VeriSign Global Registry Services
address:      12061 Bluemont Way
address:      Reston VA 20190
address:      United States of America (the)
phone:        +1 703 925-6999
fax-no:       +1 703 948 3978
e-mail:       info@verisign-grs.com

nserver:      A.GTLD-SERVERS.NET 192.5.6.30 2001:503:a83e:0:0:0:2:30
nserver:      B.GTLD-SERVERS.NET 192.33.14.30 2001:503:231d:0:0:0:2:30
nserver:      C.GTLD-SERVERS.NET 192.26.92.30 2001:503:83eb:0:0:0:0:30
nserver:      D.GTLD-SERVERS.NET 192.31.80.30 2001:500:856e:0:0:0:0:30
nserver:      E.GTLD-SERVERS.NET 192.12.94.30 2001:502:1ca1:0:0:0:0:30
nserver:      F.GTLD-SERVERS.NET 192.35.51.30 2001:503:d414:0:0:0:0:30
nserver:      G.GTLD-SERVERS.NET 192.42.93.30 2001:503:eea3:0:0:0:0:30
nserver:      H.GTLD-SERVERS.NET 192.54.112.30 2001:502:8cc:0:0:0:0:30
nserver:      I.GTLD-SERVERS.NET 192.43.172.30 2001:503:39c1:0:0:0:0:30
nserver:      J.GTLD-SERVERS.NET 192.48.79.30 2001:502:7094:0:0:0:0:30
nserver:      K.GTLD-SERVERS.NET 192.52.178.30 2001:503:d2d:0:0:0:0:30
nserver:      L.GTLD-SERVERS.NET 192.41.162.30 2001:500:d937:0:0:0:0:30
nserver:      M.GTLD-SERVERS.NET 192.55.83.30 2001:501:b1f9:0:0:0:0:30
ds-rdata:     19718 13 2 8acbb0cd28f41250a80a491389424d341522d946b0da0c0291f2d3d771d7805a

whois:        whois.verisign-grs.com

status:       ACTIVE
remarks:      Registration information: http://www.verisigninc.com

created:      1985-01-01
changed:      2023-12-07
source:       IANA

# whois.verisign-grs.com

   Domain Name: DNSIMPLE.COM
   Registry Domain ID: 1591842594_DOMAIN_COM-VRSN
   Registrar WHOIS Server: whois.1api.net
   Registrar URL: http://www.1api.net
   Updated Date: 2025-11-23T10:43:28Z
   Creation Date: 2010-04-07T17:32:16Z
   Registry Expiry Date: 2029-04-07T17:32:16Z
   Registrar: 1API GmbH
   Registrar IANA ID: 1387
   Registrar Abuse Contact Email: abuse@1api.net
   Registrar Abuse Contact Phone: +49.68949396850
   Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
   Name Server: NS1.DNSIMPLE.COM
   Name Server: NS2.DNSIMPLE-EDGE.NET
   Name Server: NS3.DNSIMPLE.COM
   Name Server: NS4.DNSIMPLE-EDGE.ORG
   DNSSEC: unsigned
   URL of the ICANN Whois Inaccuracy Complaint Form: https://www.icann.org/wicf/
>>> Last update of whois database: 2026-02-10T01:54:52Z <<<

# whois.1api.net

Domain Name: dnsimple.com
Registry Domain ID: 1591842594_DOMAIN_COM-VRSN
Registrar WHOIS Server: whois.1api.net
Registrar URL: https://dnsimple.com
Updated Date: 2025-11-23T10:43:28Z
Creation Date: 2010-04-07T17:32:16Z
Registrar Registration Expiration Date: 2029-04-07T17:32:16Z
Registrar: 1API GmbH
Registrar IANA ID: 1387
Registrar Abuse Contact Email: abuse@1api.net
Registrar Abuse Contact Phone: +49.68949396850
Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
Registry Registrant ID: REDACTED FOR PRIVACY
Registrant Name: REDACTED FOR PRIVACY
Registrant Organization: REDACTED FOR PRIVACY
Registrant Street: REDACTED FOR PRIVACY
Registrant Street: REDACTED FOR PRIVACY
Registrant Street: REDACTED FOR PRIVACY
Registrant City: REDACTED FOR PRIVACY
Registrant State/Province: FL
Registrant Postal Code: REDACTED FOR PRIVACY
Registrant Country: US
Registrant Phone: REDACTED FOR PRIVACY
Registrant Phone Ext: REDACTED FOR PRIVACY
Registrant Fax: REDACTED FOR PRIVACY
Registrant Fax Ext: REDACTED FOR PRIVACY
Registrant Email: info@domain-contact.org
Registry Admin ID: REDACTED FOR PRIVACY
Admin Name: REDACTED FOR PRIVACY
Admin Organization: REDACTED FOR PRIVACY
Admin Street: REDACTED FOR PRIVACY
Admin Street: REDACTED FOR PRIVACY
Admin Street: REDACTED FOR PRIVACY
Admin City: REDACTED FOR PRIVACY
Admin State/Province: REDACTED FOR PRIVACY
Admin Postal Code: REDACTED FOR PRIVACY
Admin Country: REDACTED FOR PRIVACY
Admin Phone: REDACTED FOR PRIVACY
Admin Phone Ext: REDACTED FOR PRIVACY
Admin Fax: REDACTED FOR PRIVACY
Admin Fax Ext: REDACTED FOR PRIVACY
Admin Email: info@domain-contact.org
Registry Tech ID: REDACTED FOR PRIVACY
Tech Name: REDACTED FOR PRIVACY
Tech Organization: REDACTED FOR PRIVACY
Tech Street: REDACTED FOR PRIVACY
Tech Street: REDACTED FOR PRIVACY
Tech Street: REDACTED FOR PRIVACY
Tech City: REDACTED FOR PRIVACY
Tech State/Province: REDACTED FOR PRIVACY
Tech Postal Code: REDACTED FOR PRIVACY
Tech Country: REDACTED FOR PRIVACY
Tech Phone: REDACTED FOR PRIVACY
Tech Phone Ext: REDACTED FOR PRIVACY
Tech Fax: REDACTED FOR PRIVACY
Tech Fax Ext: REDACTED FOR PRIVACY
Tech Email: info@domain-contact.org
Registry Billing ID: REDACTED FOR PRIVACY
Billing Name: REDACTED FOR PRIVACY
Billing Organization: REDACTED FOR PRIVACY
Billing Street: REDACTED FOR PRIVACY
Billing Street: REDACTED FOR PRIVACY
Billing Street: REDACTED FOR PRIVACY
Billing City: REDACTED FOR PRIVACY
Billing State/Province: REDACTED FOR PRIVACY
Billing Postal Code: REDACTED FOR PRIVACY
Billing Country: REDACTED FOR PRIVACY
Billing Phone: REDACTED FOR PRIVACY
Billing Phone Ext: REDACTED FOR PRIVACY
Billing Fax: REDACTED FOR PRIVACY
Billing Fax Ext: REDACTED FOR PRIVACY
Billing Email: info@domain-contact.org
Name Server: ns1.dnsimple.com
Name Server: ns2.dnsimple-edge.net
Name Server: ns3.dnsimple.com
Name Server: ns4.dnsimple-edge.org
DNSSEC: unsigned
URL of the ICANN WHOIS Data Problem Reporting System: https://wdprs.internic.net/
>>> Last update of WHOIS database: 2026-02-10T01:55:06Z <<<
```

</details>


## It's Getting Late

* Resolver gets the IP address from the authoritative server (50.31.213.210).

* That final IP gets passed back to the OS/browser.

* Browser can now contact the web server and load the actual website.

* Resolver caches this response for faster future access.

DNS queries are typically recursive from the client’s perspective, even though the resolver may perform iterative steps through the hierarchy.


## Glue Records

How does the resolver finds `ns1.dnsimple.com` before `dnsimple.com`?

Since `ns1.dnsimple.com` is a subdomain of `dnsimple.com`, how could we resolve `ns1.dnsimple.com` without resolving `dnsimple.com` first?

* Sometimes the authoriative servers/name servers for a domain is a subdomain of the domain itself.
  * For example, `ns1.dnsimple.com` is a subdomain of `dnsimple.com`.
  * But `howdns.works` its name server looks like `V0N0.NIC.WORKS 2a01:8840:1a:0:0:0:0:6 65.22.24.6`

    <details>
        <summary>Example of <code>WHOIS</code> lookup for <code>howdns.works</code></summary>

    ```shell
    ╭─amit@mac ~
    ╰─$ whois howdns.works
    % IANA WHOIS server
    % for more information on IANA, visit http://www.iana.org
    % This query returned 1 object

    refer:

    domain:       WORKS

    organisation: Binky Moon, LLC
    address:      c/o Identity Digital Inc.
    address:      10500 NE 8th Street, Suite 750
    address:      Bellevue WA 98004
    address:      United States of America (the)

    contact:      administrative
    name:         Vice President, Engineering
    organisation: Identity Digital Inc.
    address:      10500 NE 8th Street, Suite 750
    address:      Bellevue WA 98004
    address:      United States of America (the)
    phone:        +1.425.298.2200
    fax-no:       +1.425.671.0020
    e-mail:       tldadmin@identity.digital

    contact:      technical
    name:         Senior Director, DNS Infrastructure Group
    organisation: Identity Digital Limited
    address:      c/o Identity Digital Inc.
    address:      10500 NE 8th Street, Suite 750
    address:      Bellevue WA 98004
    address:      United States of America (the)
    phone:        +1.425.298.2200
    fax-no:       +1.425.671.0020
    e-mail:       tldtech@identity.digital

    nserver:      V0N0.NIC.WORKS 2a01:8840:1a:0:0:0:0:6 65.22.24.6
    nserver:      V0N1.NIC.WORKS 2a01:8840:1b:0:0:0:0:6 65.22.25.6
    nserver:      V0N2.NIC.WORKS 2a01:8840:1c:0:0:0:0:6 65.22.26.6
    nserver:      V0N3.NIC.WORKS 161.232.12.6 2a01:8840:f6:0:0:0:0:6
    nserver:      V2N0.NIC.WORKS 2a01:8840:1d:0:0:0:0:6 65.22.27.6
    nserver:      V2N1.NIC.WORKS 161.232.13.6 2a01:8840:f7:0:0:0:0:6
    ds-rdata:     46672 8 2 0339dd99b86b96b8e437908e9aea3eb578fad0de211bd8cf7a4fe6885e0acdd2

    whois:

    status:       ACTIVE
    remarks:      Registration information: https://www.identity.digital/

    created:      2014-01-16
    changed:      2025-10-07
    source:       IANA
    ```

    </details>


* So if I want to browse `dnsimple.com`, the `.COM` TLD would tell me to get the IP address from the authoritative server: `ns1.dnsimple.com`

* But `ns1.dnsimple.com` is a subdomain of `dnsimple.com`, we cannot get to a subdomain without resolving the parent domain first. This causes a circular dependency.

* To solve this, we use **glue records**.

* When the resolver asked the .COM TLD about dnsimple.com, extra information was attached to that response.
  * The resolver got at least one IP address for each name server.
  * Eg. `ns1.dnsimple.com 50.31.213.210`

* Glue Records are extra IP information for name servers attached to the domain at the TLD level.

* So the resolver not only got the name of the authoritative name server, it also got the IP address breaking the circular dependency.