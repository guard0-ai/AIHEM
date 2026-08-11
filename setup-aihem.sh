#!/bin/bash

# AIHEM Quick Setup Script
# This script sets up the AIHEM vulnerable AI platform for educational purposes

set -e

echo "========================================="
echo "     AIHEM - AI Hacking Educational Module"
echo "     Quick Setup Script v1.0"
echo "========================================="
echo ""
echo "⚠️  WARNING: This creates intentionally vulnerable services!"
echo "⚠️  Only run in isolated environments for educational purposes!"
echo ""
read -p "Continue with setup? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Function to check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    echo "✅ Docker found"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    echo "✅ Docker Compose found"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    echo "✅ Python 3 found"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        echo "❌ Git is not installed. Please install Git first."
        exit 1
    fi
    echo "✅ Git found"
    
    echo ""
}

# Function to create project structure
create_project_structure() {
    echo "Creating project structure..."
    
    mkdir -p aihem/{services,frontend,deploy,challenges,docs,tools,vulnerabilities,sdk}
    
    # Create service directories
    mkdir -p aihem/services/{auth-service,chatbot-service,rag-service,agent-service,model-registry,challenge-validator}
    
    # Create frontend directories
    mkdir -p aihem/frontend/{web-app,hackpad,admin-panel}
    
    # Create deployment directories
    mkdir -p aihem/deploy/{docker,k8s}
    
    # Create challenge directories
    mkdir -p aihem/challenges/{definitions,validators,solutions}
    
    echo "✅ Project structure created"
    echo ""
}

# Function to create environment file
create_env_file() {
    echo "Creating environment configuration..."
    
    cat > aihem/deploy/docker/.env << 'EOF'
# AIHEM Environment Configuration
# ⚠️  Update these values before running!

# Shared OpenAI-compatible LLM Gateway
LLM_GATEWAY_URL=http://host.docker.internal:4000/v1
LLM_GATEWAY_MODEL=gpt-5-mini
LLM_GATEWAY_API_KEY=

# Anthropic Configuration  
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Hugging Face Configuration
HUGGINGFACE_API_KEY=hf_your_api_key_here

# Database Configuration
POSTGRES_USER=aihem
POSTGRES_PASSWORD=aihem123
POSTGRES_DB=aihem_db

# Redis Configuration
REDIS_PASSWORD=redis123

# MongoDB Configuration
MONGO_USER=admin
MONGO_PASSWORD=admin123

# MinIO Configuration
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Application Configuration
JWT_SECRET=aihem-secret-key-2024
ADMIN_API_KEY=admin123
DEBUG_MODE=true

# Resource Limits
MAX_REQUESTS_PER_MINUTE=100
MAX_TOKENS_PER_REQUEST=4096
MAX_AGENT_ITERATIONS=10

# Security Settings (intentionally weak for education)
ALLOW_CODE_EXECUTION=true
ALLOW_SYSTEM_PROMPT_OVERRIDE=true
ALLOW_ADMIN_ENDPOINTS=true
ENABLE_DEBUG_ENDPOINTS=true
EOF
    
    echo "✅ Environment file created at aihem/deploy/docker/.env"
    echo "⚠️  Please update API keys in the .env file!"
    echo ""
}

# Function to create Docker Compose file
create_docker_compose() {
    echo "Creating Docker Compose configuration..."
    
    cat > aihem/deploy/docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD}
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  auth-service:
    build: ../../services/auth-service
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://default:${REDIS_PASSWORD}@redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - DEBUG_MODE=${DEBUG_MODE}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  chatbot-service:
    build: ../../services/chatbot-service
    ports:
      - "8002:8000"
    environment:
      - LLM_GATEWAY_URL=${LLM_GATEWAY_URL}
      - LLM_GATEWAY_MODEL=${LLM_GATEWAY_MODEL}
      - LLM_GATEWAY_API_KEY=${LLM_GATEWAY_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - ALLOW_SYSTEM_PROMPT_OVERRIDE=${ALLOW_SYSTEM_PROMPT_OVERRIDE}
      - ALLOW_CODE_EXECUTION=${ALLOW_CODE_EXECUTION}
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build: ../../frontend/web-app
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8001
      - REACT_APP_DEBUG_MODE=${DEBUG_MODE}
    depends_on:
      - auth-service
      - chatbot-service

volumes:
  postgres_data:
  redis_data:
EOF
    
    echo "✅ Docker Compose file created"
    echo ""
}

