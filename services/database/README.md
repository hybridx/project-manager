# MongoDB Setup for Project Manager

This directory contains a complete MongoDB setup using Podman containers, designed for the AI Project Manager system.

## 🚀 Quick Start

### Prerequisites
- **Podman** installed on your system
- **podman-compose** plugin or standalone tool

### Installation Steps

1. **Install Podman**:
   ```bash
   # macOS
   brew install podman podman-compose
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install podman podman-compose
   
   # RHEL/CentOS/Fedora
   sudo dnf install podman podman-compose
   ```

2. **Navigate to Database Directory**:
   ```bash
   cd services/database
   ```

3. **Start MongoDB Services**:
   ```bash
   # Method 1: Using the management script (recommended)
   ./manage.sh start
   
   # Method 2: Using podman-compose directly
   podman-compose up -d
   
   # Method 3: Start only MongoDB (no web admin)
   ./manage.sh start --no-admin
   ```

4. **Verify Installation**:
   ```bash
   # Check service status
   ./manage.sh status
   
   # Check health
   ./manage.sh health
   
   # View logs
   ./manage.sh logs
   ```

### Access MongoDB
- **MongoDB**: `mongodb://localhost:27017`
- **Web Admin**: http://localhost:8081 (admin/admin)

### Default Credentials
- **Root User**: admin / projectmanager123
- **App User**: app_user / app_password
- **Database**: project_manager

### Stop Services
```bash
# Using management script
./manage.sh stop

# Using podman-compose
podman-compose down
```

## 📁 File Structure

```
services/database/
├── Containerfile           # MongoDB container with custom setup
├── mongod.conf             # MongoDB configuration
├── docker-entrypoint.sh    # Custom initialization script
├── podman-compose.yml      # Podman Compose configuration
├── backup.sh               # Automated backup script
├── restore.sh              # Database restore script
├── manage.sh               # Management utility script
├── backups/                # Backup storage directory
└── README.md              # This file
```

## 🗄️ Database Schema

The MongoDB instance is automatically initialized with these collections:

### Collections
- **users**: User accounts and profiles
- **projects**: Project information and metadata
- **documents**: Uploaded documents and content
- **epics**: Generated epics from AI processing
- **stories**: User stories derived from epics

### Sample Data
- Admin user: admin@projectmanager.com
- Regular user: user@projectmanager.com

## 🔧 Configuration

### Environment Variables
The following environment variables are configured in the `podman-compose.yml` file:
```yaml
environment:
  - MONGO_INITDB_ROOT_USERNAME=admin
  - MONGO_INITDB_ROOT_PASSWORD=projectmanager123
  - MONGO_INITDB_DATABASE=project_manager
```

To customize these values, edit the `podman-compose.yml` file directly.

### MongoDB Configuration
The `mongod.conf` file includes:
- Performance optimizations
- Security settings
- Logging configuration
- Index configurations

## 🛠️ Management Commands

### Using the Management Script (Recommended)
The `manage.sh` script provides a convenient way to manage all MongoDB operations:

```bash
# Start MongoDB with web admin interface
./manage.sh start

# Start only MongoDB (no web admin)
./manage.sh start --no-admin

# Stop all services
./manage.sh stop

# Restart services
./manage.sh restart

# View status
./manage.sh status

# View logs (follow mode)
./manage.sh logs -f

# Connect to MongoDB shell
./manage.sh shell

# Create backup
./manage.sh backup

# Restore from backup
./manage.sh restore mongodb_backup_20240101_120000.gz

# Check health
./manage.sh health

# Show real-time stats
./manage.sh monitor

# List collections
./manage.sh collections

# List users
./manage.sh users

# Show help
./manage.sh help
```

### Direct Podman Commands
```bash
# Start all services
podman-compose up -d

# Stop all services
podman-compose down

# View logs
podman-compose logs -f mongodb

# Check status
podman-compose ps
```

