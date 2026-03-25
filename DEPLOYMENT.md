# Deployment Guide

## 🚀 Deployment Options

Choose the deployment method that best fits your needs.

---

## Option 1: Local Deployment (Development)

### Requirements
- Python 3.8+
- pip

### Steps

```bash
# Clone and setup
git clone https://github.com/uniccongroup/RAG-based-llm-test.git
cd RAG-based-llm-test
git checkout -b your-name

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Initialize knowledge base
python setup_kb.py

# Run application
python run.py
```

**Access**: http://localhost:8000

---

## Option 2: Docker Deployment

### Requirements
- Docker
- Docker Compose (optional)

### Steps

#### Using Docker directly:

```bash
# Build image
docker build -t uniccon-chatbot .

# Run container
docker run -d \
  -p 8000:8000 \
  -e LLM_PROVIDER=huggingface \
  -e HF_API_TOKEN=your_token \
  --name chatbot \
  uniccon-chatbot

# Check logs
docker logs -f chatbot

# Stop container
docker stop chatbot
```

#### Using Docker Compose:

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access**: http://localhost:8000

---

## Option 3: HuggingFace Spaces

### Steps

1. **Create Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Select "Docker" as the SDK
   - Name it "uniccon-chatbot"

2. **Upload Files**
   - Click "Files" → "Add file"
   - Upload all project files

3. **Add Secrets**
   - Go to Space Settings → Secrets
   - Add `HF_API_TOKEN` with your Hugging Face token
   - Add `OPENAI_API_KEY` if using OpenAI (optional)

4. **Configure**
   - Edit `.env` in the space
   - Set LLM provider and model

5. **Deploy**
   - Space auto-builds and deploys
   - Access via provided HuggingFace URL

**Pros**: Free hosting, automatic HTTPS, easy sharing  
**Cons**: Limited resources, slower startup

---

## Option 4: AWS Deployment

### Using AWS Lambda + API Gateway

```bash
# Install serverless framework
npm install -g serverless

# Deploy
serverless deploy
```

### Using AWS ECS

```bash
# Push image to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker tag uniccon-chatbot:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/uniccon-chatbot:latest
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/uniccon-chatbot:latest

# Create ECS cluster and deploy
# (Use AWS Console or AWS CLI)
```

---

## Option 5: Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/uniccon-chatbot

# Deploy
gcloud run deploy uniccon-chatbot \
  --image gcr.io/PROJECT_ID/uniccon-chatbot \
  --platform managed \
  --region us-central1 \
  --port 8000 \
  --set-env-vars LLM_PROVIDER=huggingface,HF_API_TOKEN=YOUR_TOKEN
```

**Pros**: Serverless, auto-scaling, free tier  
**Cons**: Cold start delays

---

## Option 6: Azure Container Instances

```bash
# Push to Azure Container Registry
az acr build --registry myregistry \
  --image uniccon-chatbot:latest .

# Deploy
az container create \
  --resource-group mygroup \
  --name uniccon-chatbot \
  --image myregistry.azurecr.io/uniccon-chatbot:latest \
  --ports 8000 \
  --environment-variables LLM_PROVIDER=huggingface
```

---

## Option 7: Heroku

```bash
# Install Heroku CLI
# Then deploy

heroku login
heroku create uniccon-chatbot
git push heroku main

# Set environment variables
heroku config:set LLM_PROVIDER=huggingface
heroku config:set HF_API_TOKEN=your_token

# View logs
heroku logs --tail
```

---

## Option 8: Self-Hosted (Linux VPS)

### Using Ubuntu/Debian

```bash
# SSH into server
ssh user@your_server.com

# Install dependencies
sudo apt update
sudo apt install python3.10 python3-pip nginx

# Clone and setup
git clone https://github.com/uniccongroup/RAG-based-llm-test.git
cd RAG-based-llm-test
pip install -r requirements.txt
python setup_kb.py

# Use systemd service
sudo nano /etc/systemd/system/chatbot.service
```

Create `/etc/systemd/system/chatbot.service`:
```ini
[Unit]
Description=UNICCON RAG Chatbot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/RAG-based-llm-test
ExecStart=/usr/bin/python3 run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start chatbot
sudo systemctl enable chatbot

# Check status
sudo systemctl status chatbot
```

---

## Environment Variables for Deployment

```bash
# Core Settings
APP_NAME=UNICCON RAG Chatbot
DEBUG=False
LOG_LEVEL=INFO

# LLM Configuration
LLM_PROVIDER=huggingface  # or openai, cohere
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
HF_API_TOKEN=hf_xxxxxxxxxxxx
OPENAI_API_KEY=sk_xxxxxxxxxxxx
COHERE_API_KEY=xxxxxxxxxxxx

# RAG Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=3
SIMILARITY_THRESHOLD=0.5

# Server
HOST=0.0.0.0
PORT=8000
```

---

## Performance Optimization

### For Production

1. **Use UVICORN Workers**
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

2. **Enable Caching**
   - Add Redis for response caching
   - Cache embedding generations

3. **Scale Database**
   - Use cloud vector database (Pinecone, Weaviate)
   - Implement connection pooling

4. **CDN**
   - Use CloudFlare for static content
   - Add API gateway caching

5. **Monitoring**
   - Setup error tracking (Sentry)
   - Monitor performance (New Relic, DataDog)
   - Log aggregation (ELK Stack)

---

## Domain & HTTPS

### Using Custom Domain

1. **With Docker on VPS**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Get certificate
   sudo certbot certonly -d yourdomain.com
   
   # Configure nginx
   sudo nano /etc/nginx/sites-available/default
   ```

2. **With HuggingFace Spaces**
   - Use provided `.huggingface.space` domain
   - Or connect custom domain in settings

3. **With Cloud Providers**
   - Auto-provisioned HTTPS
   - Managed certificates

---

## Continuous Deployment (CD)

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push Docker image
        run: |
          docker build -t uniccon-chatbot .
          docker tag uniccon-chatbot myregistry/uniccon-chatbot
          docker push myregistry/uniccon-chatbot
      
      - name: Deploy to production
        run: |
          # Your deployment script here
```

---

## Monitoring & Logs

### Setup Logging

```python
# Logs are stored in logs/app.log
# View logs:
tail -f logs/app.log

# On deployed server
docker logs -f chatbot
heroku logs --tail
gcloud logging read "resource.labels.service_name=chatbot" --limit 50
```

### Health Checks

```bash
# Regular health checks
curl http://your-domain/api/health

# Automated monitoring
# Setup with your cloud provider's monitoring service
```

---

## Rollback & Recovery

### Docker
```bash
# Pull previous image
docker pull myregistry/uniccon-chatbot:v1.0

# Run previous version
docker run -d -p 8000:8000 myregistry/uniccon-chatbot:v1.0
```

### Git
```bash
# Revert to previous commit
git revert HEAD
git push

# Force rollback
git reset --hard <commit-hash>
git push -f
```

---

## Troubleshooting Deployment

### Issue: Out of Memory
- Reduce `CHUNK_SIZE`
- Use smaller embedding model
- Implement batch processing

### Issue: Slow Response Time
- Add caching layer
- Use CDN for static content
- Scale horizontally

### Issue: High CPU Usage
- Reduce `TOP_K_RETRIEVAL`
- Optimize LLM calls
- Add request throttling

---

## Support & Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Docker Docs**: https://docs.docker.com
- **Deployment Guides**: Each service provides official guides

---

**Choose the deployment option that best fits your infrastructure and requirements!**
