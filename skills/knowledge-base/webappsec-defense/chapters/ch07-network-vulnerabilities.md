# Chapter 7: Network Vulnerabilities

## Core Idea
Between the browser and the server lie three distinct threat categories — traffic interception, misdirection (fake domains and DNS attacks), and credential/key theft — and pervasive HTTPS, DNS hygiene, and disciplined certificate/key management together neutralize almost all of them.

## Frameworks Introduced
- **Pervasive HTTPS as the MITM neutralizer**: Encrypting all traffic, not just "sensitive" pages, so no unencrypted segment exists for an attacker to intercept.
  - When to use: For 100% of traffic to your web server, unconditionally.
  - How: Redirect all HTTP to HTTPS at the server/load-balancer level, add HSTS so browsers stop even attempting HTTP after first contact, and enforce a minimum strong TLS version (1.3, per PCI guidance at time of writing) to close downgrade-attack windows.
- **DNS hygiene against misdirection**: Preventing dangling DNS entries and enabling DNS-layer authentication so attackers can't redirect users to malicious infrastructure.
  - When to use: Whenever provisioning or deprovisioning any subdomain or DNS record, and as an ongoing scan across your whole domain portfolio.
  - How: Delete subdomain DNS entries *before* deprovisioning the underlying resource (not after); periodically scan for dangling subdomains with tools like Amass/Sublist3r; enable DNSSEC on your domains where your registrar/host supports it.
- **Certificate lifecycle discipline (issue → monitor → revoke → reissue)**: Treating certificates as an actively-managed, revocable trust artifact rather than a set-and-forget deployment step.
  - When to use: Continuously — certificate transparency monitoring is ongoing, and revocation/reissuance must be ready to execute immediately upon any suspected compromise.
  - How: Avoid wildcard certificates (enumerate subdomains explicitly instead); monitor certificate transparency logs for rogue certificates issued against your domain; have a scripted (not manual) revoke-and-reissue process ready to run on short notice.
- **Least privilege for server access and key custody**: Minimizing who and what can reach your private encryption keys.
  - When to use: When provisioning server access, structuring your deployment topology, and setting filesystem permissions.
  - How: Time-box access keys and prefer automated processes over standing human access; separate web servers from application servers so a compromise of one doesn't expose the other's keys; restrict private-key directory permissions to the web server process only; never place private keys in a publicly-served directory.

## Key Concepts
- **Monster-in-the-middle (MITM) attack**: An adversary positioned between two communicating parties, intercepting and potentially reading or altering traffic between them.
- **ARP spoofing**: Flooding a local network with forged Address Resolution Protocol packets so traffic gets routed to the attacker's device instead of the legitimate gateway.
- **sslstrip / downgrade attack**: sslstrip rewrites HTTPS links to HTTP before the user notices, capturing credentials in transit; a downgrade attack more generally tricks a TLS handshake into negotiating a weaker, breakable cipher (e.g., the POODLE exploit).
- **Doppelganger domain / homograph attack**: A lookalike domain using typos, character substitution (0 for O), or non-ASCII homoglyphs (Cyrillic а for Latin a) to impersonate a trusted site; browsers mitigate the latter by rendering internationalized domains in Punycode.
- **DNS poisoning**: Corrupting a DNS cache (host file, ISP resolver, or root/authoritative server) to redirect a domain lookup to a malicious IP address.
- **DNSSEC**: A cryptographic extension to DNS letting servers sign their responses, allowing clients to detect poisoned/forged DNS answers.
- **Subdomain squatting / dangling subdomain**: A DNS entry pointing to a deprovisioned resource (e.g., an abandoned third-party service username) that an attacker claims to serve malicious content under your trusted domain.
- **Chain of trust / certificate revocation (CRL/OCSP)**: The hierarchy of certificate authorities vouching for each other down to your domain's certificate; CRL is a periodically-downloaded list of revoked certificates, OCSP is a real-time revocation-status query — browsers use both.
- **Certificate transparency**: A requirement that certificate authorities publish all issued certificates to public logs, letting domain owners detect rogue certificates issued in their name.

