# Deploying to GitHub Pages

This guide explains how to publish the Ekwendeni Mission Hospital website to GitHub Pages for free hosting.

---

## Overview

GitHub Pages is a free static website hosting service provided by GitHub. It serves the files in your repository directly as a website. The site updates automatically whenever you push changes to the `main` branch.

**What you need:**
- A GitHub account (free at github.com)
- Git installed on your computer
- The project files ready to publish

---

## Step 1: Create a GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click **"New"** (green button) or go to `github.com/new`
3. Set the repository name:
   - If using a custom domain (recommended): any name, e.g., `ekwendeni-hospital-website`
   - If NOT using a custom domain: must be `yourusername.github.io` for the root URL
4. Set visibility to **Public** (required for free GitHub Pages)
5. Do NOT tick "Add a README file" (we already have one)
6. Click **"Create repository"**

---

## Step 2: Upload the Project Files

### Option A: Using Git on the command line (recommended)

In a terminal, navigate to the project folder:

```bash
cd /path/to/ekwendeni_mission_hospital_website

# Initialise git (first time only)
git init
git branch -M main

# Add all files
git add .
git commit -m "Initial website build"

# Connect to GitHub (replace with your actual repository URL)
git remote add origin https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git

# Push to GitHub
git push -u origin main
```

### Option B: GitHub Desktop app (easier for non-technical users)

1. Download GitHub Desktop from [desktop.github.com](https://desktop.github.com)
2. Click **"Add an Existing Repository from your Hard Drive"**
3. Select the project folder
4. Click **"Publish repository"** in the top bar
5. Make sure "Keep this code private" is **unchecked**
6. Click **"Publish Repository"**

---

## Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **"Settings"** (tab near the top)
3. In the left sidebar, click **"Pages"**
4. Under **"Source"**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **"Save"**
6. GitHub will display a green banner with your site URL (usually within 1–2 minutes)

**Without a custom domain**, your site will be at:  
`https://yourusername.github.io/repository-name/`

⚠️ **Important**: Without a custom domain, absolute paths like `/assets/css/main.css` will NOT work. See the note below about custom domains.

---

## Step 4: Add the Custom Domain (Required for Correct Functionality)

The site is built with absolute URL paths (e.g., `/assets/css/main.css`) which require a custom domain. Without one, navigation and styles will break.

See **CLOUDFLARE_DOMAIN.md** for the complete domain setup guide.

Once your domain is pointing to GitHub Pages:

1. In your repository, check that a file named `CNAME` exists in the root directory with your domain name inside it, e.g.:
   ```
   ekwendenihospital.mw
   ```
2. In GitHub Pages settings, enter your custom domain in the "Custom domain" field
3. Tick **"Enforce HTTPS"** once it becomes available (GitHub provisions a free TLS certificate)

---

## Updating the Website After Initial Setup

Whenever you make changes to the website files:

### Using Git (command line):

```bash
# Stage all changed files
git add .

# Commit with a description of what changed
git commit -m "Updated contact page phone numbers"

# Push to GitHub
git push
```

### Using GitHub Desktop:

1. Open GitHub Desktop
2. You'll see a list of changed files on the left
3. Write a short summary at the bottom (e.g., "Updated events for May")
4. Click **"Commit to main"**
5. Click **"Push origin"** in the top bar

Changes typically go live within **30–60 seconds** of pushing.

---

## Checking Deployment Status

1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. You'll see a list of deployments — a green tick means it deployed successfully

---

## Common Issues

### "404 Not Found" after deploying
- Check that `index.html` is in the root of the repository (not inside a subfolder)
- Wait 2–3 minutes for GitHub Pages to process the deployment

### Styles not loading / nav not appearing
- You likely don't have a custom domain set up. The site requires absolute paths which only work with a proper domain.
- See CLOUDFLARE_DOMAIN.md for domain setup.

### Changes not showing up
- Wait 1–2 minutes — GitHub Pages deployments take a moment
- Try a hard refresh in the browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Check the Actions tab for any deployment errors

---

## Branch Strategy (Optional, for More Advanced Use)

For a simple site like this, committing directly to `main` is fine. However, if multiple people are making changes, consider:

- `main` branch: always the live site
- Create a new branch for each change: `git checkout -b update-contact-page`
- Merge to `main` when ready: `git checkout main && git merge update-contact-page`
