# IP and Service Table

## Current Network Information

| Machine | Role | IP Address | Status |
|---|---|---|---|
| Mac 1 | DNS + Client | `10.7.26.144` | Available |
| Mac 2 | nginx + HTTPS + Load Balancer + Backend A | To be confirmed | Not currently available |
| Mac 3 | Backend B + Client | To be confirmed | Not currently available |

## Planned Services

| Service | Address / Port |
|---|---|
| Application | `app.team1.test` |
| API | `api.team1.test` |
| DNS | UDP/TCP `53` |
| HTTP | TCP `80` |
| HTTPS | TCP `443` |
| Backend A | TCP `3001` |
| Backend B | TCP `3002` |

## DNS Mapping

Mac 1 will provide DNS resolution for:

```text
app.team1.test -> Mac 2
api.team1.test -> Mac 2
