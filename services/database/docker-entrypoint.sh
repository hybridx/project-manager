#!/bin/bash
set -e

# MongoDB custom entrypoint for Project Manager

# Create log directory
mkdir -p /var/log/mongodb
touch /var/log/mongodb/mongod.log
chown mongodb:mongodb /var/log/mongodb/mongod.log

# Function to wait for MongoDB to be ready
wait_for_mongo() {
    echo "Waiting for MongoDB to be ready..."
    while ! mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
        sleep 1
    done
    echo "MongoDB is ready!"
}

# Function to initialize database
initialize_db() {
    echo "Initializing MongoDB database..."
    
    # Create root user
    mongo admin <<EOF
db.createUser({
    user: '${MONGO_INITDB_ROOT_USERNAME}',
    pwd: '${MONGO_INITDB_ROOT_PASSWORD}',
    roles: [
        { role: 'root', db: 'admin' }
    ]
});
EOF

    # Create application database and user
    mongo -u "${MONGO_INITDB_ROOT_USERNAME}" -p "${MONGO_INITDB_ROOT_PASSWORD}" --authenticationDatabase admin <<EOF
use ${MONGO_INITDB_DATABASE};

// Create application user
db.createUser({
    user: 'app_user',
    pwd: 'app_password',
    roles: [
        { role: 'readWrite', db: '${MONGO_INITDB_DATABASE}' }
    ]
});

// Create collections with validation
db.createCollection('users', {
    validator: {
        \$jsonSchema: {
            bsonType: 'object',
            required: ['email', 'name', 'created_at'],
            properties: {
                email: { bsonType: 'string' },
                name: { bsonType: 'string' },
                created_at: { bsonType: 'date' }
            }
        }
    }
});

db.createCollection('projects', {
    validator: {
        \$jsonSchema: {
            bsonType: 'object',
            required: ['name', 'description', 'owner_id', 'created_at'],
            properties: {
                name: { bsonType: 'string' },
                description: { bsonType: 'string' },
                owner_id: { bsonType: 'objectId' },
                created_at: { bsonType: 'date' }
            }
        }
    }
});

db.createCollection('documents', {
    validator: {
        \$jsonSchema: {
            bsonType: 'object',
            required: ['name', 'project_id', 'content', 'uploaded_at'],
            properties: {
                name: { bsonType: 'string' },
                project_id: { bsonType: 'objectId' },
                content: { bsonType: 'string' },
                uploaded_at: { bsonType: 'date' }
            }
        }
    }
});

db.createCollection('epics', {
    validator: {
        \$jsonSchema: {
            bsonType: 'object',
            required: ['title', 'project_id', 'description', 'created_at'],
            properties: {
                title: { bsonType: 'string' },
                project_id: { bsonType: 'objectId' },
                description: { bsonType: 'string' },
                created_at: { bsonType: 'date' }
            }
        }
    }
});

db.createCollection('stories', {
    validator: {
        \$jsonSchema: {
            bsonType: 'object',
            required: ['title', 'epic_id', 'description', 'created_at'],
            properties: {
                title: { bsonType: 'string' },
                epic_id: { bsonType: 'objectId' },
                description: { bsonType: 'string' },
                created_at: { bsonType: 'date' }
            }
        }
    }
});

// Create indexes for better performance
db.users.createIndex({ email: 1 }, { unique: true });
db.projects.createIndex({ owner_id: 1 });
db.projects.createIndex({ name: 'text', description: 'text' });
db.documents.createIndex({ project_id: 1 });
db.documents.createIndex({ name: 'text', content: 'text' });
db.epics.createIndex({ project_id: 1 });
db.stories.createIndex({ epic_id: 1 });

// Insert sample data
db.users.insertMany([
    {
        email: 'admin@projectmanager.com',
        name: 'Admin User',
        role: 'admin',
        created_at: new Date()
    },
    {
        email: 'user@projectmanager.com',
        name: 'Regular User',
        role: 'user',
        created_at: new Date()
    }
]);

print('Database initialized successfully!');
EOF

    echo "Database initialization completed!"
}

# Check if this is the first run
if [ ! -f /data/db/.initialized ]; then
    echo "First run detected. Starting MongoDB and initializing database..."
    
    # Start MongoDB in background
    mongod --config /etc/mongod.conf --noauth &
    MONGO_PID=$!
    
    # Wait for MongoDB to be ready
    wait_for_mongo
    
    # Initialize database
    initialize_db
    
    # Create initialization marker
    touch /data/db/.initialized
    
    # Stop MongoDB
    kill $MONGO_PID
    wait $MONGO_PID || true
    
    echo "Initialization completed. Starting MongoDB with authentication..."
fi

# Start MongoDB with authentication
exec mongod --config /etc/mongod.conf 