# Backup and Recovery Plan

**Document Reference:** R-19  
**Controller:** UnGouge LLC, Vermont, USA  
**Contact:** legal@ungouge.ai  
**Date:** 2026-02-13  
**Review Date:** 2027-02-13  
**GDPR Basis:** Article 32(1)(c) — Ability to restore availability and access to personal data in a timely manner  

---

## 1. Purpose

This plan ensures UnGouge LLC can restore personal data and system availability following data loss, corruption, or infrastructure failure. It addresses the GDPR requirement under Article 32(1)(c) for the *"ability to restore the availability and access to personal data in a timely manner in the event of a physical or technical incident."*

---

## 2. System Architecture

### 2.1 Current Production Environment

| Component | Technology | Location | Data Classification |
|-----------|-----------|----------|-------------------|
| **Application** | Google Cloud Run (containerized) | Google Cloud (us-central1) | Stateless — no persistent data |
| **Database** | Cloud SQL for MySQL | Google Cloud (us-central1) | **Primary data store** — user accounts, quotes, analysis results |
| **File Storage** | Google Cloud Storage | Google Cloud (us-central1) | Uploaded quote documents (PDFs, images) |
| **AI Processing** | Google Gemini API | Google Cloud | Stateless — no persistent data retained |
| **Payments** | Stripe (planned) | Stripe infrastructure | Payment data held by Stripe as processor |
| **Secrets** | Google Secret Manager | Google Cloud | API keys, database credentials |
| **DNS/CDN** | *[Current provider]* | — | Configuration only |

### 2.2 Data Categories and Sensitivity

| Data | Location | Sensitivity | Backup Priority |
|------|----------|-------------|----------------|
| User accounts (name, email, hashed password) | Cloud SQL | High | Critical |
| Contractor quotes (uploaded files) | Cloud Storage | High | Critical |
| Analysis results | Cloud SQL | Medium | High |
| Security logs | Cloud Logging | Medium | Standard |
| Application configuration | Cloud Run / Secret Manager | High | Critical |
| Aggregate analytics | Cloud SQL | Low | Standard |

---

## 3. Backup Strategy

### 3.1 Cloud SQL (MySQL) — Automated Backups

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Automated backups** | Enabled | Google-managed, daily |
| **Backup window** | 02:00–06:00 UTC (off-peak) | Minimize performance impact |
| **Retention period** | 30 days | Sufficient for incident detection and recovery; balances GDPR minimization |
| **Point-in-time recovery (PITR)** | Enabled | Continuous binary log retention allows recovery to any point within retention window |
| **Binary log retention** | 7 days | Enables precise PITR within the most recent week |
| **Backup location** | Same region (us-central1) | Default; cross-region backup for DR — see Section 3.4 |
| **Encryption** | Google-managed encryption keys (default) | At-rest encryption for all backups |

### 3.2 Cloud Storage (Uploaded Files) — Versioning and Redundancy

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Object versioning** | Enabled | Protects against accidental deletion/overwrite |
| **Version retention** | 30 days (lifecycle rule deletes older noncurrent versions) | Consistent with database backup retention |
| **Storage class** | Standard | Frequently accessed during analysis |
| **Redundancy** | Regional (us-central1) | Multi-zone within region |
| **Cross-region backup** | Daily sync to separate region bucket — see Section 3.4 | DR protection |

### 3.3 Application Configuration

| Component | Backup Method | Frequency |
|-----------|--------------|-----------|
| Cloud Run service definitions | Infrastructure as Code (Terraform/YAML in Git) | Every change (version controlled) |
| Secret Manager secrets | Manual export procedure (encrypted) | Monthly or upon change |
| IAM policies | Terraform state / Git | Every change |
| DNS configuration | Documented in Git | Every change |

### 3.4 Disaster Recovery — Cross-Region Redundancy

For resilience against regional outages:

| Component | DR Strategy |
|-----------|------------|
| Cloud SQL | **Cross-region read replica** (us-east1) — can be promoted to primary |
| Cloud Storage | **Daily cross-region sync** to us-east1 bucket via Storage Transfer Service |
| Cloud Run | Multi-region deployment capability (container images in Artifact Registry, deployable to any region) |
| Secret Manager | Regional replication enabled |

---

## 4. Recovery Procedures

### 4.1 Scenario: Database Corruption or Data Loss

**Procedure: Point-in-Time Recovery (PITR)**

