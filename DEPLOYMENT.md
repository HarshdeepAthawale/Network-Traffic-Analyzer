# Deployment Guide

This guide will help you deploy the Network Traffic Analyzer project with the backend on Render and the frontend on Vercel.

## Architecture

- **Backend (Python/FastAPI)** → Render
- **Frontend (Next.js)** → Vercel

## Prerequisites

1. GitHub account with your code pushed to a repository
2. [Render](https://render.com) account (free tier available)
3. [Vercel](https://vercel.com) account (free tier available)

## Part 1: Deploy Backend to Render

### Option A: Using render.yaml (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Sign in to Render**
   - Go to https://dashboard.render.com
   - Click "New +" and select "Blueprint"

3. **Connect your repository**
   - Select your GitHub repository
   - Render will automatically detect the `render.yaml` file

4. **Configure Environment Variables** (Optional)
   - Service Name: `network-traffic-analyzer-backend`
   - You can add these optional environment variables:
     - `NTA_CORS_ORIGINS`: Your Vercel frontend URL (e.g., `https://your-app.vercel.app`)
     - `NTA_MAX_UPLOAD_SIZE`: Maximum upload size in bytes (default: 104857600)
     - `NTA_STORAGE_TYPE`: `memory` (recommended for free tier)

5. **Deploy**
   - Click "Apply" and wait for deployment to complete
   - Copy your backend URL (e.g., `https://network-traffic-analyzer-backend.onrender.com`)

### Option B: Manual Deployment

1. **Sign in to Render**
   - Go to https://dashboard.render.com
   - Click "New +" and select "Web Service"

2. **Connect your repository**
   - Select your GitHub repository
   - Choose the repository branch

3. **Configure the service**
   - **Name**: `network-traffic-analyzer-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**
   Add these environment variables:
   ```
   NTA_DEBUG=false
   NTA_HOST=0.0.0.0
   NTA_STORAGE_TYPE=memory
   ```

5. **Create Web Service**
   - Click "Create Web Service"
   - Wait for deployment (first deploy takes 5-10 minutes)
   - Copy your backend URL

### Important Notes for Render

- **Free Tier Limitations**:
  - Service spins down after 15 minutes of inactivity
  - First request after spin-down takes 30-60 seconds to wake up
  - 750 free hours per month
  
- **Persistent Storage**: The free tier uses in-memory storage, so uploaded files are lost when the service restarts. For persistent storage, consider upgrading to a paid plan with persistent disks.

## Part 2: Deploy Frontend to Vercel

### Step 1: Prepare for Deployment

1. **Update the frontend API URL**
   - You'll configure this in Vercel's environment variables

### Step 2: Deploy to Vercel

1. **Sign in to Vercel**
   - Go to https://vercel.com
   - Click "Add New..." → "Project"

2. **Import your repository**
   - Select your GitHub repository
   - Click "Import"

3. **Configure Project**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

4. **Environment Variables**
   Add this environment variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your Render backend URL (e.g., `https://network-traffic-analyzer-backend.onrender.com`)

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment (2-5 minutes)
   - Copy your frontend URL (e.g., `https://your-app.vercel.app`)

### Step 3: Update CORS Settings

1. **Go back to Render Dashboard**
   - Navigate to your backend service
   - Go to "Environment" tab

2. **Add/Update CORS Environment Variable**
   - Add new environment variable:
     - **Key**: `NTA_CORS_ORIGINS`
     - **Value**: Your Vercel URL (e.g., `https://your-app.vercel.app,https://your-app-*.vercel.app`)
   - Click "Save Changes"
   - Service will automatically redeploy

## Part 3: Testing Your Deployment

1. **Visit your frontend URL**
   - Open your Vercel URL in a browser
   - You should see the Network Traffic Analyzer interface

2. **Test file upload**
   - Upload a small PCAP file
   - Check if the analysis works
   - Note: First request might be slow if Render service was sleeping

3. **Check for errors**
   - Open browser DevTools Console
   - Look for any CORS or API connection errors
   - If you see CORS errors, verify the `NTA_CORS_ORIGINS` setting in Render

## Troubleshooting

### Backend Issues

**Problem**: 502 Bad Gateway or service unavailable
- **Solution**: Wait 30-60 seconds for the Render service to wake up (free tier)

**Problem**: Build fails on Render
- **Solution**: Check build logs and ensure all dependencies in `requirements.txt` are correct

**Problem**: "Module not found" errors
- **Solution**: Ensure the start command includes `cd backend`

### Frontend Issues

**Problem**: "Failed to fetch" or network errors
- **Solution**: Check that `NEXT_PUBLIC_API_URL` is set correctly in Vercel

**Problem**: CORS errors in browser console
- **Solution**: Update `NTA_CORS_ORIGINS` in Render to include your Vercel URL

**Problem**: Build fails on Vercel
- **Solution**: Check build logs and ensure all npm dependencies are installed

### Connection Issues

**Problem**: Frontend can't connect to backend
1. Verify the `NEXT_PUBLIC_API_URL` in Vercel settings
2. Test backend directly: `https://your-backend.onrender.com/`
3. Check CORS settings in Render
4. Ensure backend is not in "sleeping" state

## Environment Variables Reference

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Backend (Render)
```
NTA_DEBUG=false
NTA_HOST=0.0.0.0
NTA_STORAGE_TYPE=memory
NTA_CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend-*.vercel.app
NTA_MAX_UPLOAD_SIZE=104857600
NTA_UPLOAD_CHUNK_SIZE=1048576
NTA_CACHE_TTL=300
NTA_MAX_PACKETS_PER_PAGE=100
NTA_DEFAULT_PACKETS_PER_PAGE=25
```

## Updating Your Deployment

### Updating Backend
1. Push changes to GitHub
2. Render automatically redeploys (if auto-deploy is enabled)
3. Or manually trigger deployment in Render dashboard

### Updating Frontend
1. Push changes to GitHub
2. Vercel automatically redeploys
3. Or manually trigger deployment in Vercel dashboard

## Cost Considerations

### Free Tier Limits

**Render Free Tier**:
- 750 hours per month per service
- Service sleeps after 15 minutes of inactivity
- 512 MB RAM
- Shared CPU

**Vercel Free Tier**:
- Unlimited deployments
- 100 GB bandwidth per month
- Serverless function execution: 100 GB-hours
- 1000 serverless function invocations per day

## Upgrading for Production

For production use, consider:

1. **Render**:
   - Upgrade to paid plan for:
     - Always-on service (no sleeping)
     - More memory and CPU
     - Persistent disk storage
   - Starting at $7/month

2. **Vercel**:
   - Pro plan for:
     - Higher bandwidth limits
     - Better analytics
     - Commercial use
   - Starting at $20/month per user

## Security Recommendations

1. **Update CORS Origins**
   - Replace `*` with specific frontend URLs
   - Use environment variables for configuration

2. **Add Authentication**
   - Consider adding user authentication for production
   - Protect sensitive endpoints

3. **File Upload Limits**
   - Configure appropriate file size limits
   - Validate file types

4. **HTTPS Only**
   - Both Render and Vercel provide HTTPS by default
   - Ensure all API calls use HTTPS

## Support

For deployment issues:
- **Render**: https://render.com/docs
- **Vercel**: https://vercel.com/docs
- **Project Issues**: Open an issue on GitHub

## Next Steps

1. Set up custom domain (optional)
2. Configure analytics and monitoring
3. Set up error tracking (e.g., Sentry)
4. Add CI/CD workflows
5. Configure database for persistent storage (if needed)

---

Happy deploying! 🚀

