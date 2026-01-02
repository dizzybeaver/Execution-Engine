# platforms-Master-Index-of-Indexes.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Master index for platforms domain  
**Domain:** Platforms (Platform-Specific Knowledge)  
**Status:** Empty (ready for import)

---

## 📊 OVERVIEW

This domain contains **platform-specific knowledge** for cloud providers, services, and execution environments.

**Current Status:** Empty - ready for platform imports

---

## ☁️ SUPPORTED PLATFORMS

### Structure
```
/sima/platforms/
├── {platform}/
│   ├── {service}/
│   │   ├── core/            # Core concepts
│   │   ├── anti-patterns/   # Service anti-patterns
│   │   ├── decisions/       # Service decisions
│   │   └── lessons/         # Service lessons
│   └── {platform}-Index.md
```

**Status:** No platforms imported yet

---

## 📂 EXPECTED PLATFORMS

### AWS (Amazon Web Services)
**Path:** `/sima/platforms/aws/`  
**Status:** Not yet imported

**Expected Services:**
- Lambda (serverless functions)
- API Gateway (API management)
- DynamoDB (NoSQL database)
- S3 (object storage)
- CloudWatch (monitoring)
- SSM (parameter store)
- IAM (security/permissions)

**Expected Content:**
- Service constraints
- Best practices
- Cost optimization
- Integration patterns
- Performance tuning
- Security patterns

---

### Azure
**Path:** `/sima/platforms/azure/`  
**Status:** Not yet imported

**Expected Services:**
- Azure Functions
- App Service
- Cosmos DB
- Blob Storage
- Application Insights
- Key Vault

---

### GCP (Google Cloud Platform)
**Path:** `/sima/platforms/gcp/`  
**Status:** Not yet imported

**Expected Services:**
- Cloud Functions
- Cloud Run
- Firestore
- Cloud Storage
- Cloud Monitoring
- Secret Manager

---

### Other Platforms
**Add as needed:**
- Kubernetes
- Docker
- Heroku
- Vercel
- Netlify

---

## 🎯 CONTENT RULES

### What Belongs Here
✅ Platform-specific features  
✅ Service constraints  
✅ Platform limitations  
✅ Integration patterns  
✅ Cost considerations  
✅ Performance characteristics  

### What Does NOT Belong
❌ Universal patterns (→ generic/)  
❌ Language-specific code (→ languages/)  
❌ Project implementations (→ projects/)  
❌ Tool-agnostic patterns  

---

## 📥 IMPORT GUIDELINES

When importing platform knowledge:
1. **Create platform directory** if not exists
2. **Organize by service** (Lambda, DynamoDB, etc.)
3. **Keep platform-specific** (no generic content)
4. **Document constraints** clearly
5. **Index immediately** after adding entries
6. **Cross-reference** with generic + language knowledge

---

## 🔍 NAVIGATION

### By Platform
Browse platform-specific index for each cloud provider

### By Service
- Serverless (Lambda, Functions, Cloud Run)
- Databases (DynamoDB, Cosmos DB, Firestore)
- Storage (S3, Blob Storage, Cloud Storage)
- Monitoring (CloudWatch, Application Insights)
- Security (IAM, Key Vault, Secret Manager)

### By Router
Use [platforms-Router.md](/sima/platforms/platforms-Router.md) for topic-based navigation

---

## 📈 STATISTICS

**Total Platforms:** 0  
**Total Services:** 0  
**Total Entries:** 0  

**By Platform:**
- AWS: 0 entries
- Azure: 0 entries
- GCP: 0 entries

**By Category:**
- Core Concepts: 0
- Anti-Patterns: 0
- Decisions: 0
- Lessons: 0

---

## ✅ QUALITY STANDARDS

All platform entries must:
- Be platform-specific (not universal)
- Follow file standards (≤400 lines, UTF-8, LF)
- Include proper headers
- Use REF-IDs with platform prefix (AWS-Lambda-LESS-##)
- Document version/service tiers
- Reference constraints explicitly
- Have 4-8 keywords
- Link 3-7 related topics

---

## 🔗 RELATED FILES

- **Router:** [platforms-Router.md](/sima/platforms/platforms-Router.md)
- **Generic Knowledge:** [generic-Master-Index-of-Indexes.md](/sima/generic/generic-Master-Index-of-Indexes.md)
- **Languages:** [languages-Master-Index-of-Indexes.md](/sima/languages/languages-Master-Index-of-Indexes.md)
- **Navigation:** [SIMA-Navigation-Hub.md](/sima/SIMA-Navigation-Hub.md)

---

**END OF PLATFORMS MASTER INDEX**

**Domain:** Platforms (Platform-Specific)  
**Status:** Empty (ready for import)  
**Platforms:** 0 (awaiting import)  
**Next Step:** Import first platform knowledge