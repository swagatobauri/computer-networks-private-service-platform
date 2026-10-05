# IP and Service Table

## Network Information

| Machine | Role | IP Address | Subnet Mask | Status |
|---|---|---|---|---|
| Mac 1 | DNS + Client | `10.7.26.144` | `255.255.224.0` | Active |
| Mac 2 | Nginx + HTTPS + Load Balancer + Backend A | `10.7.6.173` | `255.255.224.0` | Active |
| Mac 3 | Backend B + Client | `10.7.9.59` | `255.255.224.0` | Active |

## Services

| Service | Machine | Address / Port | Protocol |
|---|---|---|---|
| Private DNS | Mac 1 | `10.7.26.144:53` | UDP/TCP |
| HTTP (redirect to HTTPS) | Mac 2 | `10.7.6.173:80` | TCP |
| HTTPS / Nginx | Mac 2 | `10.7.6.173:443` | TCP |
| Backend A | Mac 2 | `10.7.6.173:3001` | TCP |
| Backend B | Mac 3 | `10.7.9.59:3002` | TCP |

## Domain Names

| Domain | Resolves to | Backend |
|---|---|---|
| `app.team1.test` | `10.7.6.173` | Nginx (round-robin → Backend A / Backend B) |
| `api.team1.test` | `10.7.6.173` | Nginx (round-robin → Backend A / Backend B) |

## DNS Mapping (dnsmasq on Mac 1)

```text
app.team1.test -> 10.7.6.173
api.team1.test -> 10.7.6.173
```