## Mental Models
- Think of HTTPS as closing the entire MITM attack surface at once: ARP spoofing, rogue Wi-Fi hotspots, and sslstrip all depend on some segment of traffic being unencrypted or downgradable — pervasive HTTPS + HSTS + a minimum TLS version removes all three attack vectors' shared precondition simultaneously.
- Treat DNS poisoning as insufficient on its own: even if an attacker redirects your users' DNS lookups, they still need either your real certificate or must present their own (triggering a browser warning) — so DNS attacks are "rarely used in isolation" and are usually paired with certificate compromise.
- Think of dangling subdomains as an inventory/lifecycle problem, not a technical vulnerability: the fix is procedural (delete-DNS-before-deprovision) and detective (periodic scanning), not a code change.
- Use the "web server has the certificate, application server doesn't need the private key" separation as a structural least-privilege boundary: co-locating them means a single command-injection bug anywhere in the application server can reach the encryption key.

## Anti-patterns
- **Serving "low-risk" content over HTTP**: The historical practice (exploited by sslstrip) of upgrading to HTTPS only at login; any unencrypted segment is an MITM opportunity, and even non-login browsing history (e.g., medical searches) has privacy value to an attacker.
- **Stale DNS entries for deprovisioned resources**: Directly enables subdomain squatting; the DNS entry must be deleted *before*, not after, decommissioning.
- **Wildcard certificates**: Cover every subdomain under one certificate, which is more convenient but less secure than explicitly enumerating subdomains — a compromise of the wildcard cert compromises everything under it.
- **Manual certificate reissuance**: Slow, error-prone recovery in exactly the moment (suspected compromise) when speed matters most; automate the revoke-and-reissue pipeline in advance.
- **Standing (non-expiring) server access keys**: Widens the window in which a stolen or leaked key grants an attacker ongoing access; time-box and prefer automated deployment processes over persistent human SSH access.
- **Co-located web and application servers**: A command injection vulnerability in the application server can then directly reach the encryption private key stored for the web server.
- **Private keys in publicly-served directories**: An easy, "fatally dangerous" mistake during deployment that exposes the key over the internet alongside static assets like JS/CSS/images.

## Code Examples
```
Strict-Transport-Security: max-age=31536000
```
- **What it demonstrates**: HSTS header instructing browsers to upgrade to HTTPS immediately (without waiting for a redirect) and to enforce this for a full year — the direct response to Moxie Marlinspike's sslstrip disclosure.

```
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;   # Redirects HTTP to HTTPS
}
server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate     /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;    # Certificate + paired private key
    add_header Strict-Transport-Security "max-age=31536000";
    ssl_protocols TLSv1.3;                            # Enforces minimum strong TLS version
}
```
- **What it demonstrates**: A complete NGINX configuration combining HTTP→HTTPS redirect, HSTS, and a minimum TLS version to close both the MITM and downgrade-attack vectors at once.

```javascript
// Scanning user-submitted comments for malicious/blocklisted domains before rendering as links
function convertUrlsToLinks(comment, blocklist) {
  comment = escapeHtml(comment);
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  return comment.replace(urlRegex, (match) => {
    const url = new URL(match);
    if (blocklist.includes(url.hostname)) {
      throw new Error(`Blocked domain found: ${url.hostname}`);
    }
    return `<a href="${url.href}">${url.href}</a>`;
  });
}
```
- **What it demonstrates**: Defending your own users against doppelganger-domain phishing links posted in user-generated content on your site.

```
Set-Cookie: session_id=273819272819191; domain=example.com
```
- **What it demonstrates**: The `domain` attribute controlling whether a cookie is readable across subdomains — omit it if subdomain cookie sharing isn't needed, to reduce the blast radius of a subdomain compromise (including a squatted one).

## Reference Tables
| Revocation-check mechanism | How it works | Timing |
|---|---|---|
| CRL (Certificate Revocation List) | Browser periodically downloads a list of revoked certificates from the CA and checks locally | Periodic (cached) |
| OCSP (Online Certificate Status Protocol) | Browser makes a real-time query to the CA's OCSP responder for a specific certificate's status | Real-time (per connection) |

| Attack category | Example techniques | Primary mitigation |
|---|---|---|
| Interception | ARP spoofing, rogue Wi-Fi hotspot, sslstrip, downgrade attacks (POODLE) | Pervasive HTTPS, HSTS, minimum TLS version |
| Misdirection | Doppelganger/homograph domains, DNS poisoning, subdomain squatting | Link blocklisting, DNSSEC, dangling-subdomain scans |
| Credential/key theft | Certificate compromise, stolen private keys | Certificate transparency monitoring, revocation, least-privilege key custody |

