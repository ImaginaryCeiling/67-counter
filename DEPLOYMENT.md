# 67 Counter - Vercel Deployment Guide

This guide walks you through deploying both the frontend and API to Vercel.

## Overview

- **Frontend**: Next.js app deployed to Vercel
- **API**: Python Flask API deployed as Vercel serverless functions
- **Data**: In-memory storage with demo data (upgradeable to database)

## Prerequisites

- Vercel account ([sign up here](https://vercel.com))
- Git repository with your code
- Vercel CLI (optional): `npm i -g vercel`

## Deployment Steps

### 1. Deploy the API

1. **Push API to Git**:
   ```bash
   cd api
   git init
   git add .
   git commit -m "Initial API commit"
   git remote add origin YOUR_API_REPO_URL
   git push -u origin main
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your API repository
   - Vercel will detect the `vercel.json` configuration
   - Click "Deploy"

3. **Get API URL**:
   - After deployment, copy your API URL (e.g., `https://your-api.vercel.app`)

### 2. Deploy the Frontend

1. **Update Environment Variables**:
   ```bash
   cd frontend
   # Edit .env.local to use your deployed API URL
   echo "NEXT_PUBLIC_API_URL=https://your-api.vercel.app" > .env.local
   ```

2. **Push Frontend to Git**:
   ```bash
   git init
   git add .
   git commit -m "Initial frontend commit"
   git remote add origin YOUR_FRONTEND_REPO_URL
   git push -u origin main
   ```

3. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your frontend repository
   - Add environment variable: `NEXT_PUBLIC_API_URL` = `https://your-api.vercel.app`
   - Click "Deploy"

## Alternative: Single Repository Deployment

You can also deploy both from a single repository:

1. **Project Structure**:
   ```
   67-counter/
   ├── frontend/          # Next.js app
   ├── api/              # Flask API
   └── README.md
   ```

2. **Deploy API First**:
   - Create new Vercel project
   - Set Root Directory to `api`
   - Deploy

3. **Deploy Frontend Second**:
   - Create another Vercel project  
   - Set Root Directory to `frontend`
   - Add environment variable with API URL
   - Deploy

## Environment Variables

### Frontend
**Vercel Environment Variable:**
- `NEXT_PUBLIC_API_URL` = `https://your-api.vercel.app`

**Local Development (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:5002
```

### API (no env vars needed)
The API uses in-memory storage and includes demo data.

### Python Script (Optional)
**For production API:**
```bash
export API_URL=https://your-api.vercel.app
```

**Local Development:**
```bash
export API_URL=http://localhost:5002
# or just omit - defaults to localhost:5002
```

## Testing Deployment

1. **Test API**:
   ```bash
   curl https://your-api.vercel.app/api/health
   curl https://your-api.vercel.app/api/rankings
   ```

2. **Test Frontend**:
   - Visit your frontend URL
   - Should show demo rankings data
   - Try the refresh button

## Customization

### Adding Real Database

To use a real database instead of in-memory storage:

1. **Add Database Service** (e.g., Supabase, PlanetScale)
2. **Update API Code** in `api/index.py`:
   - Replace `data_store` with database calls
   - Add database connection code
3. **Add Environment Variables** for database credentials

### Custom Domain

1. Go to your Vercel project settings
2. Click "Domains" 
3. Add your custom domain
4. Update DNS records as instructed

## Monitoring

- **Vercel Dashboard**: Monitor deployments, logs, analytics
- **Error Tracking**: Check Function Logs in Vercel dashboard
- **Performance**: View Web Analytics in Vercel

## Troubleshooting

### Common Issues

1. **API Not Found (404)**:
   - Check `vercel.json` routes configuration
   - Ensure `api/index.py` file exists

2. **CORS Errors**:
   - API is configured with CORS enabled for all origins
   - Check browser console for specific errors

3. **Environment Variables**:
   - Make sure `NEXT_PUBLIC_API_URL` is set in Vercel dashboard
   - Redeploy after changing environment variables

4. **Build Errors**:
   - Check Vercel build logs
   - Ensure all dependencies are in `requirements.txt` (API) and `package.json` (frontend)

## Next Steps

After successful deployment:
- Share your live URLs
- Add more demo data or connect real database  
- Set up custom domain
- Monitor usage and performance

Your 67 Counter app is now live and ready to track hand crossing competitions worldwide! 🏆