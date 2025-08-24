// Forensic Reconciliation + Fraud Platform - Neo4j Graph Schema
// Neo4j 5+ Initialization Script

// =============================================================================
// CREATE CONSTRAINTS AND INDEXES
// =============================================================================

// Create constraints for unique properties
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT account_id IF NOT EXISTS FOR (a:Account) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (t:Transaction) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT evidence_id IF NOT EXISTS FOR (e:Evidence) REQUIRE e.id IS UNIQUE;

// Create indexes for performance
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX person_email IF NOT EXISTS FOR (p:Person) ON (p.email);
CREATE INDEX person_phone IF NOT EXISTS FOR (p:Person) ON (p.phone);
CREATE INDEX organization_name IF NOT EXISTS FOR (o:Organization) ON (o.name);
CREATE INDEX account_number IF NOT EXISTS FOR (a:Account) ON (a.account_number);
CREATE INDEX transaction_amount IF NOT EXISTS FOR (t:Transaction) ON (t.amount);
CREATE INDEX transaction_date IF NOT EXISTS FOR (t:Transaction) ON (t.date);
CREATE INDEX case_number IF NOT EXISTS FOR (c:Case) ON (c.case_number);

// =============================================================================
// CREATE NODE LABELS AND PROPERTIES
// =============================================================================