### Database Operations
```bash
# Connect to MongoDB shell
podman exec -it project-manager-mongodb mongo -u admin -p projectmanager123 --authenticationDatabase admin

# View database collections
podman exec -it project-manager-mongodb mongo -u admin -p projectmanager123 --authenticationDatabase admin --eval "use project_manager; db.getCollectionNames()"
```

## 💾 Backup & Restore

### Automatic Backups
```bash
# Run backup (creates timestamped backup in ./backups/)
./backup.sh

# Set up daily backups via cron
0 2 * * * /path/to/project-manager/services/database/backup.sh
```

### Restore Database
```bash
# List available backups
ls -la backups/

# Restore from backup
./restore.sh mongodb_backup_20240101_120000.gz
```

### Backup Features
- Compressed backups (gzip)
- Automatic cleanup (7-day retention)
- Timestamped filenames
- Size reporting

## 🔒 Security

### Authentication
- Root user for administration
- Application user with limited permissions
- Database-specific access control

### Network Security
- Bind to all interfaces for container access
- Authentication required for all connections
- TLS ready (uncomment in mongod.conf)

## 📊 Monitoring

### Health Checks
```bash
# Check container health
podman inspect project-manager-mongodb | grep -A 10 Health

# Manual health check
podman exec project-manager-mongodb mongo --eval "db.adminCommand('ping')"
```

### Performance Monitoring
```bash
# View MongoDB stats
podman exec project-manager-mongodb mongo -u admin -p projectmanager123 --authenticationDatabase admin --eval "db.stats()"

# Check slow queries
podman exec project-manager-mongodb mongo -u admin -p projectmanager123 --authenticationDatabase admin --eval "db.setProfilingLevel(1, {slowms: 100})"
```

## 🔧 Troubleshooting

### Common Issues

**Container won't start**
```bash
# Check logs
podman logs project-manager-mongodb

# Check disk space
df -h

# Remove and recreate
podman-compose down -v
podman-compose up -d
```

**Authentication issues**
```bash
# Reset to no-auth mode temporarily
podman exec project-manager-mongodb mongod --config /etc/mongod.conf --noauth
```

**Performance issues**
```bash
# Check memory usage
podman stats project-manager-mongodb

# Adjust cache size in mongod.conf
# wiredTiger.engineConfig.cacheSizeGB: 2
```

## 📈 Scaling

### Replication (Future)
Uncomment in `mongod.conf`:
```yaml
replication:
  replSetName: "rs0"
```

### Sharding (Future)
For large datasets, configure sharding:
```yaml
sharding:
  clusterRole: configsvr
```

## 🚀 Integration

### Application Connection
```javascript
// Node.js example
const MongoClient = require('mongodb').MongoClient;
const url = 'mongodb://app_user:app_password@localhost:27017/project_manager';

MongoClient.connect(url, (err, client) => {
  const db = client.db('project_manager');
  // Use database...
});
```

### Python Example
```python
from pymongo import MongoClient

client = MongoClient('mongodb://app_user:app_password@localhost:27017/project_manager')
db = client.project_manager
```

## 📋 Maintenance

### Regular Tasks
1. **Daily**: Automated backups
2. **Weekly**: Check disk usage and logs
3. **Monthly**: Review slow query log
4. **Quarterly**: Update MongoDB version

### Log Rotation
Logs are automatically rotated. Manual rotation:
```bash
podman exec project-manager-mongodb mongod --logRotate
```

## 🆘 Support

For issues:
1. Check the logs: `podman logs project-manager-mongodb`
2. Verify connectivity: `podman exec project-manager-mongodb mongo --eval "db.adminCommand('ping')"`
3. Check disk space and memory usage
4. Review MongoDB documentation for specific errors

## 📚 Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [Podman Documentation](https://podman.io/docs)
- [MongoDB Best Practices](https://docs.mongodb.com/manual/administration/production-notes/) 