## Worked Example
A company runs `example.com` plus several subdomains, and undergoes a security review of its network-layer posture after a marketing team member mentions the company blog "moved off Medium a while back."

1. **Pervasive HTTPS audit**: The review confirms all traffic — not just the login and checkout flows — redirects HTTP→HTTPS via the NGINX config shown above, HSTS is set with a one-year `max-age`, and `ssl_protocols TLSv1.3` is enforced, closing off both classic MITM interception and downgrade attacks like POODLE in one pass.
2. **Dangling subdomain discovery**: Running Amass against `example.com`'s DNS records, the team finds `blog.example.com` still has a CNAME pointing at `example-blog.medium.com` — the account was abandoned when marketing discontinued their Medium presence, but nobody removed the DNS entry. This is a textbook dangling subdomain: an attacker could register `example-blog` as a new Medium username and serve content (including cookie-stealing scripts, if `blog.example.com` was ever granted cookie access via the `domain` attribute) under the company's trusted domain.
   - **Fix applied**: The team immediately removes the CNAME record, and separately checks whether `Set-Cookie: ...; domain=example.com` was ever set broadly enough to be readable by `blog.example.com` — it wasn't, since the main app's session cookie omits the `domain` attribute entirely, limiting exposure even during the window the dangling entry existed.
   - **Process fix**: They add a step to their resource-deprovisioning checklist: delete the DNS entry *before* the underlying resource (Medium account, in this case) is abandoned, not after — directly following the book's recommended ordering.
3. **Certificate posture**: The team discovers they're using a wildcard certificate (`*.example.com`) "for convenience." Given the dangling-subdomain incident just found, they decide to migrate to certificates enumerating specific subdomains explicitly, so that a future subdomain compromise doesn't automatically inherit trust for the entire domain space. They also enable certificate transparency log monitoring (a one-click feature in their DNS/CDN provider's dashboard) to catch any future rogue certificate issuance against `example.com`.
4. **Key custody review**: They confirm the web server (holding the TLS private key) and application server run on separate machines — so a hypothetical command injection vulnerability in the application layer (covered in a later chapter) cannot directly reach the private key. They also audit that no `.key` files live under the publicly-served static-assets directory, and that SSH access to the web server host is granted only via a time-boxed, automated deployment pipeline rather than standing developer credentials.
5. **User-facing misdirection defense**: Because the forum lets users post links in comments, the team adds the `convertUrlsToLinks` blocklist-checking function shown above to reject known-malicious/doppelganger domains before rendering them as clickable links, protecting their own users from being misdirected via content hosted on the company's own site.

## Key Takeaways
1. Encrypt all traffic via HTTPS unconditionally — MITM interception techniques (ARP spoofing, sslstrip) all depend on some segment being unencrypted or downgradable.
2. Pair HSTS with a minimum enforced TLS version (1.3 as of this writing) to close both the "first insecure request" window and downgrade attacks like POODLE.
3. Delete DNS entries *before* deprovisioning the underlying resource, and periodically scan for dangling subdomains — this is a lifecycle/process fix, not a code fix.
4. Enable DNSSEC where supported; it's low-risk to turn on since unsupporting browsers simply ignore it.
5. Avoid wildcard certificates in favor of explicitly enumerated subdomains, and monitor certificate transparency logs for rogue issuance.
6. Separate web and application servers so a compromise in one doesn't directly expose the other's private keys; never place private keys in publicly-served directories.
7. Time-box server access credentials and prefer automated deployment processes over standing human SSH access to reduce the key-theft attack surface.

## Connects To
- **Ch 2**: The `domain` attribute on cookies, only briefly flagged there, is fully explained here in the context of subdomain squatting and cross-subdomain cookie exposure.
- **Ch 3**: Directly builds on the certificate, TLS, and HTTPS fundamentals established in Encryption — this chapter is essentially "what goes wrong with those mechanisms and how to harden them."
- **Ch 12 (external)**: The private-key-theft-via-command-injection scenario (co-located servers) foreshadows the book's dedicated Injection Vulnerabilities chapter.
- **Ch 14 (external)**: The doppelganger-domain/spoofed-email mitigation (DKIM) mentioned here is covered fully in the book's later chapter on being an unwitting accomplice.
