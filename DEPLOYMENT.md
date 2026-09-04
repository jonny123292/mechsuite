# MechSuite Deployment Guide

This guide walks you through deploying **MechSuite** to the cloud (free on **Render** or **Railway**) so anyone can access your Mechanical Engineering Suite via a public URL (`https://your-app.onrender.com`).

---

## 🌟 Option A: Deploy to Render (Free, Recommended)

Render provides a completely free tier for web applications with automatic SSL (HTTPS).

### Step 1: Upload Your Code to GitHub
1. Go to [GitHub](https://github.com/) and log in (or create a free account).
2. Click the **`+`** icon in the top right → **New repository**.
3. Name your repository `mechsuite` (or any name you like) and set it to **Public** or **Private**.
4. Click **Create repository**.
5. Upload your files:
   - On your new GitHub repository page, click **"uploading an existing file"**.
   - Drag and drop the contents of this project folder (**excluding `.venv`**).
   - Click **Commit changes**.

### Step 2: Deploy on Render
1. Go to [Render](https://render.com/) and sign up / log in with your GitHub account.
2. In your Render Dashboard, click **New +** → **Web Service**.
3. Select **Build and deploy from a Git repository** → click **Next**.
4. Connect your GitHub account and select the `mechsuite` repository you just created.
5. Fill in the service settings:
   - **Name**: `mechsuite` (or any unique name)
   - **Region**: Nearest to you (e.g. Frankfurt, Oregon, Singapore)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: **Free**
6. Click **Deploy Web Service**.

Render will automatically install the requirements, start the Gunicorn server, and provide you with a live public URL (e.g. `https://mechsuite.onrender.com`).

---

## 🚂 Option B: Deploy to Railway

Railway is another popular platform with instant zero-config deployments.

1. Go to [Railway](https://railway.app/) and sign up with GitHub.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your `mechsuite` repository.
4. Railway will automatically read `Procfile` / `railway.json` and start the deployment.
5. In project settings, click **Generate Domain** to receive your public `.up.railway.app` URL.

---

## 🐳 Option C: Deploy with Docker

If you have Docker installed or want to deploy to a VPS (DigitalOcean, AWS EC2, etc.):

1. **Build the image**:
   ```bash
   docker build -t mechsuite .
   ```
2. **Run the container**:
   ```bash
   docker run -d -p 5000:5000 --name mechsuite-app mechsuite
   ```
3. Open `http://localhost:5000` in your browser.

---

## 💻 Local Production WSGI Test

To verify production serving locally using multi-threaded Waitress WSGI:
```powershell
& ".\.venv\Scripts\python.exe" deploy_local.py
```
This tests the exact production WSGI environment before pushing to the cloud.

