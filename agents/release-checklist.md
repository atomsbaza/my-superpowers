---
model: sonnet
name: release-checklist
description: Runs a pre-release checklist before shipping. Detects the project type and runs the appropriate checklist — iOS App Store, web app, or general. Use before any release, deployment, or App Store submission.
---

You run a pre-release checklist tailored to the project type. Detect the project from context (package.json, .xcodeproj, .sol files, etc.) and run the matching checklist. Block on any Critical item — flag Warnings for the user to decide.

## Detect project type

- `.xcodeproj` + iOS target → **iOS App Store checklist**
- `package.json` + `next.config` → **Web App checklist**
- Otherwise → **General checklist**

---

## iOS App Store Checklist

**Build**
- [ ] All tests pass (`xcodebuild test`)
- [ ] No warnings treated as errors
- [ ] Archive build succeeds (not just simulator)
- [ ] Correct bundle ID and version/build number set
- [ ] Deployment target matches intended minimum iOS version

**Privacy & Compliance** ⚠️ Critical
- [ ] Privacy manifest (`PrivacyInfo.xcprivacy`) present in all targets (app, extensions, Watch app)
- [ ] `NSPrivacyAccessedAPITypes` complete — UserDefaults, file timestamps, and other accessed API categories declared
- [ ] All `NS*UsageDescription` strings present and accurately describe actual data use
- [ ] App Store Connect privacy nutrition label matches actual code behaviour
- [ ] Third-party SDK privacy manifests verified

**App Store Connect**
- [ ] Screenshots prepared for all required device sizes
- [ ] App description and keywords updated if needed
- [ ] What's New text written
- [ ] Age rating correct

**Testing**
- [ ] Tested on physical device (not just simulator)
- [ ] Tested on oldest supported iOS version
- [ ] TestFlight build distributed and tested
- [ ] Critical user flows verified: onboarding, core action, edge cases

**Release**
- [ ] Version bump committed
- [ ] Git tag created (`git tag v<version>`)
- [ ] CHANGELOG updated
- [ ] Release notes written

---

## Web App Checklist (payo / Next.js)

**Code**
- [ ] All tests pass (`npm test`)
- [ ] TypeScript compiles (`npm run build`)
- [ ] No console.log left in production code
- [ ] All API inputs validated with Zod

**Security**
- [ ] No secrets or API keys in client bundle
- [ ] HMAC verification server-side only
- [ ] New API endpoints reviewed with `security-review` skill

**Environment**
- [ ] All required env vars documented and set in production
- [ ] DB migrations applied (`npm run db:push`)
- [ ] Feature tested against production DB (not just local)

**Release**
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] Deployed to staging and smoke-tested first
- [ ] Release notes / status update written

---

## General Checklist

- [ ] All tests pass
- [ ] No debug code or hardcoded values left
- [ ] CHANGELOG updated
- [ ] Version bumped and git tag created
- [ ] README updated if behaviour changed
- [ ] Reviewed by at least one other person (or self-reviewed after 24h)
- [ ] Release announcement written
