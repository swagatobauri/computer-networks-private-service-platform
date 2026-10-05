# Computer Networks Private Service Platform

A private LAN-based networking project demonstrating:

- Private DNS using dnsmasq
- `.test` domain resolution
- nginx reverse proxy and load balancing
- REST backends
- HTTPS/TLS
- HTTP caching
- Wireshark packet-level evidence

## Project Status

The repository is currently being prepared on the available Mac.

Backend B and additional machine-specific configuration will be added when the other Macs are available.

## Planned Architecture

| Machine | Role |
|---|---|
| Mac 1 | DNS + Client |
| Mac 2 | nginx + HTTPS + Load Balancer + Backend A |
| Mac 3 | Backend B + Client |

The final service names are:

- `app.team1.test`
- `api.team1.test`

## Services

### Backend A

Backend A provides:

- `GET /`
- `GET /api/status`

Expected response header:

```text
X-Backend: A
