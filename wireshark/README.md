# Wireshark Packet Analysis — Phase 1

This document describes the network captures taken during Phase 1 testing and explains what each capture proves.

All captures were taken on the private LAN using the following address space:

| Machine | IP | Role |
|---|---|---|
| Mac 1 | `10.7.26.144` | DNS server + client |
| Mac 2 | `10.7.6.173` | Nginx + TLS + Backend A |
| Mac 3 | `10.7.9.59` | Backend B |

---

## Capture 1 — DNS Query and Response

**File:** `evidence/dns/Screenshot 2026-10-05 at 3.09.45 PM.png`  
**Wireshark filter used:** `dns`  
**Capture interface:** Loopback (`lo0`) on Mac 1

### What the capture shows

The capture displays packet 1034, which is a **DNS response** from the local dnsmasq resolver:

| Field | Value |
|---|---|
| Source IP | `10.7.26.144` (Mac 1 — dnsmasq) |
| Destination IP | `10.7.26.144` (Mac 1 — local client) |
| Source port | UDP/53 (DNS) |
| Destination port | UDP/50840 (client ephemeral port) |
| Transaction ID | `0x814c` |
| Query type | A (IPv4 Host Address) |
| Query name | `app.team1.test` |
| Answer | `app.team1.test` → `10.7.6.173` |
| TTL | 30 seconds |
| Answer RRs | 1 |
| Flags | `0x8580` — Standard query response, No error |

### What this proves

- The private DNS server (dnsmasq on Mac 1) correctly resolves `app.team1.test` to `10.7.6.173` (Mac 2).
- The `.test` namespace is correctly handled without leaking queries to the public internet.
- The configured TTL of 30 seconds (matching `local-ttl=30` in `dns/dnsmasq.conf`) is present in the response.
- The response flag `No error` confirms the resolution succeeded.

---

## Capture 2 — TCP 3-Way Handshake and TLS Handshake

**File:** `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.39.47.jpeg`  
**Wireshark filter used:** `tcp.port == 443 && tcp.port == 57640`  
**Capture interface:** LAN interface (Wi-Fi), file `wireshark-WiFiXD7YW3.pcapng`

### TCP 3-Way Handshake

Packets 4273–4278 show the TCP connection establishment between Mac 1 (client) and Mac 2 (Nginx):

| Packet | Direction | Flags | Description |
|---|---|---|---|
| 4273 | `10.7.26.144:57640` → `10.7.6.173:443` | SYN, ECE, CWR | Client initiates connection |
| 4275 | `10.7.6.173:443` → `10.7.26.144:57640` | SYN, ACK, ECE | Server acknowledges |
| 4278 | `10.7.26.144:57640` → `10.7.6.173:443` | ACK | Client completes handshake |

- **Src Port:** `57640` (client ephemeral)
- **Dst Port:** `443` (HTTPS on Mac 2 Nginx)
- **Seq/Ack numbers** confirm proper TCP state machine progression.

### TLS Handshake

Immediately after the TCP handshake, TLS begins:

| Packet | Direction | Content |
|---|---|---|
| 4279 | `10.7.26.144` → `10.7.6.173` | **TLS Client Hello** — `SNI=app.team1.test` |
| 4282 | `10.7.6.173` → `10.7.26.144` | **Server Hello, Change Cipher Spec, Application Data** |
| 4283 | `10.7.6.173` → `10.7.26.144` | Application Data, Application Data |

Subsequent packets (4312 onward) show **TLS Application Data** frames carrying the encrypted HTTP traffic.

### What this proves

- The full TCP 3-way handshake (`SYN → SYN-ACK → ACK`) is present and correct.
- The client sends a TLS **Client Hello** containing SNI `app.team1.test`, proving TLS is initiated to the correct virtual host.
- The server responds with **Server Hello** and immediately follows with **Change Cipher Spec**, transitioning to encrypted communication.
- All subsequent application-layer data is classified as **Application Data** (i.e., opaque encrypted payloads) — confirming TLS encryption is in effect and HTTP request/response bodies are not exposed in plaintext.

---

## Capture 3 — TLS SNI Detail and Application Data

**File:** `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.44.40.jpeg`  
**Wireshark filter used:** `tcp.port == 57640 && tls`

### What the capture shows

This capture isolates TLS-only packets on connection `57640 ↔ 443`, providing a cleaner view of the TLS handshake:

| Packet | Source | Destination | Content |
|---|---|---|---|
| 4279 | `10.7.26.144` | `10.7.6.173` | Client Hello (`SNI=app.team1.test`) |
| 4282 | `10.7.6.173` | `10.7.26.144` | Server Hello, Change Cipher Spec, Application Data |
| 4283 | `10.7.6.173` | `10.7.26.144` | Application Data, Application Data |
| 4312 | `10.7.26.144` | `10.7.6.173` | Change Cipher Spec |
| 4313–4321 | both directions | both directions | Application Data |

The packet bytes panel (bottom-right) shows the raw TLS Client Hello frame. The ASCII column reveals the SNI string: `app.team1.test`, and the ALPN value `h2` / `http/1.1` visible at offset `0x180`.

### What this proves

- The TLS SNI field is explicitly set to `app.team1.test` in the Client Hello — confirming the client correctly targets the virtual host.
- ALPN negotiation (`h2`, `http/1.1`) is present in the Client Hello.
- Following the handshake, all application traffic is encrypted (Application Data frames only) — HTTP headers and body are not visible in the capture.
- This directly confirms the TLS termination is functioning correctly at Nginx on Mac 2.

---

## Summary Table

| Requirement | Captured? | Evidence File |
|---|---|---|
| DNS query for `app.team1.test` | ✅ Yes | `evidence/dns/Screenshot 2026-10-05 at 3.09.45 PM.png` |
| DNS response → `10.7.6.173` | ✅ Yes | `evidence/dns/Screenshot 2026-10-05 at 3.09.45 PM.png` |
| TCP SYN (client → server port 443) | ✅ Yes | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.39.47.jpeg` |
| TCP SYN-ACK (server → client) | ✅ Yes | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.39.47.jpeg` |
| TCP ACK (client completes handshake) | ✅ Yes | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.39.47.jpeg` |
| TLS Client Hello with SNI `app.team1.test` | ✅ Yes | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.44.40.jpeg` |
| TLS Server Hello + Change Cipher Spec | ✅ Yes | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.44.40.jpeg` |
| Encrypted Application Data (no plaintext) | ✅ Yes | `evidence/wireshark/WhatsApp Image 2026-10-05 at 15.39.47.jpeg` |
