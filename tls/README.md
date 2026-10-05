# TLS / HTTPS Configuration — Phase 1

This document describes the TLS setup used for the Phase 1 private service platform.

---

## Certificate Overview

A self-signed X.509 certificate was generated on Mac 2 for the project domains. The certificate is used by Nginx for TLS termination on port 443.

| Field | Value |
|---|---|
| Subject Common Name | `app.team1.test` |
| Subject Alternative Names (SANs) | `app.team1.test`, `api.team1.test` |
| Issuer | Self-signed (same as Subject) |
| Key type | RSA |
| Validity | Set at generation time — confirm with `openssl x509 -noout -dates` |

> **Important:** The exact validity period and serial number depend on when the certificate was generated on Mac 2. Use the verification commands below to view live certificate details.

---

## Certificate and Key File Paths (Mac 2)

The certificate and private key are stored locally on Mac 2 and are **not committed to this repository**.

| File | Path on Mac 2 |
|---|---|
| Certificate | `/opt/homebrew/etc/nginx/certs/server.crt` |
| Private key | `/opt/homebrew/etc/nginx/certs/server.key` |

> ⚠️ **Never commit the private key (`server.key`) to this repository.**  
> It is intentionally excluded from git tracking.

---

## Nginx TLS Configuration

The relevant section of `nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl;
    server_name app.team1.test api.team1.test;

    ssl_certificate     /opt/homebrew/etc/nginx/certs/server.crt;
    ssl_certificate_key /opt/homebrew/etc/nginx/certs/server.key;

    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://backend_pool;
        ...
    }
}
```

HTTP on port 80 redirects to HTTPS:

```nginx
server {
    listen 80;
    server_name app.team1.test api.team1.test;
    return 301 https://$host$request_uri;
}
```

---

## Trust Configuration

Because the certificate is self-signed, clients must explicitly trust it. On macOS:

1. Export the certificate from Mac 2: `/opt/homebrew/etc/nginx/certs/server.crt`
2. Double-click the `.crt` file in Finder to add it to the macOS Keychain.
3. In Keychain Access → find the certificate → Get Info → Trust → set **"Always Trust"** for SSL.

Once trusted, `curl` and browsers will connect without the `-k` (insecure) flag.

---

## Verification Commands

Run these on any LAN machine that has the certificate trusted and DNS pointing to `10.7.6.173`.

**View certificate details:**
```bash
openssl s_client -connect 10.7.6.173:443 -servername app.team1.test < /dev/null
```

**View certificate dates:**
```bash
echo | openssl s_client -connect 10.7.6.173:443 -servername app.team1.test 2>/dev/null \
  | openssl x509 -noout -subject -dates
```

**HTTPS request without -k (requires certificate trusted in OS):**
```bash
curl -i https://app.team1.test/
```

**HTTPS request with explicit resolve (bypasses DNS, useful from any machine):**
```bash
curl -i --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/
```

**Verify TLS protocol version:**
```bash
openssl s_client -connect 10.7.6.173:443 -tls1_3 -servername app.team1.test < /dev/null
```

---

## What Was Verified

During Phase 1 testing:

- `curl -i --resolve app.team1.test:443:10.7.6.173 https://app.team1.test/` returned `HTTP/1.1 200 OK` served by `nginx/1.31.6`.
- The Wireshark capture (`evidence/wireshark/`) shows a complete TLS handshake: Client Hello with SNI `app.team1.test`, Server Hello, Change Cipher Spec, and encrypted Application Data. No plaintext application content is visible in the capture, confirming encryption is active.
- TLS versions configured: `TLSv1.2` and `TLSv1.3`.
