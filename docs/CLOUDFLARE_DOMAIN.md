# Setting Up a Custom Domain with Cloudflare

This guide explains how to connect a custom domain (e.g., `ekwendenihospital.mw`) to the GitHub Pages site using Cloudflare for DNS management.

---

## Why Cloudflare?

Cloudflare provides:
- Free DNS management
- Free SSL/TLS certificate (HTTPS) for your domain
- DDoS protection
- Fast global CDN (content delivery network)

---

## Prerequisites

- The website is already deployed to GitHub Pages (see GITHUB_PAGES.md)
- You have a domain name registered (either through Cloudflare Registrar or another registrar)
- You have a Cloudflare account (free at cloudflare.com)

---

## Overview of How It Works

```
Visitor's browser
       ↓
 ekwendenihospital.mw (your domain)
       ↓
 Cloudflare (DNS + CDN)
       ↓
 GitHub Pages (your-username.github.io)
       ↓
 Your website files
```

---

## Step 1: Add Your Domain to Cloudflare

If your domain is **registered through Cloudflare Registrar**:
- It is already in your Cloudflare account. Skip to Step 2.

If your domain is **registered elsewhere** (e.g., Malawi domain registrar):
1. Log in to [cloudflare.com](https://cloudflare.com)
2. Click **"Add a Site"**
3. Enter your domain name and click **"Add Site"**
4. Select the **Free** plan
5. Cloudflare will scan your existing DNS records
6. Click **"Continue"**
7. Cloudflare will show you two nameserver addresses (e.g., `ada.ns.cloudflare.com`)
8. Log in to your domain registrar and change the nameservers to the ones Cloudflare provides
9. This can take up to 24 hours to propagate

---

## Step 2: Add DNS Records in Cloudflare

In your Cloudflare dashboard, go to **DNS** for your domain.

Delete any existing A records or CNAME records for the root domain (`@`) or `www` that you don't want.

Add the following records:

### A Records (for root domain — e.g., `ekwendenihospital.mw`)

Add **four** A records pointing to GitHub Pages' IP addresses:

| Type | Name | Content | Proxy status |
|------|------|---------|--------------|
| A | `@` | `185.199.108.153` | DNS only (grey cloud) |
| A | `@` | `185.199.109.153` | DNS only (grey cloud) |
| A | `@` | `185.199.110.153` | DNS only (grey cloud) |
| A | `@` | `185.199.111.153` | DNS only (grey cloud) |

### CNAME Record (for www subdomain)

| Type | Name | Content | Proxy status |
|------|------|---------|--------------|
| CNAME | `www` | `YOUR-USERNAME.github.io` | DNS only (grey cloud) |

Replace `YOUR-USERNAME` with your actual GitHub username.

**Important:** Set proxy status to **"DNS only"** (grey cloud icon), NOT "Proxied" (orange cloud). GitHub Pages needs to see the real IP to provision your TLS certificate.

---

## Step 3: Add CNAME File to Your Repository

In the root of the website project, there should be a file called `CNAME` (no file extension) containing exactly your domain name:

```
ekwendenihospital.mw
```

This file is already created in the project. Open it and update it with your actual domain name.

Commit and push this file to GitHub:
```bash
git add CNAME
git commit -m "Add custom domain CNAME"
git push
```

---

## Step 4: Configure GitHub Pages Custom Domain

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Custom domain**, enter: `ekwendenihospital.mw`
4. Click **Save**
5. Wait for the DNS check to pass (green tick)
6. Once the DNS check passes, tick **Enforce HTTPS**

GitHub Pages will automatically provision a free TLS certificate via Let's Encrypt. This may take up to 30 minutes.

---

## Step 5: Configure Cloudflare SSL Settings

In Cloudflare:
1. Go to **SSL/TLS** → **Overview**
2. Set encryption mode to **"Full"** (not "Flexible", not "Full (Strict)")
   - **Full** works because GitHub Pages provides a valid certificate
   - **Flexible** would cause redirect loops
   - **Full (Strict)** may cause issues; use Full

---

## Step 6: Test the Setup

After DNS propagates (usually within 30 minutes, up to 24 hours):

1. Visit `https://ekwendenihospital.mw` — the site should load
2. Visit `https://www.ekwendenihospital.mw` — should redirect to the root domain
3. Check that the padlock (🔒) appears in the browser address bar (HTTPS working)

---

## Troubleshooting

### "ERR_TOO_MANY_REDIRECTS"
- Check Cloudflare SSL mode is set to **"Full"** not "Flexible"

### Site loads but assets (CSS, images) are missing
- Check the `CNAME` file contains the correct domain name
- Check GitHub Pages Custom domain field matches exactly

### DNS not propagating
- Use [dnschecker.org](https://dnschecker.org) to check if your A records have propagated worldwide
- Wait up to 24 hours for full propagation

### "Not secure" warning / no HTTPS
- Make sure "Enforce HTTPS" is enabled in GitHub Pages settings
- GitHub may need up to 30 minutes to provision the certificate

---

## Annual Renewal

Domain names must be renewed annually. Cloudflare Registrar will send email reminders before expiry. If using another registrar, set calendar reminders to renew before the expiry date to avoid the site going offline.
