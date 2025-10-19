# Deployment Checklist ✅

Use this checklist to deploy your Network Traffic Analyzer to production.

## Pre-Deployment

- [ ] Code is committed and pushed to GitHub
- [ ] All tests pass locally
- [ ] Environment variables are documented
- [ ] Dependencies are up to date

## Backend Deployment (Render)

### Setup
- [ ] Create Render account at https://render.com
- [ ] Connect GitHub account to Render
- [ ] Verify `render.yaml` configuration exists

### Deployment
- [ ] Create new Blueprint in Render (or Web Service)
- [ ] Select your GitHub repository
- [ ] Verify build command: `pip install -r backend/requirements.txt`
- [ ] Verify start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Deploy and wait for completion

### Configuration
- [ ] Copy backend URL (e.g., `https://your-app.onrender.com`)
- [ ] Add environment variable: `NTA_DEBUG=false`
- [ ] Add environment variable: `NTA_STORAGE_TYPE=memory`
- [ ] Add environment variable: `NTA_CORS_ORIGINS` (will update after frontend deployment)

### Testing
- [ ] Visit backend URL in browser
- [ ] Check API documentation at `/docs`
- [ ] Verify health endpoint returns 200 OK

## Frontend Deployment (Vercel)

### Setup
- [ ] Create Vercel account at https://vercel.com
- [ ] Connect GitHub account to Vercel
- [ ] Verify `vercel.json` configuration exists

### Deployment
- [ ] Click "Add New..." → "Project" in Vercel
- [ ] Import your GitHub repository
- [ ] Verify framework preset is Next.js
- [ ] Add environment variable:
  - [ ] `NEXT_PUBLIC_API_URL` = Your Render backend URL
- [ ] Deploy and wait for completion

### Configuration
- [ ] Copy frontend URL (e.g., `https://your-app.vercel.app`)
- [ ] Test frontend loads correctly
- [ ] Verify theme toggle works

## Post-Deployment Configuration

### Update CORS Settings
- [ ] Go back to Render dashboard
- [ ] Navigate to your backend service
- [ ] Update environment variable:
  - [ ] `NTA_CORS_ORIGINS` = Your Vercel URL (e.g., `https://your-app.vercel.app,https://your-app-*.vercel.app`)
- [ ] Save changes (service will auto-redeploy)
- [ ] Wait for redeployment to complete

## Testing Production Environment

### Smoke Tests
- [ ] Open frontend URL in browser
- [ ] Upload a small PCAP file (< 5MB)
- [ ] Verify dashboard loads with data
- [ ] Check packet table displays correctly
- [ ] Verify protocol charts render
- [ ] Check IP/MAC mapping table
- [ ] Test filters and pagination
- [ ] Switch between light/dark themes

### Browser Console
- [ ] Open DevTools Console (F12)
- [ ] Check for JavaScript errors
- [ ] Verify no CORS errors
- [ ] Check API calls succeed (Network tab)

### Performance
- [ ] Check initial load time (should be < 3s)
- [ ] Test with larger PCAP file (10-50MB)
- [ ] Verify smooth scrolling and interactions

## Security & Best Practices

### Security
- [ ] HTTPS is enabled (default on both platforms)
- [ ] CORS is restricted to your domain
- [ ] File upload size limits are set
- [ ] No sensitive data in environment variables

### Monitoring
- [ ] Set up uptime monitoring (optional)
- [ ] Configure error tracking (optional)
- [ ] Enable analytics (optional)

## Documentation

- [ ] Update README with deployment URLs
- [ ] Document any custom configuration
- [ ] Share deployment guide with team
- [ ] Create runbook for common issues

## Optional Enhancements

### Custom Domain
- [ ] Purchase domain name
- [ ] Configure DNS settings
- [ ] Add domain to Vercel
- [ ] Add domain to Render
- [ ] Update CORS settings

### Monitoring & Analytics
- [ ] Set up Vercel Analytics
- [ ] Configure error tracking (Sentry)
- [ ] Set up uptime monitoring
- [ ] Enable logging

### Performance
- [ ] Enable Vercel Analytics
- [ ] Configure caching headers
- [ ] Optimize images
- [ ] Test with Lighthouse

## Troubleshooting

If you encounter issues, check:

- [ ] Environment variables are set correctly
- [ ] Backend URL is accessible
- [ ] CORS settings include your frontend domain
- [ ] Build logs for errors
- [ ] Runtime logs for errors

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed troubleshooting steps.

## Rollback Plan

If deployment fails:

- [ ] Check build logs in Render/Vercel
- [ ] Revert to previous commit if needed
- [ ] Roll back environment variables
- [ ] Redeploy from last known good commit

## Success Criteria

Deployment is successful when:

- ✅ Backend responds to health checks
- ✅ Frontend loads without errors
- ✅ File upload works end-to-end
- ✅ Data displays correctly in dashboard
- ✅ No CORS or network errors
- ✅ Performance is acceptable

---

## Quick Reference

### Backend URL
```
Production: https://your-backend.onrender.com
Docs: https://your-backend.onrender.com/docs
```

### Frontend URL
```
Production: https://your-app.vercel.app
```

### Support Links
- Render Dashboard: https://dashboard.render.com
- Vercel Dashboard: https://vercel.com/dashboard
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs

---

**Note**: Keep this checklist updated as your deployment process evolves.

🎉 **Congratulations on deploying your Network Traffic Analyzer!**

