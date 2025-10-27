# Render Deployment Guide

## 🚀 Deploying Network Traffic Analyzer to Render

---

## Step 1: Push to GitHub

Make sure your code is pushed to GitHub:

```bash
git add .
git commit -m "Add Cloudinary + MongoDB integration"
git push origin master
```

---

## Step 2: Connect to Render

1. Go to https://render.com
2. Sign up or log in
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Select your repository

---

## Step 3: Configure Your Service

### Service Settings
- **Name**: `network-traffic-analyzer-backend`
- **Environment**: `Python 3`
- **Branch**: `master` (or your default branch)
- **Root Directory**: Leave empty (whole repo)
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Step 4: Add Environment Variables

Click **"Environment"** tab and add these variables:

### Cloudinary (Required)
```
NTA_CLOUDINARY_CLOUD_NAME=dgdbs9kt3
NTA_CLOUDINARY_API_KEY=396237447446776
NTA_CLOUDINARY_API_SECRET=s_v3LI31qQ7iRrv71syy6Mnnp2M
```

### MongoDB (Required)
```
NTA_MONGODB_URI=mongodb+srv://harshdeepathawale777_db_user:fYGzE0I9LqwgPwZz@cluster2.uz5vnrp.mongodb.net/
NTA_MONGODB_DATABASE=network_traffic_analyzer
```

### Other Settings
```
NTA_DEBUG=false
NTA_HOST=0.0.0.0
NTA_PORT=$PORT
NTA_CORS_ORIGINS=*
NTA_MAX_UPLOAD_SIZE=524288000
```

---

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for the build to complete (usually 2-5 minutes)
3. You'll see logs showing:
   ```
   ✅ Cloudinary initialized successfully
   ✅ MongoDB initialized successfully
   ```
4. Your service will be live at: `https://your-service-name.onrender.com`

---

## Step 6: Test Your Deployment

### Test Health Check
```bash
curl https://your-service-name.onrender.com/
```

Should return:
```json
{
  "message": "Network Traffic Analyzer API",
  "version": "1.0.0"
}
```

### Test MongoDB Connection
Visit: `https://your-service-name.onrender.com/api/files`

Should return an empty array `[]` if working correctly.

---

## Step 7: Update Frontend (if deployed)

Update your frontend API URL to point to your Render backend:

**If using Vercel/Netlify:**
- Update API endpoint in your frontend code
- Set `VITE_API_URL=https://your-service-name.onrender.com/api`

**Or create `.env.production`:**
```
VITE_API_URL=https://your-service-name.onrender.com/api
```

---

## 📊 Monitoring

### View Logs
- Go to your service in Render dashboard
- Click **"Logs"** tab to see real-time logs

### Health Check
- Auto health check at `/` endpoint
- Render will restart service if unhealthy

---

## 🔧 Troubleshooting

### Build Failed
- Check logs in Render dashboard
- Verify `requirements.txt` is in `backend/` folder
- Make sure Python 3.11.9 is supported

### MongoDB Connection Failed
- Check MongoDB Atlas IP whitelist
- Add Render IPs or set to `0.0.0.0/0` for all IPs
- Verify connection string is correct

### Cloudinary Errors
- Verify credentials in environment variables
- Check Cloudinary dashboard for usage limits

### Service Crashes
- Check logs for Python errors
- Verify all environment variables are set
- MongoDB and Cloudinary credentials are required

---

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] Service created in Render
- [ ] Environment variables added
- [ ] Build successful
- [ ] Service running
- [ ] Health check passed
- [ ] Can access `/api/files` endpoint

---

## 🎉 You're Live!

Your backend is now deployed at:
**https://your-service-name.onrender.com**

**API Base URL**: `https://your-service-name.onrender.com/api`

**API Documentation**: `https://your-service-name.onrender.com/docs`

---

## 📝 Next Steps

1. **Deploy Frontend** to Vercel/Netlify
2. **Update Frontend API URL** to your Render backend
3. **Test the full stack** with a PCAP file upload

---

## 💰 Free Tier Limits

- **MongoDB Atlas**: 512MB storage, shared cluster
- **Cloudinary**: 25GB storage, 25GB bandwidth/month
- **Render**: 750 hours/month (enough for most projects)
- **Total Cost**: $0/month 🎉

---

## 🔐 Security Notes

⚠️ **Never commit `.env` file to GitHub!**
- Your `.env` file should already be in `.gitignore`
- Secrets are added via Render dashboard only

---

## 📚 Resources

- [Render Docs](https://render.com/docs)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Cloudinary Docs](https://cloudinary.com/documentation)

