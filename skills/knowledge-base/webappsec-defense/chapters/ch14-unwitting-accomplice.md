# Chapter 14: Being an Unwitting Accomplice

## Core Idea
Web applications can be hijacked as launch pads to attack third parties (SSRF), send spam/phishing emails (email spoofing), or redirect victims to phishing sites (open redirects) — being a "good internet citizen" about outbound requests, emails, and redirects avoids both harming others and risking your own hosting provider shutting you down.

## Frameworks Introduced
- **Server-side domain restriction (anti-SSRF)**: outbound request domains must come from server-side code, never from client input; use vendor SDKs where available.
  - When to use: any server-side call to an external API (payments, maps, email, webhooks).
  - How: call vendor SDKs (e.g., Google Maps Java SDK) that construct the outbound request internally, so an attacker can never control which domain your server contacts.
- **URL validation pipeline (for unavoidable arbitrary-URL fetches)**: when a feature genuinely requires fetching arbitrary third-party URLs (e.g., link-preview generation), validate structurally before fetching.
  - When to use: link-sharing/preview features, webhook-target configuration, or any feature that must accept a user-supplied URL.
  - How: require HTTPS with a valid certificate, reject raw IP addresses in place of domains, reject nonstandard ports, gate the feature to authenticated users, rate-limit per user, and maintain (or subscribe to) a domain blocklist — while acknowledging DNS can still be pointed at internal IPs, so domain validation alone isn't airtight.
- **Email authentication trio (SPF + DKIM + DMARC)**: DNS-based mechanisms letting recipients verify that an email claiming to be from your domain is legitimate and untampered.
  - When to use: any domain that sends transactional or business email.
  - How: publish an SPF TXT record listing permitted sending IP ranges; sign outgoing emails with DKIM (public key in DNS, private key signs each message); publish a DMARC policy at `_dmarc.<domain>` dictating what happens to emails that fail SPF/DKIM.
- **Relative-path-only redirects + Referer validation (anti open-redirect)**: constrain redirect targets to your own site, or verify the originating page before redirecting externally.
  - When to use: any redirect target derived from a request parameter (e.g., post-login `next` URL) or any legitimate off-site redirect (e.g., interstitial warning pages).
  - How: only allow redirect targets that are relative paths starting with a single `/` (reject `//`-prefixed URLs, which browsers treat as protocol-agnostic absolute URLs); for legitimate off-site redirects, check that the `Referer` header matches your own domain before proceeding.

## Key Concepts
- **SSRF (server-side request forgery)**: an attacker tricks your server into making HTTP requests to arbitrary destinations of the attacker's choosing, using your server as a proxy.
- **DoS via SSRF**: an attacker uses your server's outbound-request capability (amplified if one attacker request triggers several server requests) to flood a victim, hiding behind your server's identity.
- **Internal network probing via SSRF**: an attacker uses your server's privileged network position (access to internal databases/caches not exposed to the internet) to discover and potentially compromise internal resources.
- **SPF (Sender Policy Framework)**: a DNS TXT record listing which IP ranges are authorized to send email on behalf of a domain.
- **DKIM (DomainKeys Identified Mail)**: email signing scheme where a public key in DNS lets recipients verify a message wasn't tampered with in transit.
- **DMARC (Domain-Based Message Authentication, Reporting and Conformance)**: a DNS policy record dictating what should happen to emails that fail SPF/DKIM checks.
- **Open-redirect vulnerability**: a site's redirect function accepts an arbitrary third-party destination, letting spammers "bounce" a link off a trusted domain to evade spam filters that check outbound link destinations.

## Mental Models
- Think of your server's outbound HTTP capability as a loaded gun handed to whoever controls the request — the domain being contacted must always be decided by your code, never by the client, or an attacker points that gun wherever they like.
- Treat a redirect feature the same way: it exists to serve your users' navigation, and any path by which an external party can redirect through your trusted domain turns that convenience into a phishing amplifier.
- Remember DNS is not a source of truth for "is this really an external, safe destination" — an attacker who controls DNS for a domain can point it at an internal IP, so domain-only validation isn't a complete SSRF defense.

## Anti-patterns
- **Client-controlled outbound domains**: the root cause of virtually all SSRF — if the domain in an outbound server request is ever taken directly from client input, it's exploitable.
- **Unauthenticated or unrate-limited arbitrary-URL fetches**: even with a legitimate feature need (link previews), lack of authentication/rate-limiting turns it into a free DoS/probing tool for anonymous attackers.
- **Naive domain validation**: checking only "is this a domain, not an IP" is insufficient since DNS can resolve a legitimate-looking domain to an internal IP.
- **`//`-prefixed redirect targets**: browsers interpret these as protocol-relative absolute URLs, so blocking only `http://`/`https://` prefixes while allowing `//evil.com` is an incomplete fix.
- **Blind trust in the `Referer` header**: it's spoofable by an attacker with full control of the request, though it's still a meaningful check in the open-redirect scenario where the attacker doesn't control the victim's browser request headers.

## Code Examples
```java
DirectionsResult result = DirectionsApi.newRequest(ctx)
    .mode(com.google.maps.model.TravelMode.BICYCLING)
    .avoid(RouteRestriction.HIGHWAYS, RouteRestriction.TOLLS, RouteRestriction.FERRIES)
    .region("au")
    .origin("Sydney")
    .destination("Melbourne")
    .await();
```
- **What it demonstrates**: using a vendor SDK (Google Maps) so the outbound request's domain is fixed by the SDK itself, never derived from client input.