1. **Assess** — Determine the exact time before corruption/loss occurred
2. **Create clone** — Use Cloud SQL PITR to clone the instance to the target timestamp:
   ```
   gcloud sql instances clone [SOURCE_INSTANCE] [CLONE_NAME] \
     --point-in-time [TIMESTAMP]
   ```
3. **Verify** — Connect to the cloned instance and verify data integrity
4. **Validate** — Confirm the recovery point contains the expected data and no corruption
5. **Switch** — Update Cloud Run service to point to the recovered instance
6. **Test** — Run application health checks and verify user-facing functionality
7. **Decommission** — Delete the corrupted original instance after confirming recovery
8. **Re-enable backups** — Ensure automated backups are active on the new instance

**Estimated recovery time:** 15–60 minutes depending on database size.

### 4.2 Scenario: Accidental File Deletion (Cloud Storage)

**Procedure: Object Version Restore**

1. **Identify** — Determine which objects were deleted or overwritten
2. **List versions** — `gsutil ls -la gs://[BUCKET]/[OBJECT_PATH]`
3. **Restore** — Copy the desired noncurrent version to current:
   ```
   gsutil cp gs://[BUCKET]/[OBJECT]#[GENERATION] gs://[BUCKET]/[OBJECT]
   ```
4. **Verify** — Confirm restored files are accessible and intact

**Estimated recovery time:** Minutes for individual files; up to 1 hour for bulk restoration.

### 4.3 Scenario: Cloud Run Service Failure

**Procedure: Redeployment**

1. **Identify** — Determine whether the issue is the container image, configuration, or infrastructure
2. **Rollback** — Cloud Run maintains revision history:
   ```
   gcloud run services update-traffic [SERVICE] \
     --to-revisions=[PREVIOUS_REVISION]=100
   ```
3. **Verify** — Confirm service is responding correctly
4. **Investigate** — Debug the failed revision in a staging environment

**Estimated recovery time:** Under 5 minutes for revision rollback.

### 4.4 Scenario: Regional Outage (Disaster Recovery)

**Procedure: Cross-Region Failover**

1. **Confirm** — Verify the regional outage via Google Cloud Status Dashboard
2. **Promote replica** — Promote the Cloud SQL read replica in us-east1 to standalone instance
3. **Deploy application** — Deploy Cloud Run service to us-east1 using the same container image
4. **Update DNS** — Point application DNS to the new region's endpoint
5. **Verify Cloud Storage** — Confirm cross-region bucket has recent sync data
6. **Update application config** — Point to promoted database and DR storage bucket
7. **Test** — Full application verification
8. **Communicate** — Notify users of any data loss window (gap between last sync and outage)

**Estimated recovery time:** 1–4 hours.

### 4.5 Scenario: Ransomware / Complete Compromise

**Procedure: Clean Rebuild**

1. **Isolate** — Disconnect all affected systems immediately
2. **Assess** — Determine the extent of compromise (see Incident Response Plan R-13)
3. **Provision clean infrastructure** — New Cloud SQL instance, new Cloud Run service, rotated credentials
4. **Restore from backup** — Use the most recent clean backup (pre-compromise)
5. **Rotate all secrets** — API keys, database passwords, service account keys
6. **Redeploy** — Fresh container build from verified source code (Git)
7. **Verify** — Full security audit before restoring user access
8. **Notify** — Per Incident Response Plan

**Estimated recovery time:** 4–24 hours.

---

## 5. Recovery Objectives

### 5.1 Recovery Point Objective (RPO)

| Scenario | RPO Target | Mechanism |
|----------|-----------|-----------|
| Database corruption | **< 5 minutes** | Point-in-time recovery from binary logs |
| File loss | **< 24 hours** | Object versioning (immediate for overwrites/deletes) |
| Regional outage | **< 24 hours** | Daily cross-region sync |
| Complete compromise | **< 24 hours** | Daily automated backups |

### 5.2 Recovery Time Objective (RTO)

| Scenario | RTO Target | Rationale |
|----------|-----------|-----------|
| Database recovery (PITR) | **< 1 hour** | Cloud SQL clone operation + verification |
| File restoration | **< 1 hour** | Object version copy |
| Service rollback | **< 15 minutes** | Cloud Run revision routing |
| Regional failover | **< 4 hours** | Replica promotion + redeployment |
| Full rebuild | **< 24 hours** | Clean infrastructure + backup restore |

