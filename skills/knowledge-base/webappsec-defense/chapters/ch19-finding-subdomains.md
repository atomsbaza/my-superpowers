# Chapter 19: Finding Subdomains

## Core Idea
Behind-the-scenes subdomains (mail, admin, dev, internal) receive far less scrutiny than the public-facing app and are a high-value recon target; because no single discovery technique is comprehensive, effective subdomain recon layers manual, public-record, and automated (dictionary-before-brute-force) methods.

## Frameworks Introduced
- **Layered subdomain discovery**: No single technique finds all subdomains, so combine manual browsing, public records (search engines, archives, social APIs), zone transfer attempts, and dictionary/brute-force scans, escalating in effort/risk.
  - When to use: Any time mapping an application's full domain footprint during recon.
  - How: Start with the browser's Network tab (free, zero-risk); move to public records (Google dorking, archive.org, social media APIs — still low-risk); attempt a zone transfer (near-zero effort, occasionally very high payoff); only then fall back to dictionary attacks, and brute force as an absolute last resort.
- **Dictionary-over-brute-force preference**: Prefer a curated wordlist of known-common subdomain names over generating every possible character combination.
  - When to use: Whenever a subdomain wordlist (e.g., dnscan's list) is available, which is nearly always.
  - How: Stream the dictionary file and resolve each candidate asynchronously; only fall back to full brute force if the dictionary yields insufficient results, since brute force is slower and far more likely to trigger rate-limiting, logging, or IP bans.

## Key Concepts
- **Zone transfer attack**: A DNS technique that impersonates an authorized secondary DNS server to request a full zone file from a misconfigured primary server, potentially revealing every subdomain and internal IP in one request.
- **Google dorking (`site:` / `-inurl:`)**: Using search-engine operators to scope a search to one domain and exclude known subdomains/keywords, surfacing subdomains not otherwise obvious.
- **Archive.org historical recon**: Public web archives preserve old snapshots of a site's HTML/JS, which can reveal subdomains that were once linked but have since been removed from the live app.
- **Async DNS resolution (`dns.resolve` vs. `dns.lookup`)**: In Node.js, `dns.resolve` is genuinely asynchronous, while `dns.lookup` appears async in JavaScript but relies on the OS's synchronous `getaddrinfo(3)` under the hood — a critical distinction for building a performant bulk scanner.
- **Solutions space (subdomain generation)**: The character set and length used to generate brute-force candidates; narrowing this space (fewer characters, shorter length, known patterns) is the main lever for making brute force tractable.
- **X (Twitter) search/streaming/firehose APIs**: Three tiers of social-media data access useful for finding subdomains mentioned in marketing, hiring, or support links; each trades cost against completeness (search API = cheap but rate-limited; firehose = expensive but guarantees 100% match delivery).

## Mental Models
- Think of subdomain discovery as an escalating-risk ladder: free/passive techniques (browser tab, search engines, archives) first, active-but-cheap techniques (zone transfer) next, and noisy/detectable techniques (brute force) only as a last resort.
- Use "behind-the-scenes = less scrutinized" as your prioritization heuristic: a consumer-facing domain under an active bug bounty gets fixed fast; a forgotten `internal.` or `dev.` subdomain does not.
- Treat DNS zone transfer attempts as a "free lottery ticket" — one line of Bash, near-zero cost, occasionally an outright win against a misconfigured server.

## Anti-patterns
- **Brute force as the first resort**: Extremely noisy, easily logged, and likely to trigger IP bans or legal exposure — always exhaust dictionary and passive techniques first.
- **Synchronous `dns.lookup()` for bulk scanning**: Silently serializes what looks like async code, because the underlying OS call is synchronous — use `dns.resolve()` for genuine concurrency at scale.
- **Treating one technique as sufficient**: No single method (browser tab, search engine, zone transfer, dictionary) reliably finds every subdomain; comprehensive mapping requires combining several.

## Code Examples
```javascript
// Async DNS dictionary attack against a target domain, streaming
// a large subdomain wordlist from disk rather than loading it all
// into memory.
const dns = require('dns');
const csv = require('csv-parser');
const fs = require('fs');
const promises = [];

fs.createReadStream('subdomains-10000.txt')
  .pipe(csv())
  .on('data', (subdomain) => {
    promises.push(
      new Promise((resolve, reject) => {
        dns.resolve(`${subdomain}.mega-bank.com`, function (err, ip) {
          return resolve({ subdomain: subdomain, ip: ip });
        });
      }));
  })
  .on('end', () => {
    Promise.all(promises).then(function (results) {
      results.forEach((result) => {
        if (!!result.ip) { console.log(result); }
      });
    });
  });
```
- **What it demonstrates**: A production-shape dictionary attack — streamed input (memory-safe for large wordlists), fully async DNS resolution via `dns.resolve`, and `Promise.all` to wait for every candidate before reporting live subdomains.

```bash
# Zone transfer attack against a misconfigured DNS server
host -t mega-bank.com
# -> mega-bank.com name server ns1.bankhost.com
# -> mega-bank.com name server ns2.bankhost.com

host -l mega-bank.com ns1.bankhost.com
# If misconfigured, returns the full zone file:
# mail.mega-bank.com has address 82.31.105.140
# admin.mega-bank.com has address 32.45.105.144
# internal.mega-bank.com has address 25.44.105.144
```
- **What it demonstrates**: A two-command zone transfer attempt — first find the domain's nameservers, then request a zone transfer from one of them; a properly configured server returns "Transfer Failed," but a misconfigured one hands over every subdomain and internal IP.

## Reference Tables
dnscan's top-25 most common subdomains (from a dataset of 86,000+ DNS zone records), used to seed dictionary attacks:

| www | ns1 | m | www2 |
|---|---|---|---|
| mail | webdisk | imap | admin |
| ftp | ns2 | test | forum |
| localhost | cpanel | ns | news |
| webmail | whm | blog | |
| smtp | autodiscover | pop3 | |
| pop | autoconfig | dev | |

## Worked Example
The chapter's running MegaBank scenario walks through the full escalation ladder:

1. **Scope check**: `mega-bank.com` (the public app) already has an active bug bounty program, so easy vulnerabilities there are likely already fixed or reported — the tester looks for less-scrutinized subdomains instead.
2. **Browser Network tab**: Walking through the public app's UI surfaces a few low-hanging API endpoints, but nothing behind-the-scenes.
3. **Google dorking**: `site:mega-bank.com -inurl:www -inurl:mobile` filters out known subdomains, surfacing anything left over (demonstrated against Reddit: `site:reddit.com -inurl:www` surfaces `code.reddit.com`, an old public archive).
4. **Archive.org**: Viewing historical HTML source of old snapshots and grepping for `http://`, `https://`, `ftp://` reveals hyperlinks to subdomains no longer linked from the live site.
5. **Zone transfer**: `host -t mega-bank.com` finds nameservers `ns1.bankhost.com`/`ns2.bankhost.com`; `host -l mega-bank.com ns1.bankhost.com` succeeds (misconfigured server), revealing `mail.`, `admin.`, and `internal.mega-bank.com` along with their IPs in one shot.
6. **Dictionary fallback**: Had the zone transfer failed, the tester would stream dnscan's 10,000-entry wordlist through the async `dns.resolve` script above, discovering the same `admin`/`mail`/`dev`/`test` subdomains at much lower risk and effort than full brute force.
7. **Outcome**: The tester now has a working list of behind-the-scenes subdomains (`admin.mega-bank.com`, `internal.mega-bank.com`) to add to the recon map and prioritize over the already-hardened public `www` app.

## Key Takeaways
1. Behind-the-scenes subdomains (mail, admin, dev, internal) are consistently under-scrutinized compared to public-facing domains — prioritize them.
2. Always try a zone transfer attempt (`host -t` then `host -l`) — it costs one line of Bash and occasionally hands over the entire subdomain list at once.
3. Prefer dictionary attacks over brute force; only escalate to brute force if the dictionary is insufficient, given the higher detection/ban risk.
4. Use `dns.resolve()`, not `dns.lookup()`, for genuinely concurrent async DNS scanning in Node.js.
5. Public records (search engine caches, archive.org, social media APIs) can reveal subdomains that are no longer live-linked but were once exposed.
6. Stream large wordlists from disk rather than loading them fully into memory when scanning at scale.

## Connects To
- **Ch18 (global)**: Builds directly on the client/server/database architecture model — subdomains are how that multi-application structure is physically distributed across servers.
- **Ch20 (global)**: Once subdomains are found, API Analysis is the very next recon step — each subdomain likely hosts its own unique set of API endpoints.
- **Ch24-34 (Offense, global)**: Discovered "behind-the-scenes" subdomains (admin panels, internal tools) become prime targets for the offensive techniques covered later.
- **DNS protocol (external concept)**: Zone transfers and nameserver resolution are standard DNS administration concepts this chapter repurposes for offensive recon.
