# Computer Networks Private Service Platform

A private LAN-based service platform demonstrating private DNS, reverse proxy/load balancing, HTTPS/TLS, HTTP caching, and packet-level network analysis.

## Project Status

Phase 1 implementation and evidence have been completed and tested on a 3-Mac private LAN.

## Architecture

| Machine | IP Address | Role |
|---|---|---|
| Mac 1 | 10.7.26.144 | DNS + Client |
| Mac 2 | 10.7.6.173 | Nginx + HTTPS/TLS + Load Balancer + Backend A |
| Mac 3 | 10.7.9.59 | Backend B + Client |

Subnet mask: `255.255.224.0`

Project domain names:

- `app.team1.test`
- `api.team1.test`

## Private DNS

Mac 1 runs dnsmasq.

```text
app.team1.test -> 10.7.6.173
api.team1.test -> 10.7.6.173
```

## Repository Structure

```
dns/            dnsmasq configuration (Mac 1)
nginx/          Nginx configuration (Mac 2)
backend-a/      Backend A Python server (Mac 2, port 3001)
backend-b/      Backend B Python server (Mac 3, port 3002)
tls/            TLS setup documentation
wireshark/      Wireshark packet analysis
docs/           Architecture, IP table, and demo evidence
evidence/       Screenshots and captures from live testing
```