```python
import requests
from urllib.parse import urlparse
from IPy import IP

def validate_url(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme != 'https':
        return False, "URL does not use HTTPS"
    if parsed_url.port and parsed_url.port != 443:
        return False, "URL does not use the standard HTTPS port"
    if not parsed_url.hostname:
        return False, "URL does not have a domain"
    try:
        IP(parsed_url.hostname)
        return False, "Host name must not be an IP address"
    except ValueError:
        pass
    try:
        response = requests.get(url, verify=True)
        return True, "Certificate is valid"
    except requests.exceptions.SSLError:
        return False, "URL has an invalid TLS certificate"
    except requests.exceptions.RequestException:
        return False, "URL could not be reached"
```
- **What it demonstrates**: a structural URL-validation pipeline (HTTPS-only, standard port, domain not IP, valid certificate) for features that must fetch arbitrary third-party URLs.

```python
import re
from flask import request, redirect

def is_relative(url):
    return url and re.match(r"^\/[^\/\\]", url)

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    if credentials_are_valid(username, password):
        session['user'] = username
        original_destination = request.args.get('next')
        if is_relative(original_destination):
            return redirect(original_destination)
    return redirect('/')
```
- **What it demonstrates**: restricting post-login redirects to single-leading-slash relative paths, rejecting both absolute URLs and `//`-prefixed protocol-relative URLs.

```python
from urlparse.parse import urlparse

@app.before_request
def check_referer():
    referer = request.headers.get('Referer')
    if not referer:
        return 'Missing referer. Access denied.', 403
    if urlparse(referer).netloc != 'yourdomain.com':
        return 'Invalid referer. Access denied.', 403
```
- **What it demonstrates**: validating the `Referer` header before permitting a redirect to an external interstitial page, to ensure the redirect was triggered from your own site.

## Reference Tables
| Attack | Your app's role | Primary mitigation |
|---|---|---|
| SSRF (DoS on victim) | Proxy amplifying attacker's requests | Server-side-only domains; rate limiting |
| SSRF (internal network probing) | Privileged vantage point into internal network | URL validation (HTTPS, domain not IP, standard ports); network segmentation |
| Email spoofing | Trusted domain impersonated in phishing | SPF, DKIM, DMARC |
| Open redirect | Trusted domain used to launder a phishing link past spam filters | Relative-path-only redirects; Referer check for legitimate off-site redirects |

| DNS record | Purpose |
|---|---|
| SPF (TXT) | Lists authorized sending IP ranges for the domain |
| DKIM (TXT, public key) | Lets recipients verify message signature/integrity |
| DMARC (TXT, `_dmarc.<domain>`) | Policy for what to do with emails failing SPF/DKIM |

## Worked Example
The chapter's open-redirect scenario: a site called `breddit.com` implements a redirect feature (e.g., post-login "return to where you were" or an outbound link tracker) that accepts a destination URL parameter without restricting it to the site's own domain. A spam emailer constructs a link like `https://breddit.com/redirect?url=https://burnttoast.com` and includes it in phishing emails. Because webmail spam filters check outbound link *domains* against blocklists, and `breddit.com` is a trusted, unlisted domain, the email sails past spam detection. The victim sees `breddit.com` in the link and clicks it, trusting the familiar domain — but is silently redirected to `burnttoast.com`, the actual malicious destination, potentially downloading malware or entering credentials on a phishing clone.

The fix combines both techniques from this chapter: restrict the redirect endpoint to accept only relative paths (single leading `/`, rejecting `//`-prefixed values), which eliminates the "arbitrary third-party bounce" capability entirely for ordinary navigation redirects; for any legitimate need to redirect off-site (e.g., an explicit "you are leaving our site" interstitial), require that the redirect only be reachable from a page on `breddit.com` itself, verified via the `Referer` header, so it can't be triggered directly by an externally crafted link.

## Key Takeaways
1. Never derive an outbound server-side request's domain from client input; use vendor SDKs to enforce this by construction.
2. If arbitrary-URL fetching is unavoidable, require authentication, rate-limit per user, and consider a CAPTCHA.
3. Validate fetched URLs structurally (HTTPS, valid cert, domain not IP, standard ports) — but remember DNS tricks can still route a validated domain to an internal IP.
4. Maintain (or subscribe to) a domain blocklist for SSRF-prone features like link sharing.
5. Implement SPF and DKIM so recipients can verify your domain's emails, and a DMARC policy to define what happens on failure.
6. Restrict all redirects to relative paths starting with a single `/`; explicitly reject `//`-prefixed protocol-relative URLs.
7. For legitimate off-site redirects, verify the `Referer` header points back to your own domain before proceeding.

## Connects To
- **Ch 11**: XXE-based external entity resolution (Ch 11) is itself a form of SSRF — same underlying vulnerability class, different entry point (XML parser vs. HTTP client feature).
- **Ch 15**: the Optus 2022 breach (referenced in both this chapter and Ch 15) illustrates how an unauthenticated API enumeration failure can cascade into a massive real-world incident.
- **Ch 10**: SSRF's "internal network probing" risk is compounded when internal services assume network-level trust instead of independently enforcing authorization.