// Person nodes - Individuals involved in cases
CREATE (p1:Person {
    id: 'person_001',
    name: 'John Smith',
    email: 'john.smith@example.com',
    phone: '+1-555-0101',
    date_of_birth: '1980-05-15',
    nationality: 'US',
    risk_score: 0.3,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (p2:Person {
    id: 'person_002',
    name: 'Jane Doe',
    email: 'jane.doe@example.com',
    phone: '+1-555-0102',
    date_of_birth: '1985-08-22',
    nationality: 'US',
    risk_score: 0.1,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (p3:Person {
    id: 'person_003',
    name: 'Robert Johnson',
    email: 'robert.johnson@example.com',
    phone: '+1-555-0103',
    date_of_birth: '1975-12-10',
    nationality: 'US',
    risk_score: 0.8,
    created_at: datetime(),
    updated_at: datetime()
});

// Organization nodes - Companies and entities
CREATE (o1:Organization {
    id: 'org_001',
    name: 'Acme Corporation',
    legal_name: 'Acme Corporation Inc.',
    tax_id: '12-3456789',
    industry: 'Technology',
    risk_score: 0.4,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (o2:Organization {
    id: 'org_002',
    name: 'Global Trading LLC',
    legal_name: 'Global Trading Limited Liability Company',
    tax_id: '98-7654321',
    industry: 'Trading',
    risk_score: 0.9,
    created_at: datetime(),
    updated_at: datetime()
});

// Account nodes - Financial accounts
CREATE (a1:Account {
    id: 'account_001',
    account_number: '1234567890',
    account_type: 'CHECKING',
    bank_name: 'First National Bank',
    balance: 50000.00,
    currency: 'USD',
    risk_score: 0.2,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (a2:Account {
    id: 'account_002',
    account_number: '0987654321',
    account_type: 'SAVINGS',
    bank_name: 'Second National Bank',
    balance: 150000.00,
    currency: 'USD',
    risk_score: 0.6,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (a3:Account {
    id: 'account_003',
    account_number: '1122334455',
    account_type: 'BUSINESS',
    bank_name: 'Third National Bank',
    balance: 750000.00,
    currency: 'USD',
    risk_score: 0.9,
    created_at: datetime(),
    updated_at: datetime()
});

// Transaction nodes - Financial transactions
CREATE (t1:Transaction {
    id: 'txn_001',
    transaction_id: 'TXN2024001',
    amount: 5000.00,
    currency: 'USD',
    transaction_type: 'TRANSFER',
    date: date('2024-01-15'),
    description: 'Business payment',
    risk_score: 0.3,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (t2:Transaction {
    id: 'txn_002',
    transaction_id: 'TXN2024002',
    amount: 25000.00,
    currency: 'USD',
    transaction_type: 'TRANSFER',
    date: date('2024-01-16'),
    description: 'Investment transfer',
    risk_score: 0.7,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (t3:Transaction {
    id: 'txn_003',
    transaction_id: 'TXN2024003',
    amount: 100000.00,
    currency: 'USD',
    transaction_type: 'TRANSFER',
    date: date('2024-01-17'),
    description: 'Large cash transfer',
    risk_score: 0.9,
    created_at: datetime(),
    updated_at: datetime()
});

// Document nodes - Evidence documents
CREATE (d1:Document {
    id: 'doc_001',
    document_id: 'DOC2024001',
    filename: 'bank_statement_jan_2024.pdf',
    document_type: 'BANK_STATEMENT',
    file_size: 2048576,
    hash_sha256: 'a1b2c3d4e5f6...',
    risk_score: 0.2,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (d2:Document {
    id: 'doc_002',
    document_id: 'DOC2024002',
    filename: 'contract_agreement.pdf',
    document_type: 'CONTRACT',
    file_size: 1048576,
    hash_sha256: 'b2c3d4e5f6a1...',
    risk_score: 0.5,
    created_at: datetime(),
    updated_at: datetime()
});

// Case nodes - Investigation cases
CREATE (c1:Case {
    id: 'case_001',
    case_number: 'CASE-2024-001',
    title: 'Suspicious Financial Activity Investigation',
    case_type: 'FINANCIAL_FRAUD',
    priority: 'HIGH',
    status: 'OPEN',
    risk_score: 0.8,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (c2:Case {
    id: 'case_002',
    case_number: 'CASE-2024-002',
    title: 'Corporate Espionage Investigation',
    case_type: 'CORPORATE_ESPIONAGE',
    priority: 'MEDIUM',
    status: 'OPEN',
    risk_score: 0.6,
    created_at: datetime(),
    updated_at: datetime()
});

// Evidence nodes - Evidence items
CREATE (e1:Evidence {
    id: 'evidence_001',
    evidence_id: 'EVID-2024-001',
    evidence_type: 'FINANCIAL_RECORD',
    description: 'Suspicious bank transfer',
    collection_date: date('2024-01-15'),
    risk_score: 0.7,
    created_at: datetime(),
    updated_at: datetime()
});

CREATE (e2:Evidence {
    id: 'evidence_002',
    evidence_id: 'EVID-2024-002',
    evidence_type: 'DOCUMENT',
    description: 'Suspicious contract',
    collection_date: date('2024-01-16'),
    risk_score: 0.5,
    created_at: datetime(),
    updated_at: datetime()
});

// =============================================================================
// CREATE RELATIONSHIPS
// =============================================================================

// Person relationships
CREATE (p1)-[:WORKS_FOR {start_date: date('2020-01-01'), position: 'CEO'}]->(o1);
CREATE (p2)-[:WORKS_FOR {start_date: date('2021-03-15'), position: 'CFO'}]->(o1);
CREATE (p3)-[:WORKS_FOR {start_date: date('2019-06-01'), position: 'Director'}]->(o2);

CREATE (p1)-[:OWNS_ACCOUNT {ownership_type: 'PRIMARY'}]->(a1);
CREATE (p2)-[:OWNS_ACCOUNT {ownership_type: 'JOINT'}]->(a1);
CREATE (p3)-[:OWNS_ACCOUNT {ownership_type: 'PRIMARY'}]->(a3);

CREATE (p1)-[:KNOWS {relationship_type: 'BUSINESS_PARTNER', since: date('2018-01-01')}]->(p3);
CREATE (p2)-[:KNOWS {relationship_type: 'COLLEAGUE', since: date('2021-03-15')}]->(p1);

// Organization relationships
CREATE (o1)-[:HAS_ACCOUNT {account_purpose: 'OPERATING'}]->(a1);
CREATE (o2)-[:HAS_ACCOUNT {account_purpose: 'TRADING'}]->(a3);

CREATE (o1)-[:PARTNERS_WITH {partnership_type: 'BUSINESS', start_date: date('2022-01-01')}]->(o2);

// Transaction relationships
CREATE (a1)-[:SENT_TRANSACTION]->(t1);
CREATE (a2)-[:RECEIVED_TRANSACTION]->(t1);
CREATE (a3)-[:SENT_TRANSACTION]->(t2);
CREATE (a1)-[:RECEIVED_TRANSACTION]->(t2);
CREATE (a3)-[:SENT_TRANSACTION]->(t3);
CREATE (a2)-[:RECEIVED_TRANSACTION]->(t3);

// Document relationships
CREATE (d1)-[:DOCUMENTS_TRANSACTION]->(t1);
CREATE (d2)-[:DOCUMENTS_TRANSACTION]->(t2);

// Case relationships
CREATE (c1)-[:INVOLVES_PERSON]->(p1);
CREATE (c1)-[:INVOLVES_PERSON]->(p3);
CREATE (c1)-[:INVOLVES_ORGANIZATION]->(o1);
CREATE (c1)-[:INVOLVES_ORGANIZATION]->(o2);
CREATE (c1)-[:INVOLVES_TRANSACTION]->(t1);
CREATE (c1)-[:INVOLVES_TRANSACTION]->(t2);
CREATE (c1)-[:INVOLVES_TRANSACTION]->(t3);

CREATE (c2)-[:INVOLVES_PERSON]->(p2);
CREATE (c2)-[:INVOLVES_ORGANIZATION]->(o1);

// Evidence relationships
CREATE (e1)-[:SUPPORTS_CASE]->(c1);
CREATE (e2)-[:SUPPORTS_CASE]->(c1);
CREATE (e1)-[:LINKS_TO_PERSON]->(p1);
CREATE (e2)-[:LINKS_TO_ORGANIZATION]->(o2);

// =============================================================================
// CREATE FRAUD PATTERN DETECTION QUERIES
// =============================================================================

// Create stored procedures for common fraud detection patterns

// 1. Circular Transaction Detection
CALL dbms.procedures() YIELD name, signature
WHERE name = 'detect_circular_transactions'
CALL {
    CALL gds.graph.project.cypher(
        'transaction_graph',
        'MATCH (a:Account) RETURN id(a) AS id, a.account_number AS account_number',
        'MATCH (a1:Account)-[:SENT_TRANSACTION]->(t:Transaction)-[:RECEIVED_TRANSACTION]->(a2:Account) RETURN id(a1) AS source, id(a2) AS target, t.amount AS amount'
    )
    YIELD graphName
    RETURN graphName
};

// 2. High-Risk Entity Detection
CALL dbms.procedures() YIELD name, signature
WHERE name = 'detect_high_risk_entities'
CALL {
    MATCH (e:Person|Organization|Account)
    WHERE e.risk_score > 0.7
    RETURN e.id, e.name, e.risk_score, labels(e)[0] as entity_type
    ORDER BY e.risk_score DESC
};

// 3. Suspicious Transaction Patterns
CALL dbms.procedures() YIELD name, signature
WHERE name = 'detect_suspicious_patterns'
CALL {
    MATCH (a1:Account)-[:SENT_TRANSACTION]->(t:Transaction)-[:RECEIVED_TRANSACTION]->(a2:Account)
    WHERE t.amount > 10000 AND t.risk_score > 0.7
    RETURN a1.account_number as from_account, a2.account_number as to_account, 
           t.amount, t.date, t.risk_score
    ORDER BY t.risk_score DESC
};

// =============================================================================
// CREATE GRAPH ALGORITHMS FOR FRAUD DETECTION
// =============================================================================

// Install Graph Data Science library procedures
CALL gds.list() YIELD name, type, projectName
WHERE name = 'gds.graph.project.cypher'
CALL {
    // Create a graph projection for fraud detection
    CALL gds.graph.project.cypher(
        'fraud_detection_graph',
        'MATCH (n:Person|Organization|Account|Transaction) RETURN id(n) AS id, n, labels(n) AS labels',
        'MATCH (n)-[r]->(m) RETURN id(n) AS source, id(m) AS target, type(r) AS type, r'
    )
    YIELD graphName, nodeCount, relationshipCount
    RETURN graphName, nodeCount, relationshipCount
};

// =============================================================================
// CREATE INDEXES FOR GRAPH ALGORITHMS
// =============================================================================

// Create indexes for graph algorithm performance
CREATE INDEX person_risk_score IF NOT EXISTS FOR (p:Person) ON (p.risk_score);
CREATE INDEX organization_risk_score IF NOT EXISTS FOR (o:Organization) ON (o.risk_score);
CREATE INDEX account_risk_score IF NOT EXISTS FOR (a:Account) ON (a.risk_score);
CREATE INDEX transaction_risk_score IF NOT EXISTS FOR (t:Transaction) ON (t.risk_score);
CREATE INDEX transaction_amount IF NOT EXISTS FOR (t:Transaction) ON (t.amount);
CREATE INDEX transaction_date IF NOT EXISTS FOR (t:Transaction) ON (t.date);

// =============================================================================
// CREATE VIEWS FOR COMMON QUERIES
// =============================================================================

// Create a view for high-risk transactions
CALL dbms.procedures() YIELD name, signature
WHERE name = 'high_risk_transactions'
CALL {
    MATCH (a1:Account)-[:SENT_TRANSACTION]->(t:Transaction)-[:RECEIVED_TRANSACTION]->(a2:Account)
    WHERE t.risk_score > 0.7
    RETURN a1.account_number as from_account, a2.account_number as to_account,
           t.amount, t.date, t.risk_score, t.description
    ORDER BY t.risk_score DESC, t.amount DESC
};

// Create a view for entity risk assessment
CALL dbms.procedures() YIELD name, signature
WHERE name = 'entity_risk_assessment'
CALL {
    MATCH (e:Person|Organization|Account)
    RETURN e.id, e.name, labels(e)[0] as entity_type, e.risk_score,
           CASE 
               WHEN e.risk_score < 0.3 THEN 'LOW'
               WHEN e.risk_score < 0.7 THEN 'MEDIUM'
               ELSE 'HIGH'
           END as risk_level
    ORDER BY e.risk_score DESC
};

// =============================================================================
// COMMIT TRANSACTION
// =============================================================================

// All operations completed successfully
RETURN 'Neo4j Graph Schema Initialization Complete' as status;
