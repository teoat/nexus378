const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Mock user database for development
const mockUsers = [
  {
    id: '1',
    username: 'admin',
    email: 'admin@example.com',
    password: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2uheWG/igi.',
    role: 'ADMIN',
    status: 'ACTIVE',
    permissions: ['read', 'write', 'delete', 'admin']
  }
];

/**
 * Authentication middleware
 * Verifies JWT token and adds user to request object
 */
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      return res.status(401).json({
        error: 'Access denied. No token provided.',
        code: 'NO_TOKEN'
      });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');
    
    // Check if user exists and is active
    const user = mockUsers.find(u => u.id === decoded.id && u.status === 'ACTIVE');
    if (!user) {
      return res.status(401).json({
        error: 'User not found or inactive.',
        code: 'USER_INACTIVE'
      });
    }

    // Add user to request object
    req.user = {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role,
      permissions: user.permissions
    };

    next();
  } catch (error) {
    return res.status(401).json({
      error: 'Invalid token.',
      code: 'INVALID_TOKEN'
    });
  }
};

/**
 * Role-based access control middleware
 */
const requireRole = (allowedRoles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        error: 'Authentication required.',
        code: 'AUTH_REQUIRED'
      });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({
        error: 'Insufficient permissions.',
        code: 'INSUFFICIENT_PERMISSIONS'
      });
    }

    next();
  };
};

/**
 * Login endpoint handler
 */
const login = async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({
        error: 'Username and password are required.',
        code: 'MISSING_CREDENTIALS'
      });
    }

    // Find user
    const user = mockUsers.find(u => u.username === username);
    if (!user || user.status !== 'ACTIVE') {
      return res.status(401).json({
        error: 'Invalid credentials.',
        code: 'INVALID_CREDENTIALS'
      });
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({
        error: 'Invalid credentials.',
        code: 'INVALID_CREDENTIALS'
      });
    }

    // Generate token
    const token = jwt.sign(
      { id: user.id, username: user.username, role: user.role },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          role: user.role,
          permissions: user.permissions
        },
        token
      }
    });

  } catch (error) {
    res.status(500).json({
      error: 'Login failed.',
      code: 'LOGIN_ERROR'
    });
  }
};

module.exports = {
  authenticateToken,
  requireRole,
  login
};
