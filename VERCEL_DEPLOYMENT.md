# Vercel Deployment Guide

This guide will help you deploy your Parra Energy project to Vercel.

## Prerequisites

1. A Vercel account (free at [vercel.com](https://vercel.com))
2. Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Connect Your Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your Git repository
4. Vercel will automatically detect this as a monorepo with Next.js applications

### 2. Configure Build Settings

Vercel should automatically detect the configuration, but verify these settings:

- **Framework Preset**: `Other` (since we're using a custom monorepo setup)
- **Root Directory**: `/` (root of the monorepo)
- **Build Command**: `pnpm build`
- **Install Command**: `pnpm install`
- **Output Directory**: Leave empty (handled by vercel.json)

### 3. Environment Variables

Add any required environment variables in the Vercel dashboard:

- Go to your project settings
- Navigate to "Environment Variables"
- Add any variables your apps need (API keys, database URLs, etc.)

### 4. Deploy

1. Click "Deploy"
2. Vercel will build and deploy your applications
3. The web app will be available at your Vercel domain
4. API routes will be available at `your-domain.vercel.app/api/*`

## Project Structure

After deployment:
- **Web App**: Available at the root domain
- **API Routes**: Available at `/api/*` (automatically routed to the API app)

## Configuration Files

### vercel.json
This file configures how Vercel handles the monorepo:
- Routes API requests to the API app
- Routes all other requests to the web app
- Sets up proper Node.js runtime

### .vercelignore
Excludes unnecessary files from deployment to keep the build fast and clean.

## Troubleshooting

### Build Issues
1. Check that all dependencies are properly installed
2. Verify that the build command works locally: `pnpm build`
3. Check the build logs in Vercel dashboard

### Runtime Issues
1. Verify environment variables are set correctly
2. Check that API routes are working
3. Review function logs in Vercel dashboard

### Performance
1. The `output: 'standalone'` configuration optimizes the build
2. Images are set to `unoptimized: true` for faster builds
3. Turbo caching is enabled for faster subsequent builds

## Custom Domains

To add a custom domain:
1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Configure DNS as instructed

## Monitoring

Vercel provides:
- Function logs for API routes
- Build logs for debugging
- Performance analytics
- Error tracking

## Local Development

To test the production build locally:
```bash
pnpm build
pnpm start
```

## Support

If you encounter issues:
1. Check the Vercel documentation
2. Review the build and function logs
3. Test locally with `pnpm build && pnpm start` 