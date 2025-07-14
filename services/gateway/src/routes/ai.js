const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const { body, validationResult } = require('express-validator');
const router = express.Router();

const config = require('../config');
const logger = require('../utils/logger');
const { createProxyRequest } = require('../utils/serviceProxy');
const { requireProjectAccess } = require('../middleware/auth');
const { getFromCache, setInCache } = require('../cache/redis');

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = path.join(config.upload.uploadDir, 'documents');
    await fs.mkdir(uploadDir, { recursive: true });
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: config.upload.maxFileSize
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = config.upload.allowedFileTypes;
    const fileExt = path.extname(file.originalname).toLowerCase().slice(1);
    
    if (allowedTypes.includes(fileExt)) {
      cb(null, true);
    } else {
      cb(new Error(`File type .${fileExt} not allowed. Allowed types: ${allowedTypes.join(', ')}`));
    }
  }
});

/**
 * @swagger
 * /api/ai/process-document:
 *   post:
 *     summary: Process document with AI
 *     tags: [AI]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               content:
 *                 type: string
 *                 description: Document content to process
 *               documentName:
 *                 type: string
 *                 description: Name of the document
 *               documentType:
 *                 type: string
 *                 enum: [prd, rfc, requirements, feature_spec, markdown, text, unknown]
 *               projectId:
 *                 type: string
 *                 description: Associated project ID
 *               additionalContext:
 *                 type: string
 *                 description: Additional context for processing
 *     responses:
 *       200:
 *         description: Document processed successfully
 *       400:
 *         description: Bad request
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
router.post('/process-document', [
  body('content').notEmpty().withMessage('Content is required'),
  body('documentName').notEmpty().withMessage('Document name is required'),
  body('documentType').optional().isIn(['prd', 'rfc', 'requirements', 'feature_spec', 'markdown', 'text', 'unknown']),
  body('projectId').optional().isMongoId().withMessage('Invalid project ID'),
  body('additionalContext').optional().isString()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { content, documentName, documentType, projectId, additionalContext } = req.body;

    logger.info(`Processing document: ${documentName} for user: ${req.user.email}`);

    // Emit WebSocket event for document processing start
    const io = req.app.get('io');
    if (io) {
      io.to(`user:${req.user._id}`).emit('document:processing:start', {
        documentName,
        userId: req.user._id,
        timestamp: new Date().toISOString()
      });
    }

    // Create request payload
    const requestPayload = {
      content,
      document_name: documentName,
      document_type: documentType || 'unknown',
      project_id: projectId,
      additional_context: additionalContext,
      user_id: req.user._id.toString()
    };

    // Call AI processor service
    const response = await createProxyRequest(
      config.services.aiProcessor.url,
      '/process-document',
      'POST',
      requestPayload,
      {
        timeout: config.services.aiProcessor.timeout,
        retries: config.services.aiProcessor.retries
      }
    );

    // Emit WebSocket event for document processing completion
    if (io) {
      io.to(`user:${req.user._id}`).emit('document:processing:complete', {
        documentName,
        documentId: response.data.document_id,
        success: response.data.success,
        userId: req.user._id,
        timestamp: new Date().toISOString()
      });
    }

    logger.info(`Document processing completed: ${documentName} (${response.data.document_id})`);

    res.json({
      success: true,
      data: response.data
    });

  } catch (error) {
    logger.error('Document processing error:', error);

    // Emit WebSocket event for processing error
    const io = req.app.get('io');
    if (io) {
      io.to(`user:${req.user._id}`).emit('document:processing:error', {
        documentName: req.body.documentName,
        error: error.message,
        userId: req.user._id,
        timestamp: new Date().toISOString()
      });
    }

    res.status(500).json({
      error: 'Document processing failed',
      message: error.message
    });
  }
});

/**
 * @swagger
 * /api/ai/upload-document:
 *   post:
 *     summary: Upload and process document file
 *     tags: [AI]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         multipart/form-data:
 *           schema:
 *             type: object
 *             properties:
 *               file:
 *                 type: string
 *                 format: binary
 *                 description: Document file to upload
 *               projectId:
 *                 type: string
 *                 description: Associated project ID
 *     responses:
 *       200:
 *         description: Document uploaded and processed successfully
 *       400:
 *         description: Bad request
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
router.post('/upload-document', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: 'No file uploaded',
        message: 'Please select a file to upload'
      });
    }

    const { projectId } = req.body;

    logger.info(`Uploading document: ${req.file.originalname} for user: ${req.user.email}`);

    // Read file content
    const filePath = req.file.path;
    const fileContent = await fs.readFile(filePath, 'utf8');

    // Create form data for AI processor
    const FormData = require('form-data');
    const formData = new FormData();
    formData.append('file', require('fs').createReadStream(filePath));
    if (projectId) {
      formData.append('project_id', projectId);
    }
    formData.append('user_id', req.user._id.toString());

    // Call AI processor service
    const response = await createProxyRequest(
      config.services.aiProcessor.url,
      '/upload-document',
      'POST',
      formData,
      {
        timeout: config.services.aiProcessor.timeout,
        retries: config.services.aiProcessor.retries,
        headers: formData.getHeaders()
      }
    );

    // Clean up uploaded file
    await fs.unlink(filePath);

    logger.info(`Document upload completed: ${req.file.originalname} (${response.data.document_id})`);

    res.json({
      success: true,
      data: response.data
    });

  } catch (error) {
    logger.error('Document upload error:', error);

    // Clean up uploaded file on error
    if (req.file) {
      try {
        await fs.unlink(req.file.path);
      } catch (cleanupError) {
        logger.error('File cleanup error:', cleanupError);
      }
    }

    res.status(500).json({
      error: 'Document upload failed',
      message: error.message
    });
  }
});

/**
 * @swagger
 * /api/ai/generate-acceptance-criteria:
 *   post:
 *     summary: Generate acceptance criteria for user story
 *     tags: [AI]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               storyTitle:
 *                 type: string
 *                 description: User story title
 *               storyDescription:
 *                 type: string
 *                 description: User story description
 *     responses:
 *       200:
 *         description: Acceptance criteria generated successfully
 *       400:
 *         description: Bad request
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
router.post('/generate-acceptance-criteria', [
  body('storyTitle').notEmpty().withMessage('Story title is required'),
  body('storyDescription').notEmpty().withMessage('Story description is required')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { storyTitle, storyDescription } = req.body;

    // Check cache first
    const cacheKey = `acceptance_criteria:${Buffer.from(storyTitle + storyDescription).toString('base64')}`;
    const cachedResult = await getFromCache(cacheKey);
    
    if (cachedResult) {
      logger.info(`Returning cached acceptance criteria for story: ${storyTitle}`);
      return res.json({
        success: true,
        data: JSON.parse(cachedResult),
        cached: true
      });
    }

    logger.info(`Generating acceptance criteria for story: ${storyTitle}`);

    // Call AI processor service
    const response = await createProxyRequest(
      config.services.aiProcessor.url,
      '/generate-acceptance-criteria',
      'POST',
      {
        story_title: storyTitle,
        story_description: storyDescription
      },
      {
        timeout: config.services.aiProcessor.timeout,
        retries: config.services.aiProcessor.retries
      }
    );

    // Cache result for 1 hour
    await setInCache(cacheKey, JSON.stringify(response.data), 3600);

    logger.info(`Acceptance criteria generated for story: ${storyTitle}`);

    res.json({
      success: true,
      data: response.data
    });

  } catch (error) {
    logger.error('Acceptance criteria generation error:', error);
    res.status(500).json({
      error: 'Acceptance criteria generation failed',
      message: error.message
    });
  }
});

/**
 * @swagger
 * /api/ai/estimate-story-points:
 *   post:
 *     summary: Estimate story points for user story
 *     tags: [AI]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               storyTitle:
 *                 type: string
 *                 description: User story title
 *               storyDescription:
 *                 type: string
 *                 description: User story description
 *               acceptanceCriteria:
 *                 type: array
 *                 items:
 *                   type: string
 *                 description: List of acceptance criteria
 *     responses:
 *       200:
 *         description: Story points estimated successfully
 *       400:
 *         description: Bad request
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
router.post('/estimate-story-points', [
  body('storyTitle').notEmpty().withMessage('Story title is required'),
  body('storyDescription').notEmpty().withMessage('Story description is required'),
  body('acceptanceCriteria').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { storyTitle, storyDescription, acceptanceCriteria } = req.body;

    logger.info(`Estimating story points for story: ${storyTitle}`);

    // Call AI processor service
    const response = await createProxyRequest(
      config.services.aiProcessor.url,
      '/estimate-story-points',
      'POST',
      {
        story_title: storyTitle,
        story_description: storyDescription,
        acceptance_criteria: acceptanceCriteria || []
      },
      {
        timeout: config.services.aiProcessor.timeout,
        retries: config.services.aiProcessor.retries
      }
    );

    logger.info(`Story points estimated for story: ${storyTitle} (${response.data.story_points} points)`);

    res.json({
      success: true,
      data: response.data
    });

  } catch (error) {
    logger.error('Story point estimation error:', error);
    res.status(500).json({
      error: 'Story point estimation failed',
      message: error.message
    });
  }
});

/**
 * @swagger
 * /api/ai/extract-contributors:
 *   post:
 *     summary: Extract contributors from document content
 *     tags: [AI]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               content:
 *                 type: string
 *                 description: Document content to analyze
 *     responses:
 *       200:
 *         description: Contributors extracted successfully
 *       400:
 *         description: Bad request
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
router.post('/extract-contributors', [
  body('content').notEmpty().withMessage('Content is required')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { content } = req.body;

    logger.info(`Extracting contributors from document content for user: ${req.user.email}`);

    // Call AI processor service
    const response = await createProxyRequest(
      config.services.aiProcessor.url,
      '/extract-contributors',
      'POST',
      { content },
      {
        timeout: config.services.aiProcessor.timeout,
        retries: config.services.aiProcessor.retries
      }
    );

    logger.info(`Contributors extracted: ${response.data.contributors.length} found`);

    res.json({
      success: true,
      data: response.data
    });

  } catch (error) {
    logger.error('Contributors extraction error:', error);
    res.status(500).json({
      error: 'Contributors extraction failed',
      message: error.message
    });
  }
});

/**
 * @swagger
 * /api/ai/models:
 *   get:
 *     summary: Get available AI models
 *     tags: [AI]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Available models retrieved successfully
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
router.get('/models', async (req, res) => {
  try {
    logger.info(`Getting available AI models for user: ${req.user.email}`);

    // Check cache first
    const cacheKey = 'ai_models';
    const cachedModels = await getFromCache(cacheKey);
    
    if (cachedModels) {
      return res.json({
        success: true,
        data: JSON.parse(cachedModels),
        cached: true
      });
    }

    // Call AI processor service
    const response = await createProxyRequest(
      config.services.aiProcessor.url,
      '/models',
      'GET',
      null,
      {
        timeout: config.services.aiProcessor.timeout,
        retries: config.services.aiProcessor.retries
      }
    );

    // Cache result for 10 minutes
    await setInCache(cacheKey, JSON.stringify(response.data), 600);

    res.json({
      success: true,
      data: response.data
    });

  } catch (error) {
    logger.error('Get models error:', error);
    res.status(500).json({
      error: 'Failed to get available models',
      message: error.message
    });
  }
});

/**
 * @swagger
 * /api/ai/health:
 *   get:
 *     summary: Check AI service health
 *     tags: [AI]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: AI service is healthy
 *       503:
 *         description: AI service is unavailable
 */
router.get('/health', async (req, res) => {
  try {
    // Call AI processor service health check
    const response = await createProxyRequest(
      config.services.aiProcessor.url,
      '/health',
      'GET',
      null,
      {
        timeout: 5000,
        retries: 1
      }
    );

    res.json({
      success: true,
      data: response.data
    });

  } catch (error) {
    logger.error('AI service health check error:', error);
    res.status(503).json({
      error: 'AI service unavailable',
      message: error.message
    });
  }
});

module.exports = router; 