# Function to create sample services
create_sample_services() {
    echo "Creating sample vulnerable services..."
    
    # Create Auth Service
    cat > aihem/services/auth-service/Dockerfile << 'EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

    cat > aihem/services/auth-service/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pyjwt==2.8.0
python-multipart==0.0.6
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
python-dotenv==1.0.0
EOF

    # Create ChatBot Service
    cat > aihem/services/chatbot-service/Dockerfile << 'EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

    cat > aihem/services/chatbot-service/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
openai==1.3.7
anthropic==0.7.7
langchain==0.0.348
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
websockets==12.0
EOF

    # Create basic frontend
    cat > aihem/frontend/web-app/Dockerfile << 'EOF'
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
EOF

    cat > aihem/frontend/web-app/package.json << 'EOF'
{
  "name": "aihem-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.2",
    "react-router-dom": "^6.20.1",
    "@mui/material": "^5.14.20"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF
    
    echo "✅ Sample services created"
    echo ""
}

# Function to create challenge definitions
create_sample_challenges() {
    echo "Creating sample challenge definitions..."
    
    cat > aihem/challenges/definitions/challenges.yaml << 'EOF'
# AIHEM Challenge Definitions

challenges:
  - id: PE-001
    name: "Jailbreak the Assistant"
    category: "Prompt Engineering"
    difficulty: "easy"
    points: 25
    description: |
      The ChatBot service has safety filters in place.
      Can you bypass them to make it reveal sensitive information?
    hints:
      - "Try role-playing as a system administrator"
      - "What if you ask about the system instructions?"
      - "Sometimes being polite helps"
    validation:
      type: "keyword_match"
      keywords: ["admin", "password", "secret"]

  - id: PE-002
    name: "System Prompt Extraction"
    category: "Prompt Engineering"
    difficulty: "easy"
    points: 30
    description: |
      Extract the complete system prompt from the assistant.
      The prompt contains secret information!
    hints:
      - "Ask the assistant to repeat its instructions"
      - "Try different phrasings"
      - "What about asking for examples?"
    validation:
      type: "contains_secret"
      secret: "AIH3M_4dm1n_2024"

  - id: DM-001
    name: "Training Data Leakage"
    category: "Data & Model"
    difficulty: "medium"
    points: 50
    description: |
      The model was trained on sensitive data.
      Can you extract PII from its training data?
    hints:
      - "Ask for specific data formats"
      - "Try common patterns like emails or phone numbers"
      - "Repetition might help"
    validation:
      type: "pii_extraction"
      min_records: 3

  - id: AG-001
    name: "Agent Tool Confusion"
    category: "Agent Security"
    difficulty: "hard"
    points: 75
    description: |
      The agent has access to multiple tools.
      Can you make it use the wrong tool for a task?
    hints:
      - "Tools have overlapping capabilities"
      - "Ambiguous instructions might confuse the agent"
      - "Try chaining multiple requests"
    validation:
      type: "tool_misuse"
      expected: "read_file"
      actual: "system_command"

  - id: IS-001
    name: "API Gateway Bypass"
    category: "Infrastructure"
    difficulty: "medium"
    points: 60
    description: |
      The API gateway has rate limiting.
      Can you bypass it to access internal endpoints?
    hints:
      - "Check for alternative endpoints"
      - "What about different HTTP methods?"
      - "Headers might help"
    validation:
      type: "endpoint_access"
      endpoint: "/admin/debug"
EOF
    
    echo "✅ Sample challenges created"
    echo ""
}

# Function to create setup instructions
create_instructions() {
    echo "Creating setup instructions..."
    
    cat > aihem/README.md << 'EOF'
# AIHEM - AI Hacking Educational Module

## ⚠️ Educational Platform - Intentionally Vulnerable

This platform contains intentionally vulnerable AI services for educational purposes only.
**DO NOT deploy in production or expose to the internet!**

## Quick Start

1. **Update Environment Variables**
   ```bash
   cd deploy/docker
   nano .env  # Add your API keys
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Access Applications**
   - Main App: http://localhost:3000
   - Auth API: http://localhost:8001/docs
   - ChatBot API: http://localhost:8002/docs

4. **Start Hacking**
   - Check `/challenges/definitions/challenges.yaml` for available challenges
   - Use the HackPad interface or API directly
   - Track your progress on the leaderboard

## Available Vulnerabilities

### OWASP LLM Top 10 (2025)
- ✅ LLM01: Prompt Injection
- ✅ LLM02: Sensitive Information Disclosure  
- ✅ LLM03: Supply Chain
- ✅ LLM04: Data/Model Poisoning
- ✅ LLM05: Improper Output Handling
- ✅ LLM06: Excessive Agency
- ✅ LLM07: System Prompt Leakage
- ✅ LLM08: Vector/Embedding Weaknesses
- ✅ LLM09: Misinformation
- ✅ LLM10: Unbounded Consumption

## Safety Guidelines

1. **Isolated Environment Only**
   - Use VMs or containers
   - Never expose to public internet
   - Use fake/synthetic data only

2. **Resource Limits**
   - Set API rate limits
   - Monitor resource usage
   - Use timeouts

3. **Educational Use**
   - For learning purposes only
   - Do not use techniques on real systems
   - Report real vulnerabilities responsibly

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## License

Apache 2.0 - See LICENSE file

## Support

- Discord: [Join our server](https://discord.gg/aihem)
- Issues: [GitHub Issues](https://github.com/yourusername/aihem/issues)
- Docs: [Documentation](https://aihem.dev/docs)

---

Made with ❤️ for the AI Security Community
EOF
    
    echo "✅ README created"
    echo ""
}

# Function to create initialization script
create_init_script() {
    echo "Creating initialization script..."
    
    cat > aihem/scripts/init.py << 'EOF'
#!/usr/bin/env python3
"""
AIHEM Initialization Script
Sets up databases and loads sample vulnerable data
"""

import os
import sys
import json
import psycopg2
import redis
from datetime import datetime

def init_postgres():
    """Initialize PostgreSQL database"""
    print("Initializing PostgreSQL...")
    
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database=os.getenv("POSTGRES_DB", "aihem_db"),
        user=os.getenv("POSTGRES_USER", "aihem"),
        password=os.getenv("POSTGRES_PASSWORD", "aihem123")
    )
    
    cur = conn.cursor()
    
    # Create users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create conversations table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            messages JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert vulnerable test data
    test_users = [
        ("admin", "5f4dcc3b5aa765d61d8327deb882cf99", "admin"),  # password
        ("user1", "5f4dcc3b5aa765d61d8327deb882cf99", "user"),   # password
        ("victim", "e10adc3949ba59abbe56e057f20f883e", "user"),  # 123456
    ]
    
    for username, password, role in test_users:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (username, password, role)
        )
    
    # Insert sensitive conversation data (for extraction challenges)
    sensitive_data = {
        "messages": [
            {
                "role": "user",
                "content": "My email is john.doe@example.com and SSN is 123-45-6789"
            },
            {
                "role": "assistant",
                "content": "I've noted your email john.doe@example.com and SSN 123-45-6789"
            }
        ]
    }
    
    cur.execute(
        "INSERT INTO conversations (user_id, messages) VALUES (1, %s)",
        (json.dumps(sensitive_data),)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ PostgreSQL initialized")

def init_redis():
    """Initialize Redis with challenge data"""
    print("Initializing Redis...")
    
    r = redis.Redis(
        host='localhost',
        port=6379,
        password=os.getenv("REDIS_PASSWORD", "redis123"),
        decode_responses=True
    )
    
    # Set up initial leaderboard
    r.set("score:admin", 1000)
    r.set("score:hacker1", 750)
    r.set("score:student1", 500)
    
    # Set up challenge metadata
    challenges = {
        "PE-001": {"solved_by": 45, "first_blood": "hacker1"},
        "PE-002": {"solved_by": 32, "first_blood": "admin"},
        "DM-001": {"solved_by": 18, "first_blood": "hacker1"},
        "AG-001": {"solved_by": 7, "first_blood": "admin"},
    }
    
    for cid, data in challenges.items():
        r.hset(f"challenge:{cid}", mapping=data)
    
    print("✅ Redis initialized")

def main():
    """Main initialization function"""
    print("=" * 50)
    print("AIHEM Initialization Script")
    print("=" * 50)
    
    try:
        init_postgres()
        init_redis()
        print("\n✅ All services initialized successfully!")
        print("\nYou can now start hacking! 🎯")
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF
    
    chmod +x aihem/scripts/init.py
    
    echo "✅ Initialization script created"
    echo ""
}

# Main setup function
main() {
    clear
    check_prerequisites
    
    echo "Starting AIHEM setup..."
    echo ""
    
    cd $(dirname "$0")
    
    create_project_structure
    create_env_file
    create_docker_compose
    create_sample_services
    create_sample_challenges
    create_instructions
    create_init_script
    
    echo "========================================="
    echo "     AIHEM Setup Complete! 🎉"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "1. cd aihem"
    echo "2. Edit deploy/docker/.env to add your API keys"
    echo "3. cd deploy/docker && docker-compose up -d"
    echo "4. python scripts/init.py"
    echo "5. Open http://localhost:3000"
    echo ""
    echo "Happy hacking! 🎯"
    echo ""
    echo "⚠️  Remember: Educational use only in isolated environments!"
}

# Run main function
main
