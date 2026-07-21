# 🎯 AIHEM - AI Hacking Educational Module

<div align="center">

![AIHEM Logo](https://img.shields.io/badge/AIHEM-v1.0.0-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)
![Status](https://img.shields.io/badge/status-educational-orange)
![Security](https://img.shields.io/badge/security-intentionally_vulnerable-red)

**The Comprehensive Platform for AI Security Education**

[Quick Start](#-quick-start) • [Documentation](#-documentation) • [Challenges](#-challenges) • [Contributing](#-contributing)

</div>

---

## ⚠️ CRITICAL WARNING

**This platform contains INTENTIONALLY VULNERABLE AI services for educational purposes only.**

- ❌ **DO NOT deploy to production**
- ❌ **DO NOT expose to the public internet**
- ❌ **DO NOT use with real data**
- ✅ **USE ONLY in isolated, sandboxed environments**
- ✅ **FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY**

---

## 📖 What is AIHEM?

AIHEM (AI Hacking Educational Module) is an intentionally vulnerable AI application platform designed to educate developers, security professionals, and AI practitioners about AI/LLM security vulnerabilities through hands-on exploitation.

Inspired by OWASP's crAPI and WebGoat, AIHEM provides a safe, realistic environment where you can:

- 🎓 **Learn** about AI security vulnerabilities (OWASP LLM Top 10)
- 🔍 **Discover** real-world attack patterns (MITRE ATLAS)
- 🛠️ **Practice** exploitation techniques safely
- 🏆 **Compete** on leaderboards and earn achievements
- 📚 **Master** AI security best practices

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (or `docker compose` command)
- 4GB+ RAM (lightweight services, no heavy ML dependencies!)
- OpenAI API key (optional - only for ChatBot & Agent services)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/JBAhire/AIHEM.git
   cd AIHEM
   ```

2. **Configure environment** (Optional if you don't need ChatBot/Agent)
   ```bash
   cd deploy/docker
   cp .env.example .env 2>/dev/null || touch .env
   # Edit .env and add your OpenAI API key:
   # OPENAI_API_KEY=sk-proj-your-key-here
   ```

3. **Start the platform**
   ```bash
   # Option A: Start everything (recommended)
   docker-compose up -d

   # Option B: Start specific services only
   docker-compose up -d postgres redis auth-service rag-service frontend

   # Watch the logs
   docker-compose logs -f
   ```

4. **Verify services are healthy** (wait ~1 minute for all services)
   ```bash
   docker-compose ps
   # All services should show "healthy" or "running"

   # Test individual services
   curl http://localhost:8001/health  # Auth Service
   curl http://localhost:8003/health  # RAG Service (should return quickly!)
   ```

5. **Access the application**
   - **Main App**: http://localhost:3000 (React Frontend)
   - **Auth API**: http://localhost:8001/docs
   - **RAG API**: http://localhost:8003/docs
   - **Kong Gateway**: http://localhost:8080
   - **Grafana**: http://localhost:3003 (admin/admin)

### Quick Test - RAG Service Only

If you want to test just the RAG service first (zero dependencies!):

```bash
cd services/rag-service

# Test standalone
python test_service.py

# Or test with Docker
docker-compose -f docker-compose.test.yml up --build

# Expected output:
# ✅ Initialized system documents with secrets
# Health: {"status":"healthy","vector_store":"ready","collections":2,"total_documents":2}
```

---

## 🔧 Troubleshooting

### Services won't start

**Check Docker resources:**
```bash
docker system df  # Check disk space
docker system prune  # Clean up old containers/images
```

**Check for port conflicts:**
```bash
# Kill any process using required ports
lsof -ti:3000,8001,8003,5432,6379 | xargs kill -9  # macOS/Linux
```

**View service logs:**
```bash
cd deploy/docker
docker-compose logs -f rag-service  # Check specific service
docker-compose logs --tail=100      # Last 100 lines from all services
```

### RAG service keeps exiting

**This has been fixed!** The RAG service now has:
- ✅ Zero external dependencies (no ChromaDB, no MongoDB)
- ✅ Only 6 lightweight packages
- ✅ Starts in ~2 seconds
- ✅ Works standalone

**Test it independently:**
```bash
cd services/rag-service
python test_service.py  # Should pass all tests
```

**Still failing? Check:**
1. Python version: `python --version` (need 3.10+)
2. Docker resources: Ensure Docker has at least 4GB RAM
3. Build from scratch: `docker-compose build --no-cache rag-service`

### Frontend can't connect to API

**Check backend services are running:**
```bash
curl http://localhost:8001/health  # Auth
curl http://localhost:8003/health  # RAG
```

**Check CORS settings:**
The services have `allow_origins=["*"]` for dev, which should work.

**Check browser console:**
Open DevTools (F12) → Console tab → Look for CORS or network errors

### Database connection issues

**PostgreSQL not ready:**
```bash
docker-compose logs postgres
# Wait for: "database system is ready to accept connections"
```

**Reset databases:**
```bash
docker-compose down -v  # Warning: Deletes all data!
docker-compose up -d
```

### OpenAI API errors

**Don't have an OpenAI key?** No problem!
- Auth Service works without it ✅
- RAG Service works without it ✅
- Frontend works without it ✅
- Only ChatBot and Agent services need it

**Start without ChatBot/Agent:**
```bash
docker-compose up -d postgres redis mongodb auth-service rag-service frontend
```

### "Out of memory" errors

**Reduce services:**
```bash
# Minimal setup (frontend + auth + database)
docker-compose up -d postgres redis auth-service frontend

# Add RAG when ready
docker-compose up -d rag-service
```

**Increase Docker memory:**
- Docker Desktop → Settings → Resources → Memory → Set to 4GB+

### Need more help?

1. Check service-specific README: `services/rag-service/README.md`
2. View full logs: `docker-compose logs --tail=500 > logs.txt`
3. Check Docker status: `docker-compose ps`
4. Create an issue with logs on GitHub

---

## 🎯 Challenges - 33 AI Security Challenges

AIHEM features **33 comprehensive challenges** covering all **OWASP LLM Top 10** categories plus advanced AI attacks!

### 📊 Challenge Statistics

| Category | Count | Total Points |
|----------|-------|--------------|
| Prompt Injection (LLM01) | 6 | 425 pts |
| Insecure Output Handling (LLM02) | 2 | 270 pts |
| Training Data Poisoning (LLM03) | 2 | 300 pts |
| Model Denial of Service (LLM04) | 2 | 150 pts |
| Supply Chain Vulnerabilities (LLM05) | 2 | 290 pts |
| Sensitive Information Disclosure (LLM06) | 4 | 370 pts |
| Insecure Plugin Design (LLM07) | 2 | 235 pts |
| Excessive Agency (LLM08) | 3 | 350 pts |
| Overreliance (LLM09) | 2 | 155 pts |
| Model Theft (LLM10) | 2 | 310 pts |
| Advanced AI Attacks | 6 | 975 pts |
| **TOTAL** | **33** | **3,825 pts** |

### 🎮 Challenge Breakdown

#### Easy Challenges (🟢 25-50 pts)
- **PE-001**: Jailbreak the Assistant - Extract admin password via prompt injection
- **PE-002**: System Prompt Heist - Steal complete system prompt with credentials
- **PE-003**: Indirect Injection Attack - Poison RAG knowledge base
- **IS-001**: API Gateway Bypass - Exploit Kong misconfigurations

#### Medium Challenges (🟡 40-80 pts)
- **DM-001**: Training Data Extraction - Extract PII via SQL injection
- **DM-002**: Model Poisoning - Corrupt model behavior via feedback
- **AG-001**: Tool Confusion Attack - Manipulate agent tool selection
- **LLM01-ADV-003**: Emotional Manipulation Jailbreak
- **LLM04-ADV-001**: Resource Exhaustion via Recursive Prompts
- **LLM09-ADV-001**: Authoritative Misinformation Injection

#### Hard Challenges (🟠 70-150 pts)
- **LLM01-ADV-001**: Multi-Layer Prompt Injection (100 pts)
- **LLM02-ADV-001**: Code Injection via Markdown (120 pts)
- **LLM03-ADV-002**: Data Poisoning via User Feedback (100 pts)
- **LLM04-ADV-002**: Context Window Overflow Attack (90 pts)
- **LLM05-ADV-002**: Dependency Confusion (110 pts)
- **LLM06-ADV-002**: API Key Extraction (100 pts)
- **LLM07-ADV-002**: Cross-Plugin Data Leakage (95 pts)
- **LLM08-ADV-002**: Tool Confusion Multi-Agent (115 pts)
- **LLM09-ADV-002**: Decision Manipulation (85 pts)
- **LLM10-ADV-002**: Membership Inference Attack (120 pts)

#### Expert Challenges (🔴 140-200 pts)
- **LLM01-ADV-002**: Indirect Prompt Injection via RAG (150 pts) ⭐
- **LLM02-ADV-002**: SQL Injection via AI Generated Queries (150 pts) ⭐
- **LLM03-ADV-001**: Backdoor Injection in Fine-tuning (200 pts) 🏆
- **LLM05-ADV-001**: Malicious Model Registry Injection (180 pts)
- **LLM06-ADV-001**: Training Data Extraction Attack (160 pts)
- **LLM07-ADV-001**: Plugin Privilege Escalation (140 pts)
- **LLM08-ADV-001**: Autonomous Agent Manipulation (170 pts)
- **LLM10-ADV-001**: Model Extraction via Query Analysis (190 pts)
- **ADV-001**: Adversarial Example Generation (160 pts)
- **ADV-002**: Model Inversion Attack (175 pts)
- **ADV-003**: Gradient Leakage in Federated Learning (185 pts)
- **ADV-004**: Watermark Removal from AI Models (155 pts)
- **ADV-005**: Side Channel Timing Attack (140 pts)

### 📖 Detailed Walkthroughs

For detailed exploitation techniques, see [CHALLENGES_WALKTHROUGH.md](CHALLENGES_WALKTHROUGH.md)

**Quick Access:**
- View all challenges: http://localhost:3000/challenges
- Challenge API: http://localhost:8006/challenges
- Leaderboard: http://localhost:8006/leaderboard
- Your progress: http://localhost:8006/progress/{username}

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [CHALLENGES_WALKTHROUGH.md](CHALLENGES_WALKTHROUGH.md) | **⭐ Complete exploitation guide for all 33 challenges** |
| [VULNERABILITY_ARCHITECTURE.md](VULNERABILITY_ARCHITECTURE.md) | **Technical vulnerability mapping across services** |
| [AIHEM_Project_Plan.md](AIHEM_Project_Plan.md) | Complete project strategy |
| [AIHEM_Implementation_Guide.md](AIHEM_Implementation_Guide.md) | Technical implementation details |
| [AIHEM_Security_Researcher_Guide.md](AIHEM_Security_Researcher_Guide.md) | Attack methodologies & research |

---

## 🛠️ Architecture

```
Frontend (React)        API Gateway (Kong)       Backend Services
├─ Main App :3000       └─ Proxy :8080          ├─ Auth :8001
├─ HackPad :3001        └─ Admin :8081          ├─ ChatBot :8002
└─ Admin :3002                                  ├─ RAG :8003 (In-Memory!)
                                                ├─ Agent :8004
Data Stores             Monitoring              ├─ Model Registry :8005
├─ PostgreSQL :5432     ├─ Prometheus :9090     └─ Challenges :8006
├─ MongoDB :27017       └─ Grafana :3003
├─ Redis :6379
└─ MinIO :9000
```

**Note:** RAG service uses lightweight in-memory vector storage - no ChromaDB needed!

---

## 🤝 Contributing

We welcome contributions to AIHEM! Whether you're fixing bugs, adding features, or creating new challenges, your help is appreciated.

### How to Contribute

1. **Fork the repository**
2. **Create a branch** for your changes
3. **Make your changes** and test them
4. **Submit a pull request**

For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Types of Contributions

- 🐛 **Bug Fixes**: Fix real bugs (not intentional vulnerabilities)
- ✨ **New Features**: Add new functionality or improvements
- 🎯 **New Challenges**: Create new security challenges
- 📚 **Documentation**: Improve docs, add examples, fix typos
- 🎨 **UI/UX**: Enhance the frontend experience
- 🔧 **Infrastructure**: Improve deployment, CI/CD, tooling

### Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Inspired by OWASP crAPI, WebGoat, and DVWA

**Made with ❤️ for the AI Security Community**

⚠️ **Remember: Ethical hacking only! Use responsibly.** ⚠️