# Deploy Frontend to Vercel

This guide provides step-by-step instructions to deploy your frontend application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com/signup) if you don't have an account
2. **Vercel CLI** (Optional): Install globally via npm: `npm install -g vercel`
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, or Bitbucket)

## Method 1: Deploy via Vercel Dashboard (Recommended)

### Step 1: Prepare Your Code
1. Ensure your frontend code is pushed to a Git repository
2. Make sure your `package.json` has the correct build script:
   ```json
   {
     "scripts": {
       "dev": "next dev",
       "build": "next build",
       "start": "next start",
       "lint": "next lint"
     }
   }
   ```

### Step 2: Connect Your Repository
1. Go to [vercel.com/dashboard/new](https://vercel.com/dashboard/new)
2. Click "Continue" to import your Git repository
3. Select the repository containing your frontend code
4. Click "Import"

### Step 3: Configure Project Settings
1. In the "Configure Project" step, set these values:
   - **Framework Preset**: Next.js (should auto-detect)
   - **Build Command**: `npm run build` or leave blank to auto-detect
   - **Output Directory**: `.next` (should auto-detect)
   - **Development Command**: `npm run dev` (for Preview deployments)

### Step 4: Set Environment Variables
1. Under "Environment Variables", add the following:
   - `NEXT_PUBLIC_API_URL`: `https://your-backend-domain.com/api` (replace with your actual backend URL)
   - `BETTER_AUTH_SECRET`: Your production auth secret (generate a strong random string)
   - `BETTER_AUTH_URL`: `https://your-frontend-domain.vercel.app` (replace with your Vercel domain)

### Step 5: Deploy
1. Click "Deploy" and wait for the build to complete
2. Your site will be deployed to a URL like `https://your-project-name.vercel.app`

## Method 2: Deploy via Vercel CLI

### Step 1: Install and Login
```bash
npm install -g vercel
vercel login
```

### Step 2: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 3: Initialize and Deploy
```bash
vercel --confirm
```

### Step 4: Set Up Environment Variables
During the setup, you'll be prompted to set environment variables. Provide:
- `NEXT_PUBLIC_API_URL`: `https://your-backend-domain.com/api`
- `BETTER_AUTH_SECRET`: Your production auth secret
- `BETTER_AUTH_URL`: `https://your-frontend-domain.vercel.app`

## Method 3: Git Integration (Automatic Deployments)

### Step 1: Link Your Repository
```bash
cd frontend
vercel --git-repo
```

### Step 2: Configure Automatic Deployments
1. Go to your Vercel dashboard
2. Select your project
3. Go to "Settings" → "Git" → "Deploy Hooks"
4. Configure to deploy on every push to main branch

## Environment Variables for Vercel

### Required Variables:
- `NEXT_PUBLIC_API_URL`: URL of your deployed backend (e.g., `https://your-backend.onrender.com/api` or `https://your-backend-app.fly.dev/api`)
- `BETTER_AUTH_SECRET`: A secure secret key for authentication (min 32 characters)
- `BETTER_AUTH_URL`: The URL of your deployed frontend (e.g., `https://your-frontend.vercel.app`)

### To Generate a Secure Secret:
```bash
# Using openssl
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## Important Configuration Notes

### Next.js Configuration
Make sure your `next.config.js` is properly configured for production:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // This is already set in your current config
  reactStrictMode: true,
  swcMinify: true,
}

module.exports = nextConfig
```

### API URL Configuration
For Vercel deployment, update your `NEXT_PUBLIC_API_URL` to point to your deployed backend:
- If deploying backend to Render: `https://your-backend-app.render.com/api`
- If deploying backend to Railway: `https://your-backend-app.up.railway.app/api`
- If deploying backend to Fly.io: `https://your-backend-app.fly.dev/api`
- If using a custom domain: `https://api.yourdomain.com/api`

## Testing Your Deployment

1. After deployment, visit your Vercel URL
2. Check browser console for any API connection errors
3. Verify that authentication and API calls work correctly
4. Test the health endpoint of your backend: `YOUR_BACKEND_URL/health`

## Common Issues and Solutions

### Issue 1: API Requests Failing
**Cause**: Incorrect `NEXT_PUBLIC_API_URL` setting
**Solution**: Double-check the environment variable in Vercel dashboard

### Issue 2: Authentication Not Working
**Cause**: Missing or incorrect `BETTER_AUTH_SECRET`
**Solution**: Regenerate and set the correct secret in Vercel environment variables

### Issue 3: Build Failures
**Cause**: Missing dependencies or incorrect build command
**Solution**:
- Ensure all dependencies are in `package.json`
- Check that `npm run build` works locally
- Verify Node.js version compatibility

### Issue 4: Static Assets Not Loading
**Solution**: Check your Next.js configuration and ensure assets are in the `public` folder

## Custom Domain Setup

1. In your Vercel dashboard, go to your project
2. Go to "Settings" → "Domains"
3. Add your custom domain (e.g., `app.yourdomain.com`)
4. Follow DNS configuration instructions provided by Vercel

## Monitoring and Analytics

1. Vercel provides built-in analytics for your deployment
2. Check "Analytics" tab in your project dashboard
3. Monitor performance, error rates, and traffic

## Troubleshooting

### Check Build Logs
If deployment fails, check the build logs in your Vercel dashboard for specific error messages.

### Local Testing
Before deploying, test your build locally:
```bash
npm run build
npm start
```

### Environment Variables
Remember that only variables prefixed with `NEXT_PUBLIC_` are available in the browser. Regular environment variables are only available at build time or server-side.

## Next Steps

1. Deploy your backend first to a cloud provider (Render, Railway, Fly.io, etc.)
2. Get the backend URL
3. Update `NEXT_PUBLIC_API_URL` in Vercel environment variables
4. Redeploy your frontend
5. Test the complete application flow

Your frontend will be accessible at your Vercel URL, and it will communicate with your backend API using the configured `NEXT_PUBLIC_API_URL`.