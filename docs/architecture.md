# Private Service Platform — Architecture

## 1. Project Overview

This project implements a private LAN service platform using a 3-Mac architecture.

The system provides:
- Private DNS using dnsmasq
- Two HTTP backend services
- Nginx reverse proxy and load balancing
- HTTPS/TLS termination
- HTTP caching using Cache-Control and ETag
- Wireshark-based DNS, TCP and TLS packet analysis
- Backend failure/resilience testing

All services operate on the private LAN and use the `.test` namespace.

---

## 2. Network Topology

```text
                         Private LAN
                              |
          +-------------------+-------------------+
          |                   |                   |
       Mac 1               Mac 2               Mac 3
       DNS + Client        Nginx + TLS          Backend B
       10.7.26.144         10.7.6.173           10.7.9.59
          |                   |                   |
          |              +----+----+              |
          |              |         |              |
          |           Backend A   HTTPS           |
          |           :3001       :443            |
          |                       :80             |
          |                                      :3002
          +--------------------------------------+
