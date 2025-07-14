require('dotenv').config();

const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT) || 8000,
  baseUrl: process.env.BASE_URL || 'http://localhost:8000',
  
  // Database configuration
  database: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/ai-pm',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
      family: 4
    }
  },
  
  // Redis configuration
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    options: {
      retryDelayOnFailover: 100,
      enableReadyCheck: true,
      maxRetriesPerRequest: 3,
      lazyConnect: true
    }
  },
  
  // JWT configuration
  jwt: {
    secret: process.env.JWT_SECRET || 'your-secret-key-change-this-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '30d'
  },
  
  // Session configuration
  session: {
    secret: process.env.SESSION_SECRET || 'your-session-secret-change-this-in-production',
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === 'production',
      httpOnly: true,
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
  },
  
  // CORS configuration
  cors: {
    origin: process.env.CORS_ORIGIN 
      ? process.env.CORS_ORIGIN.split(',').map(url => url.trim())
      : ['http://localhost:3000', 'http://localhost:3001'],
    credentials: true
  },
  
  // Microservice endpoints
  services: {
    aiProcessor: {
      url: process.env.AI_SERVICE_URL || 'http://localhost:8001',
      timeout: parseInt(process.env.AI_SERVICE_TIMEOUT) || 300000, // 5 minutes
      retries: parseInt(process.env.AI_SERVICE_RETRIES) || 3
    },
    jiraIntegration: {
      url: process.env.JIRA_SERVICE_URL || 'http://localhost:8002',
      timeout: parseInt(process.env.JIRA_SERVICE_TIMEOUT) || 30000,
      retries: parseInt(process.env.JIRA_SERVICE_RETRIES) || 3
    },
    calendarService: {
      url: process.env.CALENDAR_SERVICE_URL || 'http://localhost:8003',
      timeout: parseInt(process.env.CALENDAR_SERVICE_TIMEOUT) || 30000,
      retries: parseInt(process.env.CALENDAR_SERVICE_RETRIES) || 3
    }
  },
  
  // File upload configuration
  upload: {
    maxFileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024, // 10MB
    allowedFileTypes: (process.env.ALLOWED_FILE_TYPES || 'pdf,doc,docx,txt,md').split(','),
    uploadDir: process.env.UPLOAD_DIR || './uploads'
  },
  
  // Email configuration
  email: {
    host: process.env.EMAIL_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.EMAIL_PORT) || 587,
    secure: process.env.EMAIL_SECURE === 'true',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    },
    from: process.env.EMAIL_FROM || 'noreply@ai-pm.com'
  },
  
  // OAuth configuration
  oauth: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      redirectUri: process.env.GOOGLE_REDIRECT_URI || 'http://localhost:8000/api/auth/google/callback'
    },
    jira: {
      clientId: process.env.JIRA_CLIENT_ID,
      clientSecret: process.env.JIRA_CLIENT_SECRET,
      redirectUri: process.env.JIRA_REDIRECT_URI || 'http://localhost:8000/api/auth/jira/callback'
    }
  },
  
  // Rate limiting configuration
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) || 15 * 60 * 1000, // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX) || 100,
    skipSuccessfulRequests: process.env.RATE_LIMIT_SKIP_SUCCESS === 'true',
    skipFailedRequests: process.env.RATE_LIMIT_SKIP_FAILED === 'true'
  },
  
  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'combined',
    file: {
      enabled: process.env.LOG_FILE_ENABLED === 'true',
      filename: process.env.LOG_FILE_NAME || 'gateway.log',
      maxsize: parseInt(process.env.LOG_MAX_SIZE) || 10 * 1024 * 1024, // 10MB
      maxFiles: parseInt(process.env.LOG_MAX_FILES) || 5
    }
  },
  
  // Cache configuration
  cache: {
    ttl: parseInt(process.env.CACHE_TTL) || 3600, // 1 hour
    checkPeriod: parseInt(process.env.CACHE_CHECK_PERIOD) || 600, // 10 minutes
    maxKeys: parseInt(process.env.CACHE_MAX_KEYS) || 1000
  },
  
  // Security configuration
  security: {
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS) || 12,
    passwordMinLength: parseInt(process.env.PASSWORD_MIN_LENGTH) || 8,
    accountLockoutTime: parseInt(process.env.ACCOUNT_LOCKOUT_TIME) || 30 * 60 * 1000, // 30 minutes
    maxLoginAttempts: parseInt(process.env.MAX_LOGIN_ATTEMPTS) || 5,
    sessionTimeout: parseInt(process.env.SESSION_TIMEOUT) || 24 * 60 * 60 * 1000 // 24 hours
  },
  
  // Webhook configuration
  webhooks: {
    jira: {
      secret: process.env.JIRA_WEBHOOK_SECRET,
      enabled: process.env.JIRA_WEBHOOK_ENABLED === 'true'
    },
    github: {
      secret: process.env.GITHUB_WEBHOOK_SECRET,
      enabled: process.env.GITHUB_WEBHOOK_ENABLED === 'true'
    }
  },
  
  // Feature flags
  features: {
    realTimeUpdates: process.env.FEATURE_REAL_TIME_UPDATES !== 'false',
    aiProcessing: process.env.FEATURE_AI_PROCESSING !== 'false',
    jiraIntegration: process.env.FEATURE_JIRA_INTEGRATION !== 'false',
    calendarIntegration: process.env.FEATURE_CALENDAR_INTEGRATION !== 'false',
    emailNotifications: process.env.FEATURE_EMAIL_NOTIFICATIONS !== 'false',
    fileUpload: process.env.FEATURE_FILE_UPLOAD !== 'false',
    analytics: process.env.FEATURE_ANALYTICS !== 'false',
    auditLog: process.env.FEATURE_AUDIT_LOG !== 'false'
  }
};

// Validation
const requiredEnvVars = [
  'JWT_SECRET',
  'SESSION_SECRET'
];

const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

if (missingEnvVars.length > 0 && config.env === 'production') {
  console.error('Missing required environment variables:', missingEnvVars);
  process.exit(1);
}

// Warn about default values in production
if (config.env === 'production') {
  const warnings = [];
  
  if (config.jwt.secret === 'your-secret-key-change-this-in-production') {
    warnings.push('Using default JWT secret');
  }
  
  if (config.session.secret === 'your-session-secret-change-this-in-production') {
    warnings.push('Using default session secret');
  }
  
  if (warnings.length > 0) {
    console.warn('Production warnings:', warnings);
  }
}

module.exports = config; 