> **Context:** These targets are appropriate for a small SaaS serving individual consumers on a per-use basis. The service is not mission-critical infrastructure. Users can tolerate brief downtime. Financial impact of downtime is proportional to revenue ($19.99/use).

---

## 6. Testing Schedule

### 6.1 Quarterly Recovery Drills

**Frequency:** Every 3 months  
**Next scheduled:** *[Date]*

| Quarter | Drill Focus | Procedure |
|---------|-------------|-----------|
| Q1 | Database PITR | Clone production to a test timestamp; verify data integrity |
| Q2 | File restoration | Delete test objects; restore from versioning; verify |
| Q3 | Full DR failover simulation | Simulate regional unavailability; execute failover to DR region |
| Q4 | Complete rebuild | Provision fresh infrastructure; restore from backups; verify end-to-end |

### 6.2 Drill Procedure

1. **Schedule** — Notify team of drill date and scope
2. **Execute** — Follow the documented recovery procedure exactly as written
3. **Time** — Record actual recovery time vs. RTO target
4. **Verify** — Confirm recovered data matches expected state
5. **Document** — Record results, deviations, and lessons learned
6. **Update** — Revise procedures based on drill findings

### 6.3 Drill Documentation Template

| Field | Detail |
|-------|--------|
| Date | *[YYYY-MM-DD]* |
| Drill type | *[PITR / File restore / DR failover / Full rebuild]* |
| Participants | *[Names]* |
| Target RTO | *[From Section 5.2]* |
| Actual recovery time | *[Measured]* |
| Target RPO | *[From Section 5.1]* |
| Actual data loss | *[Measured — time gap or record count]* |
| Data integrity verified | *[Yes/No — describe verification method]* |
| Issues encountered | *[Description]* |
| Procedure updates needed | *[Description]* |
| Pass/Fail | *[Assessment]* |

---

## 7. GDPR-Specific Considerations

### 7.1 Data Minimization in Backups

- Backups contain all data in the source system, including data that may be subject to erasure requests
- **Erasure in backups:** When a data subject exercises the right to erasure (Art. 17), the data is deleted from production immediately. Backup copies will expire naturally within the 30-day retention period. This approach is consistent with ICO guidance that backups need not be individually modified, provided:
  - The backup retention period is reasonable (30 days qualifies)
  - The data would not be restored from backup into production without re-applying the erasure
  - A record is maintained of processed erasure requests to ensure they are re-applied if a backup is restored

### 7.2 Backup Access Controls

- Backup access is restricted to the same IAM roles as production database access
- All backup access is logged via Cloud Audit Logs
- Backups are encrypted at rest using Google-managed encryption
- No unencrypted copies of backups are permitted

### 7.3 Cross-Border Considerations

- All backups remain within Google Cloud US regions (us-central1, us-east1)
- No backup data is transferred outside the United States
- If EU data subjects are served in future, appropriate transfer mechanisms (Standard Contractual Clauses via Google's DPA) will apply

### 7.4 Restoration and Re-application of Compliance Actions

After any data restoration from backup, the following must be re-applied:
- [ ] Pending erasure requests (check erasure log)
- [ ] Pending data portability exports
- [ ] Account restrictions or suspensions
- [ ] Any data corrections requested under Art. 16

---

## 8. Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| **Engineering Lead** | Configure and maintain backup systems; execute recovery procedures; conduct drills |
| **Operations** | Monitor backup success/failure; escalate failures within 4 hours |
| **Legal/Compliance** | Ensure backup retention aligns with GDPR requirements; maintain erasure re-application log |
| **Incident Lead** | Authorize recovery operations during security incidents (per R-13) |

---

## 9. Monitoring and Alerts

| Check | Method | Alert Threshold |
|-------|--------|----------------|
| Cloud SQL backup completion | Cloud Monitoring | Any backup failure |
| Cloud Storage versioning | Bucket configuration audit | Versioning disabled |
| Cross-region sync | Storage Transfer Service logs | Sync failure or >24h delay |
| Binary log retention | Cloud SQL configuration audit | PITR disabled or retention changed |
| Backup encryption | Security Command Center | Encryption downgrade |

---

## 10. Plan Review

This plan is reviewed:
- **Annually** (next: 2027-02-13)
- **After every recovery drill** (update procedures based on findings)
- **After any Severity 1 or 2 incident** requiring backup restoration
- **Upon architecture changes** (new data stores, new regions, new processors)

---

*This document is maintained as part of UnGouge LLC's GDPR compliance documentation suite.*
