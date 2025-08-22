const express = require('express');
const { ApolloServer } = require('apollo-server-express');
const { gql } = require('apollo-server-express');
const { buildSubgraphSchema } = require('@apollo/subgraph');

// GraphQL Schema Definition
const typeDefs = gql`
  # User Management
  type User {
    id: ID!
    username: String!
    email: String!
    firstName: String
    lastName: String
    role: UserRole!
    status: UserStatus!
    createdAt: String!
    updatedAt: String!
    lastLoginAt: String
  }

  enum UserRole {
    ADMIN
    ANALYST
    INVESTIGATOR
    VIEWER
  }

  enum UserStatus {
    ACTIVE
    INACTIVE
    SUSPENDED
    PENDING
  }

  # Transaction Management
  type Transaction {
    id: ID!
    transactionId: String!
    amount: Float!
    currency: String!
    sourceAccount: String!
    destinationAccount: String!
    transactionType: TransactionType!
    status: TransactionStatus!
    timestamp: String!
    description: String
    riskScore: Float
    fraudIndicators: [FraudIndicator!]
  }

  enum TransactionType {
    TRANSFER
    PAYMENT
    WITHDRAWAL
    DEPOSIT
    EXCHANGE
  }

  enum TransactionStatus {
    PENDING
    COMPLETED
    FAILED
    CANCELLED
    SUSPICIOUS
  }

  # Fraud Detection
  type FraudIndicator {
    id: ID!
    type: FraudIndicatorType!
    severity: FraudSeverity!
    description: String!
    confidence: Float!
    timestamp: String!
  }

  enum FraudIndicatorType {
    UNUSUAL_AMOUNT
    UNUSUAL_FREQUENCY
    UNUSUAL_LOCATION
    UNUSUAL_TIME
    SUSPICIOUS_PATTERN
    KNOWN_FRAUDSTER
  }

  enum FraudSeverity {
    LOW
    MEDIUM
    HIGH
    CRITICAL
  }

  # Risk Assessment
  type RiskAssessment {
    id: ID!
    entityId: String!
    entityType: EntityType!
    riskScore: Float!
    riskLevel: RiskLevel!
    factors: [RiskFactor!]!
    lastUpdated: String!
  }

  enum EntityType {
    USER
    ACCOUNT
    TRANSACTION
    MERCHANT
  }

  enum RiskLevel {
    LOW
    MEDIUM
    HIGH
    CRITICAL
  }

  type RiskFactor {
    id: ID!
    factor: String!
    weight: Float!
    value: String!
    impact: Float!
  }

  # Queries
  type Query {
    # User queries
    users(
      limit: Int = 10
      offset: Int = 0
      role: UserRole
      status: UserStatus
    ): [User!]!
    user(id: ID!): User
    userByEmail(email: String!): User

    # Transaction queries
    transactions(
      limit: Int = 10
      offset: Int = 0
      status: TransactionStatus
      riskScoreMin: Float
      riskScoreMax: Float
      startDate: String
      endDate: String
    ): [Transaction!]!
    transaction(id: ID!): Transaction
    transactionsByAccount(accountNumber: String!): [Transaction!]!

    # Fraud detection queries
    fraudIndicators(
      limit: Int = 10
      offset: Int = 0
      severity: FraudSeverity
      type: FraudIndicatorType
    ): [FraudIndicator!]!
    fraudIndicatorsByTransaction(transactionId: ID!): [FraudIndicator!]!

    # Risk assessment queries
    riskAssessments(
      limit: Int = 10
      offset: Int = 0
      riskLevel: RiskLevel
      entityType: EntityType
    ): [RiskAssessment!]!
    riskAssessment(entityId: String!, entityType: EntityType!): RiskAssessment
  }

  # Mutations
  type Mutation {
    # User management
    createUser(input: CreateUserInput!): User!
    updateUser(id: ID!, input: UpdateUserInput!): User!
    deleteUser(id: ID!): Boolean!
    changeUserStatus(id: ID!, status: UserStatus!): User!

    # Transaction management
    createTransaction(input: CreateTransactionInput!): Transaction!
    updateTransaction(id: ID!, input: UpdateTransactionInput!): Transaction!
    markTransactionSuspicious(id: ID!, reason: String!): Transaction!

    # Fraud detection
    createFraudIndicator(input: CreateFraudIndicatorInput!): FraudIndicator!
    updateFraudIndicator(id: ID!, input: UpdateFraudIndicatorInput!): FraudIndicator!

    # Risk assessment
    updateRiskAssessment(entityId: String!, entityType: EntityType!, input: UpdateRiskAssessmentInput!): RiskAssessment!
  }

  # Input types
  input CreateUserInput {
    username: String!
    email: String!
    firstName: String
    lastName: String
    role: UserRole!
    password: String!
  }

  input UpdateUserInput {
    firstName: String
    lastName: String
    role: UserRole
    status: UserStatus
  }

  input CreateTransactionInput {
    amount: Float!
    currency: String!
    sourceAccount: String!
    destinationAccount: String!
    transactionType: TransactionType!
    description: String
  }

  input UpdateTransactionInput {
    status: TransactionStatus
    description: String
    riskScore: Float
  }

  input CreateFraudIndicatorInput {
    transactionId: ID!
    type: FraudIndicatorType!
    severity: FraudSeverity!
    description: String!
    confidence: Float!
  }

  input UpdateFraudIndicatorInput {
    severity: FraudSeverity
    description: String
    confidence: Float
  }

  input UpdateRiskAssessmentInput {
    riskScore: Float!
    riskLevel: RiskLevel!
    factors: [RiskFactorInput!]!
  }

  input RiskFactorInput {
    factor: String!
    weight: Float!
    value: String!
    impact: Float!
  }

  # Subscriptions
  type Subscription {
    # Real-time updates
    transactionUpdated: Transaction!
    fraudAlertCreated: FraudIndicator!
    riskScoreChanged: RiskAssessment!
    userStatusChanged: User!
  }
`;

