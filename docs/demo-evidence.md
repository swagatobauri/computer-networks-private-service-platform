# Phase 1 Demo Evidence Checklist

This document records the verification results for every Phase 1 requirement.

All tests were performed on the private LAN on **Mon, 05 Oct 2026**.

Network:

| Machine | IP | Role |
|---|---|---|
| Mac 1 | `10.7.26.144` | DNS server + client |
| Mac 2 | `10.7.6.173` | Nginx + TLS + Backend A |
| Mac 3 | `10.7.9.59` | Backend B |

---

## A. Private DNS

### A1 — DNS resolution: `app.team1.test`

| Field | Value |
|---|---|
| **Requirement** | `app.team1.test` resolves to `10.7.6.173` via private dnsmasq server on Mac 1 |
| **Verification command** | `dig app.team1.test @10.7.26.144` or captured via Wireshark |
| **Verified result** | DNS A-record response: `app.team1.test → 10.7.6.173`, TTL 30s, No error |
| **Evidence file** | `evidence/dns/Screenshot 2026-10-05 at 3.09.45 PM.png` |
| **Status** | ✅ VERIFIED |

### A2 — DNS resolution: `api.team1.test`

| Field | Value |
|---|---|
| **Requirement** | `api.team1.test` resolves to `10.7.6.173` via private dnsmasq server on Mac 1 |
| **Verification command** | `dig api.team1.test @10.7.26.144` |
| **Verified result** | Configured identically to `app.team1.test` in `dns/dnsmasq.conf` — same address `10.7.6.173`, TTL 30s |
| **Evidence file** | `dns/dnsmasq.conf` (configuration) |
| **Status** | ✅ CONFIGURED (same rule as A1) |

---

## B. HTTPS Connectivity

### B1 — HTTPS 200 OK response

| Field | Value |
|---|---|
| **Requirement** | HTTPS request to `app.team1.test` returns a successful response |
| **Verification command** | `curl -i --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/` |
| **Verified result** | `HTTP/1.1 200 OK`, `Server: nginx/1.31.6`, body `{"message": "Hello from Backend A", "backend": "A"}` |
| **Evidence file** | `evidence/http/Screenshot 2026-10-05 at 3.46.43 PM.png` |
| **Status** | ✅ VERIFIED |

---

## C. Backend Services

### C1 — Backend A response

| Field | Value |
|---|---|
| **Requirement** | Backend A (port 3001, Mac 2) is reachable and returns its identifier |
| **Verification command** | `curl -i --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/` |
| **Verified result** | Response header `X-Backend: A`, body `{"message": "Hello from Backend A", "backend": "A"}` |
| **Evidence file** | `evidence/http/Screenshot 2026-10-05 at 3.46.43 PM.png` |
| **Status** | ✅ VERIFIED |

### C2 — Backend B response

| Field | Value |
|---|---|
| **Requirement** | Backend B (port 3002, Mac 3) is reachable and returns its identifier |
| **Verification command** | Observed via repeated curl requests — load balancer routes to B |
| **Verified result** | Repeated requests produced alternating `X-Backend: A` and `X-Backend: B` responses, confirming Backend B is live and serving |
| **Evidence file** | Load balancing test (see C3 below) |
| **Status** | ✅ VERIFIED |

---

## D. Nginx Load Balancing

### C3 — Round-robin load balancing

| Field | Value |
|---|---|
| **Requirement** | Nginx distributes requests between Backend A and Backend B in round-robin |
| **Verification command** | `for i in $(seq 6); do curl -s --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/ \| python3 -c "import sys,json; print(json.load(sys.stdin)['backend'])"; done` |
| **Verified result** | Responses alternated: `A B A B A B` |
| **Evidence file** | Observed during Phase 1 testing |
| **Status** | ✅ VERIFIED |

---

## E. TLS

### E1 — TLS handshake and encryption

| Field | Value |
|---|---|
| **Requirement** | TLS is properly negotiated; traffic is encrypted |
| **Verification command** | Wireshark capture filtered on `tcp.port == 443 && tcp.port == 57640` |
| **Verified result** | Full TLS handshake visible: Client Hello (SNI=`app.team1.test`) → Server Hello → Change Cipher Spec → Application Data (encrypted) |
| **Evidence file** | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.39.47.jpeg` |
| **Status** | ✅ VERIFIED |

### E2 — TLS SNI: `app.team1.test`

| Field | Value |
|---|---|
| **Requirement** | Client sends correct SNI in TLS Client Hello |
| **Verification command** | Wireshark filtered on `tcp.port == 57640 && tls`, packet bytes inspection |
| **Verified result** | TLS Client Hello frame shows SNI value `app.team1.test` in the raw packet bytes |
| **Evidence file** | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.44.40.jpeg` |
| **Status** | ✅ VERIFIED |

