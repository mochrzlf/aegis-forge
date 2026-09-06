# Security Policy

## 🛡️ Enterprise Vulnerability Disclosure Policy

Security and data privacy are the highest priorities within the **Aegis Forge** architecture. We welcome reports from security researchers, developers, and users to assist in maintaining the integrity of this repository and its derived applications.

---

## 📦 Supported Versions

Only the latest release on the primary branch actively receives security updates:

| Version | Actively Supported | Security Patch Status |
| :--- | :---: | :--- |
| **Main (Latest)** | ✅ Yes | Patches released immediately via PR & CI/CD |
| **< 1.0.0** | ❌ No | Please rebase to the latest release |

---

## 🚨 Reporting a Vulnerability

If you discover a potential security vulnerability or credential leak, **DO NOT** create a public GitHub issue. Please submit your report through one of the following confidential channels:

1. **GitHub Private Vulnerability Reporting (Recommended):**
   - Navigate to the **Security** tab of the GitHub repository.
   - Click **Report a vulnerability** to open an encrypted disclosure draft accessible only to maintainers.

2. **Security Team Email:**
   - Send details of the finding to: `security@enterprise.local` (or maintainer contact on the GitHub profile).

### Expected Report Format:
- **Vulnerability Description:** A brief explanation of the flaw type (e.g., Broken Access Control, SQL Injection, Secret Exposure, SSRF).
- **Steps to Reproduce (Proof of Concept):** Detailed reproduction steps or a PoC script to validate the finding.
- **Potential Impact:** Business or technical risks if the vulnerability is exploited.
- **Remediation Recommendations:** Suggested code or configuration fixes, if available.

---

## ⏱️ Response Service Level Agreement (SLA)

The maintainer team commits to enterprise banking vulnerability handling standards:

- **Initial Acknowledgment:** Within **24 hours** of report receipt.
- **Triage & Validation:** Maximum of **3 business days**.
- **Security Patch Release (Hotfix):** 
  - *Critical / High Severity (CVSS 7.0 - 10.0):* Maximum of **7 calendar days**.
  - *Medium / Low Severity (CVSS < 7.0):* Included in the next release cycle.

---

## 🔒 Safe Harbor Policy & Research Ethics

We support responsible security research (*Responsible Disclosure*). Provided that you:
1. Do not damage production data or disrupt service availability (*Denial of Service*).
2. Do not access or exfiltrate personal data belonging to other users.
3. Allow reasonable time for the team to release a patch before disclosing findings publicly.

We will not pursue legal action against your authorized security research activities.
