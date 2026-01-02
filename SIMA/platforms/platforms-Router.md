# platforms-Router.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Navigation router for platforms domain  
**Domain:** Platforms (Platform-Specific Knowledge)  
**Status:** Empty (ready for import)

---

## 🧭 WHAT IS THIS?

This router helps you find **platform-specific knowledge** for cloud providers and services.

**Current Status:** Empty - awaiting platform imports

---

## ☁️ SELECT YOUR PLATFORM

### AWS (Amazon Web Services)
**Path:** `/sima/platforms/aws/`  
**Status:** Not yet imported

**Key Services:**
- **Lambda** - Serverless compute
- **API Gateway** - API management
- **DynamoDB** - NoSQL database
- **S3** - Object storage
- **CloudWatch** - Monitoring
- **SSM** - Parameter store
- **IAM** - Security

**When Available:** [aws-Index.md](/sima/platforms/aws/aws-Index.md)

---

### Azure (Microsoft Azure)
**Path:** `/sima/platforms/azure/`  
**Status:** Not yet imported

**Key Services:**
- **Azure Functions** - Serverless compute
- **App Service** - Web apps
- **Cosmos DB** - NoSQL database
- **Blob Storage** - Object storage
- **Application Insights** - Monitoring
- **Key Vault** - Secrets management

**When Available:** [azure-Index.md](/sima/platforms/azure/azure-Index.md)

---

### GCP (Google Cloud Platform)
**Path:** `/sima/platforms/gcp/`  
**Status:** Not yet imported

**Key Services:**
- **Cloud Functions** - Serverless compute
- **Cloud Run** - Containerized apps
- **Firestore** - NoSQL database
- **Cloud Storage** - Object storage
- **Cloud Monitoring** - Monitoring
- **Secret Manager** - Secrets

**When Available:** [gcp-Index.md](/sima/platforms/gcp/gcp-Index.md)

---

## 🔍 SEARCH BY SERVICE TYPE

### Serverless Compute
**Platforms:**
- AWS: Lambda
- Azure: Azure Functions
- GCP: Cloud Functions, Cloud Run

**Common Topics:**
- Cold start optimization
- Memory/timeout constraints
- Execution models
- Cost optimization
- Performance tuning

**Status:** Not yet available

---

### NoSQL Databases
**Platforms:**
- AWS: DynamoDB
- Azure: Cosmos DB
- GCP: Firestore

**Common Topics:**
- Data modeling
- Query optimization
- Indexing strategies
- Consistency models
- Cost management

**Status:** Not yet available

---

### Object Storage
**Platforms:**
- AWS: S3
- Azure: Blob Storage
- GCP: Cloud Storage

**Common Topics:**
- Bucket organization
- Access patterns
- Cost optimization
- Lifecycle policies
- Security

**Status:** Not yet available

---

### Monitoring
**Platforms:**
- AWS: CloudWatch
- Azure: Application Insights
- GCP: Cloud Monitoring

**Common Topics:**
- Metrics collection
- Log aggregation
- Alerting strategies
- Performance tracking
- Cost analysis

**Status:** Not yet available

---

### Secrets Management
**Platforms:**
- AWS: SSM Parameter Store, Secrets Manager
- Azure: Key Vault
- GCP: Secret Manager

**Common Topics:**
- Secret rotation
- Access control
- Encryption
- Integration patterns
- Cost considerations

**Status:** Not yet available

---

## 📂 BROWSE BY CATEGORY

### Core Concepts
**What:** Platform/service fundamentals  
**Examples:**
- AWS Lambda execution model
- DynamoDB consistency models
- API Gateway request flow

**Status:** Empty

---

### Anti-Patterns
**What:** Platform-specific pitfalls  
**Examples:**
- Lambda threading primitives
- DynamoDB scan operations
- S3 hotspots

**Status:** Empty

---

### Decisions
**What:** Platform/service choices  
**Examples:**
- Why Lambda over EC2
- Why DynamoDB over RDS
- Provisioned vs On-Demand

**Status:** Empty

---

### Lessons
**What:** Platform-specific learnings  
**Examples:**
- Cold start optimization
- Cost surprises
- Performance bottlenecks
- Integration challenges

**Status:** Empty

---

## 🎯 COMMON QUERIES

### Constraint Questions
**Q:** "What are [service] limitations?"  
**A:** Not yet available - import knowledge first

### Cost Questions
**Q:** "How to optimize [service] costs?"  
**A:** Not yet available - import knowledge first

### Performance Questions
**Q:** "How to improve [service] performance?"  
**A:** Not yet available - import knowledge first

### Integration Questions
**Q:** "How to integrate [service A] with [service B]?"  
**A:** Not yet available - import knowledge first

---

## 🔗 NAVIGATION AIDS

### By Purpose
- Learning: Check platform documentation
- Creating: Use templates + generic patterns
- Finding: Use platform index (when available)
- Understanding: Use generic + platform knowledge

### By Mode
- General Mode: Ask platform questions
- Learning Mode: Import platform knowledge
- Project Mode: Apply platform patterns
- Debug Mode: Troubleshoot platform issues

---

## 💡 TIPS FOR PLATFORM KNOWLEDGE

**When Domain is Empty:**
1. Import from production experiences
2. Extract platform learnings
3. Document constraints
4. Create integration guides

**When Importing:**
1. Keep platform-specific
2. Document versions/tiers
3. Include constraints
4. Reference generic patterns
5. Cross-reference services

**Best Practices:**
1. One platform per directory
2. One service per subdirectory
3. Document all constraints
4. Include cost implications
5. Link related services

---

## ⚠️ REMEMBER

**Platform-specific means:**
- ✅ Service features
- ✅ Platform constraints
- ✅ Service limits
- ✅ Integration patterns

**NOT platform-specific:**
- ❌ Universal patterns (→ generic/)
- ❌ Language syntax (→ languages/)
- ❌ Project code (→ projects/)

---

## 🚀 GETTING STARTED

**Import First Platform:**
```
1. "Start SIMA Learning Mode"
2. Provide platform knowledge
3. Claude extracts patterns
4. Review generated entries
```

**Example Import:**
```
Share: AWS Lambda cold start optimization
Result: AWS-Lambda-LESS-01 created
Location: /platforms/aws/lambda/lessons/
```

---

**END OF PLATFORMS ROUTER**

**Domain:** Platforms (Platform-Specific)  
**Purpose:** Navigation and discovery  
**Status:** Empty (awaiting imports)  
**Next Step:** Import first platform knowledge