// Mock resolvers for development
const resolvers = {
  Query: {
    // User resolvers
    users: (_, { limit, offset, role, status }) => {
      // Mock implementation - replace with actual database queries
      return [
        {
          id: '1',
          username: 'admin',
          email: 'admin@example.com',
          firstName: 'Admin',
          lastName: 'User',
          role: 'ADMIN',
          status: 'ACTIVE',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          lastLoginAt: new Date().toISOString()
        }
      ].slice(offset, offset + limit);
    },
    user: (_, { id }) => {
      return {
        id,
        username: 'user',
        email: 'user@example.com',
        firstName: 'Test',
        lastName: 'User',
        role: 'ANALYST',
        status: 'ACTIVE',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString()
      };
    },
    userByEmail: (_, { email }) => {
      return {
        id: '1',
        username: 'user',
        email,
        firstName: 'Test',
        lastName: 'User',
        role: 'ANALYST',
        status: 'ACTIVE',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString()
      };
    },

    // Transaction resolvers
    transactions: (_, { limit, offset, status, riskScoreMin, riskScoreMax, startDate, endDate }) => {
      return [
        {
          id: '1',
          transactionId: 'TXN001',
          amount: 1000.00,
          currency: 'USD',
          sourceAccount: 'ACC001',
          destinationAccount: 'ACC002',
          transactionType: 'TRANSFER',
          status: 'COMPLETED',
          timestamp: new Date().toISOString(),
          description: 'Sample transaction',
          riskScore: 0.1,
          fraudIndicators: []
        }
      ].slice(offset, offset + limit);
    },
    transaction: (_, { id }) => {
      return {
        id,
        transactionId: 'TXN001',
        amount: 1000.00,
        currency: 'USD',
        sourceAccount: 'ACC001',
        destinationAccount: 'ACC002',
        transactionType: 'TRANSFER',
        status: 'COMPLETED',
        timestamp: new Date().toISOString(),
        description: 'Sample transaction',
        riskScore: 0.1,
        fraudIndicators: []
      };
    },
    transactionsByAccount: (_, { accountNumber }) => {
      return [
        {
          id: '1',
          transactionId: 'TXN001',
          amount: 1000.00,
          currency: 'USD',
          sourceAccount: accountNumber,
          destinationAccount: 'ACC002',
          transactionType: 'TRANSFER',
          status: 'COMPLETED',
          timestamp: new Date().toISOString(),
          description: 'Sample transaction',
          riskScore: 0.1,
          fraudIndicators: []
        }
      ];
    },

    // Fraud indicator resolvers
    fraudIndicators: (_, { limit, offset, severity, type }) => {
      return [
        {
          id: '1',
          type: 'UNUSUAL_AMOUNT',
          severity: 'MEDIUM',
          description: 'Unusual transaction amount',
          confidence: 0.8,
          timestamp: new Date().toISOString()
        }
      ].slice(offset, offset + limit);
    },
    fraudIndicatorsByTransaction: (_, { transactionId }) => {
      return [
        {
          id: '1',
          type: 'UNUSUAL_AMOUNT',
          severity: 'MEDIUM',
          description: 'Unusual transaction amount',
          confidence: 0.8,
          timestamp: new Date().toISOString()
        }
      ];
    },

    // Risk assessment resolvers
    riskAssessments: (_, { limit, offset, riskLevel, entityType }) => {
      return [
        {
          id: '1',
          entityId: 'ACC001',
          entityType: 'ACCOUNT',
          riskScore: 0.3,
          riskLevel: 'LOW',
          factors: [
            {
              id: '1',
              factor: 'Transaction History',
              weight: 0.4,
              value: 'Normal',
              impact: 0.1
            }
          ],
          lastUpdated: new Date().toISOString()
        }
      ].slice(offset, offset + limit);
    },
    riskAssessment: (_, { entityId, entityType }) => {
      return {
        id: '1',
        entityId,
        entityType,
        riskScore: 0.3,
        riskLevel: 'LOW',
        factors: [
          {
            id: '1',
            factor: 'Transaction History',
            weight: 0.4,
            value: 'Normal',
            impact: 0.1
          }
        ],
        lastUpdated: new Date().toISOString()
      };
    }
  },

  Mutation: {
    // User mutations
    createUser: (_, { input }) => {
      return {
        id: '2',
        ...input,
        status: 'PENDING',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastLoginAt: null
      };
    },
    updateUser: (_, { id, input }) => {
      return {
        id,
        username: 'user',
        email: 'user@example.com',
        firstName: 'Test',
        lastName: 'User',
        role: 'ANALYST',
        status: 'ACTIVE',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString(),
        ...input
      };
    },
    deleteUser: (_, { id }) => {
      return true;
    },
    changeUserStatus: (_, { id, status }) => {
      return {
        id,
        username: 'user',
        email: 'user@example.com',
        firstName: 'Test',
        lastName: 'User',
        role: 'ANALYST',
        status,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString()
      };
    },

    // Transaction mutations
    createTransaction: (_, { input }) => {
      return {
        id: '2',
        ...input,
        status: 'PENDING',
        timestamp: new Date().toISOString(),
        riskScore: 0.0,
        fraudIndicators: []
      };
    },
    updateTransaction: (_, { id, input }) => {
      return {
        id,
        transactionId: 'TXN001',
        amount: 1000.00,
        currency: 'USD',
        sourceAccount: 'ACC001',
        destinationAccount: 'ACC002',
        transactionType: 'TRANSFER',
        status: 'COMPLETED',
        timestamp: new Date().toISOString(),
        description: 'Sample transaction',
        riskScore: 0.1,
        fraudIndicators: [],
        ...input
      };
    },
    markTransactionSuspicious: (_, { id, reason }) => {
      return {
        id,
        transactionId: 'TXN001',
        amount: 1000.00,
        currency: 'USD',
        sourceAccount: 'ACC001',
        destinationAccount: 'ACC002',
        transactionType: 'TRANSFER',
        status: 'SUSPICIOUS',
        timestamp: new Date().toISOString(),
        description: `Suspicious: ${reason}`,
        riskScore: 0.8,
        fraudIndicators: []
      };
    },

    // Fraud indicator mutations
    createFraudIndicator: (_, { input }) => {
      return {
        id: '2',
        ...input,
        timestamp: new Date().toISOString()
      };
    },
    updateFraudIndicator: (_, { id, input }) => {
      return {
        id,
        type: 'UNUSUAL_AMOUNT',
        severity: 'MEDIUM',
        description: 'Unusual transaction amount',
        confidence: 0.8,
        timestamp: new Date().toISOString(),
        ...input
      };
    },

    // Risk assessment mutations
    updateRiskAssessment: (_, { entityId, entityType, input }) => {
      return {
        id: '2',
        entityId,
        entityType,
        ...input,
        lastUpdated: new Date().toISOString()
      };
    }
  },

  Subscription: {
    transactionUpdated: {
      subscribe: () => {
        // Mock subscription - replace with actual pubsub implementation
        return {
          next: () => Promise.resolve({ value: { transactionUpdated: { id: '1' } } })
        };
      }
    },
    fraudAlertCreated: {
      subscribe: () => {
        return {
          next: () => Promise.resolve({ value: { fraudAlertCreated: { id: '1' } } })
        };
      }
    },
    riskScoreChanged: {
      subscribe: () => {
        return {
          next: () => Promise.resolve({ value: { riskScoreChanged: { id: '1' } } })
        };
      }
    },
    userStatusChanged: {
      subscribe: () => {
        return {
          next: () => Promise.resolve({ value: { userStatusChanged: { id: '1' } } })
        };
      }
    }
  }
};

// Create Apollo Server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => {
    // Add authentication context here
    return {
      user: req.user,
      isAuthenticated: !!req.user,
      headers: req.headers
    };
  },
  formatError: (error) => {
    console.error('GraphQL Error:', error);
    return {
      message: error.message,
      path: error.path,
      extensions: {
        code: error.extensions?.code || 'INTERNAL_SERVER_ERROR'
      }
    };
  },
  plugins: [
    {
      requestDidStart: () => ({
        willSendResponse: ({ response }) => {
          console.log('GraphQL Response:', {
            operationName: response.body?.singleResult?.data ? 'SUCCESS' : 'ERROR',
            timestamp: new Date().toISOString()
          });
        }
      })
    }
  ]
});

// Express middleware
const router = express.Router();

// Apply Apollo Server middleware
async function applyApolloMiddleware() {
  await server.start();
  server.applyMiddleware({ 
    app: router, 
    path: '/',
    cors: false // CORS is handled by Express
  });
}

// Initialize Apollo Server
applyApolloMiddleware().catch(console.error);

module.exports = router;
