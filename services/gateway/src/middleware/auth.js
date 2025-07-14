const jwt = require('jsonwebtoken');
const config = require('../config');
const logger = require('../utils/logger');
const User = require('../models/User');
const { getFromCache, setInCache } = require('../cache/redis');

/**
 * JWT Authentication Middleware
 */
const authenticate = async (req, res, next) => {
  try {
    const token = extractTokenFromRequest(req);
    
    if (!token) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'No authentication token provided'
      });
    }

    // Check if token is in cache (for faster lookup)
    const cachedUser = await getFromCache(`auth:${token}`);
    if (cachedUser) {
      req.user = JSON.parse(cachedUser);
      return next();
    }

    // Verify JWT token
    const decoded = jwt.verify(token, config.jwt.secret);
    
    // Find user in database
    const user = await User.findById(decoded.id).select('-password');
    if (!user) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'User not found'
      });
    }

    // Check if user is active
    if (!user.isActive) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'User account is deactivated'
      });
    }

    // Cache user for 5 minutes
    await setInCache(`auth:${token}`, JSON.stringify(user), 300);

    req.user = user;
    next();
  } catch (error) {
    logger.error('Authentication error:', error);
    
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        error: 'Access denied',
        message: 'Invalid token'
      });
    }
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: 'Access denied',
        message: 'Token expired'
      });
    }
    
    return res.status(500).json({
      error: 'Internal server error',
      message: 'Authentication failed'
    });
  }
};

/**
 * Optional Authentication Middleware
 * Sets user if token is valid, but doesn't block request if not
 */
const optionalAuthenticate = async (req, res, next) => {
  try {
    const token = extractTokenFromRequest(req);
    
    if (!token) {
      return next();
    }

    const decoded = jwt.verify(token, config.jwt.secret);
    const user = await User.findById(decoded.id).select('-password');
    
    if (user && user.isActive) {
      req.user = user;
    }
    
    next();
  } catch (error) {
    // Silent fail for optional authentication
    next();
  }
};

/**
 * Role-based Authorization Middleware
 */
const authorize = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'Authentication required'
      });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Insufficient permissions'
      });
    }

    next();
  };
};

/**
 * Project Access Middleware
 */
const requireProjectAccess = async (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'Authentication required'
      });
    }

    const projectId = req.params.projectId || req.body.projectId;
    
    if (!projectId) {
      return res.status(400).json({
        error: 'Bad request',
        message: 'Project ID is required'
      });
    }

    const Project = require('../models/Project');
    const project = await Project.findById(projectId);
    
    if (!project) {
      return res.status(404).json({
        error: 'Not found',
        message: 'Project not found'
      });
    }

    // Check if user is project owner, admin, or team member
    const hasAccess = 
      project.owner.toString() === req.user._id.toString() ||
      req.user.role === 'admin' ||
      project.team.some(member => member.user.toString() === req.user._id.toString());

    if (!hasAccess) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Access denied to this project'
      });
    }

    req.project = project;
    next();
  } catch (error) {
    logger.error('Project access check error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: 'Project access check failed'
    });
  }
};

/**
 * API Key Authentication Middleware
 */
const authenticateApiKey = async (req, res, next) => {
  try {
    const apiKey = req.headers['x-api-key'];
    
    if (!apiKey) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'API key required'
      });
    }

    const ApiKey = require('../models/ApiKey');
    const keyDoc = await ApiKey.findOne({ key: apiKey, isActive: true });
    
    if (!keyDoc) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'Invalid API key'
      });
    }

    // Check if key is expired
    if (keyDoc.expiresAt && keyDoc.expiresAt < new Date()) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'API key expired'
      });
    }

    // Update last used timestamp
    keyDoc.lastUsedAt = new Date();
    await keyDoc.save();

    // Get associated user
    const user = await User.findById(keyDoc.userId).select('-password');
    if (!user || !user.isActive) {
      return res.status(401).json({
        error: 'Access denied',
        message: 'Associated user not found or inactive'
      });
    }

    req.user = user;
    req.apiKey = keyDoc;
    next();
  } catch (error) {
    logger.error('API key authentication error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: 'API key authentication failed'
    });
  }
};

/**
 * Rate Limiting by User
 */
const userRateLimit = (maxRequests = 100, windowMs = 15 * 60 * 1000) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return next();
      }

      const key = `rate_limit:${req.user._id}`;
      const current = await getFromCache(key);
      
      if (current && parseInt(current) >= maxRequests) {
        return res.status(429).json({
          error: 'Too Many Requests',
          message: 'Rate limit exceeded'
        });
      }

      const count = current ? parseInt(current) + 1 : 1;
      await setInCache(key, count.toString(), Math.ceil(windowMs / 1000));
      
      next();
    } catch (error) {
      logger.error('User rate limit error:', error);
      next();
    }
  };
};

/**
 * Extract token from request
 */
function extractTokenFromRequest(req) {
  // Check Authorization header
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    return authHeader.substring(7);
  }

  // Check query parameter
  if (req.query.token) {
    return req.query.token;
  }

  // Check cookie
  if (req.cookies && req.cookies.token) {
    return req.cookies.token;
  }

  return null;
}

/**
 * Generate JWT token
 */
const generateToken = (user) => {
  const payload = {
    id: user._id,
    email: user.email,
    role: user.role
  };

  return jwt.sign(payload, config.jwt.secret, {
    expiresIn: config.jwt.expiresIn
  });
};

/**
 * Generate refresh token
 */
const generateRefreshToken = (user) => {
  const payload = {
    id: user._id,
    type: 'refresh'
  };

  return jwt.sign(payload, config.jwt.secret, {
    expiresIn: config.jwt.refreshExpiresIn
  });
};

/**
 * Verify refresh token
 */
const verifyRefreshToken = (token) => {
  try {
    const decoded = jwt.verify(token, config.jwt.secret);
    
    if (decoded.type !== 'refresh') {
      throw new Error('Invalid token type');
    }

    return decoded;
  } catch (error) {
    throw new Error('Invalid refresh token');
  }
};

/**
 * Blacklist token
 */
const blacklistToken = async (token) => {
  try {
    const decoded = jwt.decode(token);
    if (decoded && decoded.exp) {
      const ttl = decoded.exp - Math.floor(Date.now() / 1000);
      if (ttl > 0) {
        await setInCache(`blacklist:${token}`, 'true', ttl);
      }
    }
  } catch (error) {
    logger.error('Token blacklist error:', error);
  }
};

/**
 * Check if token is blacklisted
 */
const isTokenBlacklisted = async (token) => {
  try {
    const result = await getFromCache(`blacklist:${token}`);
    return result === 'true';
  } catch (error) {
    logger.error('Token blacklist check error:', error);
    return false;
  }
};

module.exports = {
  authenticate,
  optionalAuthenticate,
  authorize,
  requireProjectAccess,
  authenticateApiKey,
  userRateLimit,
  generateToken,
  generateRefreshToken,
  verifyRefreshToken,
  blacklistToken,
  isTokenBlacklisted
}; 