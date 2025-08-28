# 🚀 Deploying GANI on Vercel

This guide will help you deploy the GANI RAG chatbot system on Vercel's serverless platform.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your GANI code to GitHub
3. **API Keys**: Ensure you have Pinecone and OpenRouter API keys

## 🔧 Setup Steps

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy from GitHub
```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/gani-repo.git
cd gani-repo

# Deploy to Vercel
vercel
```

### 4. Set Environment Variables
In your Vercel dashboard, go to your project settings and add these environment variables:

```bash
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX=gani
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=openai/gpt-oss-20b
```

## 🌐 Deployment Options

### Option A: Deploy via Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure environment variables
5. Deploy!

### Option B: Deploy via CLI
```bash
vercel --prod
```

## 📁 Project Structure for Vercel

```
GANI/
├── api/
│   ├── chat.py              # Main FastAPI app
│   └── chat_vercel.py       # Vercel-optimized version
├── rag/                     # RAG components
├── prompts/                 # System prompts
├── web/                     # Frontend files
├── vercel.json             # Vercel configuration
├── requirements-vercel.txt  # Vercel dependencies
└── config.yaml             # App configuration
```

## ⚠️ Important Notes

### **Cold Start Optimization**
- Components are initialized on first request
- Subsequent requests reuse initialized components
- Consider using Vercel's Edge Functions for faster responses

### **Memory Limitations**
- Vercel has memory limits per function
- BGE model loading may take time on cold starts
- Consider using Pinecone's hosted embeddings

### **Timeout Considerations**
- Default timeout: 10 seconds
- Extended timeout: 30 seconds (configured in vercel.json)
- Complex RAG operations may need optimization

## 🔍 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-vercel-url.vercel.app/health
```

### 2. Chat Endpoint
```bash
curl -X POST https://your-vercel-url.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Give me a 3-line intro about Ganesh."}'
```

### 3. Frontend Integration
Update your web UI to point to the Vercel URL:
```javascript
this.apiUrl = 'https://your-vercel-url.vercel.app';
```

## 🚨 Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are in `requirements-vercel.txt`
2. **Timeout Errors**: Increase `maxDuration` in `vercel.json`
3. **Memory Errors**: Optimize model loading and caching
4. **Environment Variables**: Double-check all API keys are set

### Debug Commands:
```bash
# View deployment logs
vercel logs

# Redeploy with debug info
vercel --debug

# Check function status
vercel ls
```

## 📊 Performance Optimization

### For Production:
1. **Use Edge Functions** for faster responses
2. **Implement caching** for frequently asked questions
3. **Optimize model loading** with lazy initialization
4. **Monitor function performance** in Vercel dashboard

## 🌟 Benefits of Vercel Deployment

✅ **Global CDN**: Fast responses worldwide  
✅ **Auto-scaling**: Handles traffic spikes automatically  
✅ **Zero downtime**: Automatic deployments  
✅ **Built-in monitoring**: Performance insights  
✅ **Cost-effective**: Pay per request  

## 🔗 Next Steps

After deployment:
1. **Test all endpoints** thoroughly
2. **Update frontend URLs** to point to Vercel
3. **Monitor performance** in Vercel dashboard
4. **Set up custom domain** if needed
5. **Configure webhooks** for automatic deployments

---

**Ready to deploy GANI on Vercel?** 🚀 Follow these steps and your intelligent RAG chatbot will be live on the web!
