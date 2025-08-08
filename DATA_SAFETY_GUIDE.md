# Data Safety Guide for WashLink Backend

## ⚠️ IMPORTANT: Preventing Data Loss

This guide explains how to prevent accidental data deletion when running the WashLink backend.

## The Problem

The `migrate_to_mongodb.py` script was designed to clear all existing MongoDB data before migration. This caused data loss whenever:

1. Setup scripts were run (`quick-setup.sh`, `deploy-production.sh`)
2. Migration scripts were executed
3. Database initialization occurred

## Solutions Implemented

### 1. Safe Migration Script ✅

The migration script now includes a safety check:

```python
# Only clear data if explicitly requested
clear_data = os.getenv("CLEAR_MONGODB_DATA", "false").lower() == "true"
```

**To preserve data (default):**
```bash
python migrate_to_mongodb.py
```

**To clear data (only when needed):**
```bash
CLEAR_MONGODB_DATA=true python migrate_to_mongodb.py
```

### 2. Docker Volume Persistence ✅

Your `docker-compose.yml` already includes proper volume persistence:

```yaml
volumes:
  mongodb_data:/data/db
```

This ensures data survives container restarts.

## Best Practices

### ✅ DO:
- Use Docker volumes for production data
- Run backups before any migration
- Test scripts in development first
- Check environment variables before running migrations

### ❌ DON'T:
- Run migration scripts in production without backups
- Delete Docker volumes unless you want to lose data
- Run `CLEAR_MONGODB_DATA=true` in production

## Backup Commands

### Create Backup:
```bash
# Using Docker
docker exec washlink-mongodb mongodump --out /data/backup

# Direct MongoDB
mongodump --db washlink_db --out ./backup
```

### Restore Backup:
```bash
# Using Docker
docker exec washlink-mongodb mongorestore /data/backup

# Direct MongoDB
mongorestore --db washlink_db ./backup/washlink_db
```

## Troubleshooting

### If You Lost Data:
1. Check if you have Docker volumes: `docker volume ls`
2. Check if backup files exist
3. Look for database files in your system
4. Contact your hosting provider for backups

### If Data Keeps Disappearing:
1. Check if any cron jobs are running migration scripts
2. Verify no automation is calling setup scripts
3. Ensure CLEAR_MONGODB_DATA is not set to "true"
4. Check application logs for data deletion events

## Environment Variables

Add these to your `.env` file for safety:

```env
# Data Safety
CLEAR_MONGODB_DATA=false

# MongoDB Settings
MONGODB_URL=mongodb://root:example@localhost:27017/washlink_db
MONGODB_DB_NAME=washlink_db
```

## Quick Recovery

If you need to populate your database with sample data:

```bash
# Run the MongoDB setup (safe - only adds missing data)
python setup_mongodb.py

# This will create:
# - Default admin user
# - Sample laundry items
# - Basic configuration
```

---

**Remember:** Always backup your data before running any migration or setup scripts!