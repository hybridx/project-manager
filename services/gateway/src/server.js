const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const rateLimit = require('express-rate-limit');
const slowDown = require('express-slow-down');
const { createServer } = require('http');
const { Server } = require('socket.io');
const swaggerUi = require('swagger-ui-express');
const swaggerJsdoc = require('swagger-jsdoc');

const config = require('./config');
const logger = require('./utils/logger');
const { connectDatabase } = require('./database/connection');
const { connectRedis } = require('./cache/redis');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');
const { requestLogger } = require('./middleware/requestLogger');
const { authenticate } = require('./middleware/auth');

// Route imports
const authRoutes = require('./routes/auth');
const projectRoutes = require('./routes/projects');
const documentRoutes = require('./routes/documents');
const aiRoutes = require('./routes/ai');
const jiraRoutes = require('./routes/jira');
const calendarRoutes = require('./routes/calendar');
const dashboardRoutes = require('./routes/dashboard');
const webhookRoutes = require('./routes/webhooks');

class Server {
  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.io = new Server(this.server, {
      cors: {
        origin: config.cors.origin,
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        credentials: true
      }
    });
    
    this.setupMiddleware();
    this.setupRoutes();
    this.setupWebSocket();
    this.setupErrorHandling();
    this.setupSwagger();
  }

  setupMiddleware() {
    // Basic middleware
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'"],
          imgSrc: ["'self'", "data:", "https:"]
        }
      }
    }));
    
    this.app.use(compression());
    this.app.use(cookieParser());
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    
    // CORS
    this.app.use(cors({
      origin: config.cors.origin,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
    }));
    
    // Logging
    this.app.use(morgan('combined', { 
      stream: { write: (message) => logger.info(message.trim()) }
    }));
    this.app.use(requestLogger);
    
    // Rate limiting
    const limiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      message: 'Too many requests from this IP, please try again later.',
      standardHeaders: true,
      legacyHeaders: false
    });
    this.app.use('/api/', limiter);
    
    // Slow down repeated requests
    const speedLimiter = slowDown({
      windowMs: 15 * 60 * 1000, // 15 minutes
      delayAfter: 50, // allow 50 requests per windowMs without delay
      delayMs: 500 // add 500ms delay per request after delayAfter
    });
    this.app.use('/api/', speedLimiter);
  }

  setupRoutes() {
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'gateway',
        version: process.env.npm_package_version || '1.0.0'
      });
    });

    // Public routes
    this.app.use('/api/auth', authRoutes);
    this.app.use('/api/webhooks', webhookRoutes);
    
    // Protected routes
    this.app.use('/api/projects', authenticate, projectRoutes);
    this.app.use('/api/documents', authenticate, documentRoutes);
    this.app.use('/api/ai', authenticate, aiRoutes);
    this.app.use('/api/jira', authenticate, jiraRoutes);
    this.app.use('/api/calendar', authenticate, calendarRoutes);
    this.app.use('/api/dashboard', authenticate, dashboardRoutes);
    
    // Serve static files for frontend
    if (config.env === 'production') {
      this.app.use(express.static('public'));
      this.app.get('*', (req, res) => {
        res.sendFile(path.join(__dirname, '../public/index.html'));
      });
    }
  }

  setupWebSocket() {
    // WebSocket authentication middleware
    this.io.use(async (socket, next) => {
      try {
        const token = socket.handshake.auth.token;
        if (!token) {
          return next(new Error('Authentication error'));
        }
        
        const jwt = require('jsonwebtoken');
        const decoded = jwt.verify(token, config.jwt.secret);
        const User = require('./models/User');
        const user = await User.findById(decoded.id);
        
        if (!user) {
          return next(new Error('User not found'));
        }
        
        socket.user = user;
        next();
      } catch (error) {
        next(new Error('Authentication error'));
      }
    });

    // WebSocket connection handling
    this.io.on('connection', (socket) => {
      logger.info(`User ${socket.user.email} connected via WebSocket`);
      
      // Join user to their personal room
      socket.join(`user:${socket.user.id}`);
      
      // Join user to their project rooms
      socket.user.projects.forEach(projectId => {
        socket.join(`project:${projectId}`);
      });
      
      // Handle document processing updates
      socket.on('subscribe-document', (documentId) => {
        socket.join(`document:${documentId}`);
        logger.info(`User ${socket.user.email} subscribed to document ${documentId}`);
      });
      
      socket.on('unsubscribe-document', (documentId) => {
        socket.leave(`document:${documentId}`);
        logger.info(`User ${socket.user.email} unsubscribed from document ${documentId}`);
      });
      
      // Handle project updates
      socket.on('subscribe-project', (projectId) => {
        socket.join(`project:${projectId}`);
        logger.info(`User ${socket.user.email} subscribed to project ${projectId}`);
      });
      
      socket.on('unsubscribe-project', (projectId) => {
        socket.leave(`project:${projectId}`);
        logger.info(`User ${socket.user.email} unsubscribed from project ${projectId}`);
      });
      
      socket.on('disconnect', () => {
        logger.info(`User ${socket.user.email} disconnected from WebSocket`);
      });
    });
  }

  setupErrorHandling() {
    this.app.use(notFoundHandler);
    this.app.use(errorHandler);
  }

  setupSwagger() {
    const swaggerOptions = {
      definition: {
        openapi: '3.0.0',
        info: {
          title: 'AI Project Management API',
          version: '1.0.0',
          description: 'API for AI-driven project management system'
        },
        servers: [
          {
            url: config.baseUrl,
            description: 'Gateway API Server'
          }
        ],
        components: {
          securitySchemes: {
            bearerAuth: {
              type: 'http',
              scheme: 'bearer',
              bearerFormat: 'JWT'
            }
          }
        }
      },
      apis: ['./src/routes/*.js', './src/models/*.js']
    };

    const swaggerSpec = swaggerJsdoc(swaggerOptions);
    this.app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
  }

  async start() {
    try {
      // Connect to database
      await connectDatabase();
      logger.info('Database connected successfully');
      
      // Connect to Redis
      await connectRedis();
      logger.info('Redis connected successfully');
      
      // Start server
      this.server.listen(config.port, () => {
        logger.info(`Gateway server running on port ${config.port}`);
        logger.info(`API documentation available at ${config.baseUrl}/api-docs`);
      });
      
      // Graceful shutdown
      process.on('SIGTERM', () => this.shutdown());
      process.on('SIGINT', () => this.shutdown());
      
    } catch (error) {
      logger.error('Failed to start server:', error);
      process.exit(1);
    }
  }

  async shutdown() {
    logger.info('Shutting down server...');
    
    // Close HTTP server
    this.server.close(() => {
      logger.info('HTTP server closed');
    });
    
    // Close WebSocket server
    this.io.close(() => {
      logger.info('WebSocket server closed');
    });
    
    // Close database connection
    const mongoose = require('mongoose');
    await mongoose.connection.close();
    logger.info('Database connection closed');
    
    // Close Redis connection
    const redis = require('./cache/redis');
    await redis.disconnect();
    logger.info('Redis connection closed');
    
    process.exit(0);
  }
}

// Create and start server
const server = new Server();
server.start();

module.exports = server; 