---

## F. TCP Handshake

### F1 — TCP 3-way handshake

| Field | Value |
|---|---|
| **Requirement** | Standard TCP connection establishment to port 443 |
| **Verification command** | Wireshark capture filtered on `tcp.port == 443 && tcp.port == 57640` |
| **Verified result** | Packet 4273: SYN `10.7.26.144:57640 → 10.7.6.173:443`; Packet 4275: SYN-ACK; Packet 4278: ACK |
| **Evidence file** | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.39.47.jpeg` |
| **Status** | ✅ VERIFIED |

---

## G. DNS Packets

### G1 — DNS query and response captured in Wireshark

| Field | Value |
|---|---|
| **Requirement** | DNS query/response for project domain is visible in Wireshark |
| **Verification command** | Wireshark filter: `dns`, capturing on loopback (`lo0`) on Mac 1 |
| **Verified result** | DNS response packet shows: query `app.team1.test` type A, answer `10.7.6.173`, TTL 30, No error, Transaction ID `0x814c` |
| **Evidence file** | `evidence/dns/Screenshot 2026-10-05 at 3.09.45 PM.png` |
| **Status** | ✅ VERIFIED |

---

## H. HTTP Headers

### H1 — `X-Backend` header

| Field | Value |
|---|---|
| **Requirement** | Response identifies which backend served the request |
| **Verification command** | `curl -i --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/` |
| **Verified result** | `X-Backend: A` (or `B` on alternate requests) |
| **Evidence file** | `evidence/http/Screenshot 2026-10-05 at 3.46.43 PM.png` |
| **Status** | ✅ VERIFIED |

### H2 — `X-Edge` header

| Field | Value |
|---|---|
| **Requirement** | Response identifies the Nginx edge node |
| **Verification command** | `curl -i --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/` |
| **Verified result** | `X-Edge: Mac2-Nginx` |
| **Evidence file** | `evidence/http/Screenshot 2026-10-05 at 3.46.43 PM.png` |
| **Status** | ✅ VERIFIED |

---

## I. HTTP Caching

### I1 — `Cache-Control` header

| Field | Value |
|---|---|
| **Requirement** | Response includes a `Cache-Control` directive |
| **Verification command** | `curl -i --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/` |
| **Verified result** | `Cache-Control: public, max-age=60` |
| **Evidence file** | `evidence/http/Screenshot 2026-10-05 at 3.46.43 PM.png` |
| **Status** | ✅ VERIFIED |

### I2 — `ETag` header

| Field | Value |
|---|---|
| **Requirement** | Response includes an `ETag` for conditional request support |
| **Verification command** | `curl -i --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/` |
| **Verified result** | `ETag: "backend-a-v1"` |
| **Evidence file** | `evidence/http/Screenshot 2026-10-05 at 3.46.43 PM.png` |
| **Status** | ✅ VERIFIED |

### I3 — HTTP 304 Not Modified

| Field | Value |
|---|---|
| **Requirement** | Conditional `GET` with matching `If-None-Match` returns 304 without body |
| **Verification command** | `curl -i --resolve app.team1.test:443:10.7.6.173 -H 'If-None-Match: "backend-a-v1"' https://app.team1.test/` |
| **Verified result** | `HTTP/1.1 304 Not Modified` — no body; `Cache-Control: public, max-age=60`, `ETag: "backend-a-v1"`, `X-Backend: A`, `X-Edge: Mac2-Nginx` all present |
| **Evidence file** | `evidence/http/Screenshot 2026-10-05 at 3.49.31 PM.png` |
| **Status** | ✅ VERIFIED |

---

## Summary

| ID | Requirement | Status |
|---|---|---|
| A1 | DNS: `app.team1.test` → `10.7.6.173` | ✅ VERIFIED |
| A2 | DNS: `api.team1.test` → `10.7.6.173` | ✅ CONFIGURED |
| B1 | HTTPS 200 OK | ✅ VERIFIED |
| C1 | Backend A response | ✅ VERIFIED |
| C2 | Backend B response | ✅ VERIFIED |
| C3 | Round-robin load balancing (A B A B A B) | ✅ VERIFIED |
| E1 | TLS handshake and encryption | ✅ VERIFIED |
| E2 | TLS SNI: `app.team1.test` | ✅ VERIFIED |
| F1 | TCP 3-way handshake | ✅ VERIFIED |
| G1 | DNS packets in Wireshark | ✅ VERIFIED |
| H1 | `X-Backend` header | ✅ VERIFIED |
| H2 | `X-Edge` header | ✅ VERIFIED |
| I1 | `Cache-Control` header | ✅ VERIFIED |
| I2 | `ETag` header | ✅ VERIFIED |
| I3 | HTTP 304 Not Modified | ✅ VERIFIED |
