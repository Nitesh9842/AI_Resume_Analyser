# Docker Deployment Guide

## For Hugging Face Spaces

### Prerequisites
- Docker installed on your machine
- Hugging Face account

### Local Testing

1. **Build the Docker image:**
   ```bash
   docker build -t ai-resume-analyzer .
   ```

2. **Run the container locally:**
   ```bash
   docker run -p 7860:7860 ai-resume-analyzer
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:7860`

### Deploying to Hugging Face Spaces

#### Option 1: Using Docker on Hugging Face Spaces

1. **Create a new Space on Hugging Face:**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose "Docker" as the SDK
   - Name your space and set it to Public or Private

2. **Push your code to the Space repository:**
   ```bash
   # Clone your space repository
   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   cd YOUR_SPACE_NAME
   
   # Copy your files
   cp -r /path/to/your/app/* .
   
   # Commit and push
   git add .
   git commit -m "Initial commit"
   git push
   ```

3. **Hugging Face will automatically build and deploy your Docker container.**

#### Option 2: Direct Git Push

If your code is already in a git repository:

```bash
# Add Hugging Face as a remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME

# Push to Hugging Face
git push hf main
```

### Environment Variables

If your app requires environment variables (API keys, etc.), set them in your Hugging Face Space settings:

1. Go to your Space settings
2. Navigate to "Variables and secrets"
3. Add your environment variables

### Important Notes

- Hugging Face Spaces uses port **7860** by default for Docker containers
- The Dockerfile is configured to expose port 7860
- Maximum file size for Spaces is typically 5GB
- Free tier has resource limitations (CPU/RAM)

### Troubleshooting

**Build fails due to memory:**
- Reduce dependencies in requirements.txt
- Use lighter model versions
- Consider using Gradio SDK instead of Docker

**Port issues:**
- Ensure your app binds to `0.0.0.0:7860`
- Check that EXPOSE directive matches the port

**Dependencies fail to install:**
- Update requirements.txt versions
- Add system dependencies to Dockerfile if needed

### Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Docker Documentation](https://docs.docker.com/)
