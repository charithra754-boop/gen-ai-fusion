-- FPO Economics Management System Database Schema
-- This schema supports profit distribution and anti-fraud functionality

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Members table
CREATE TABLE members (
    member_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    join_date DATE NOT NULL,
    account_balance DECIMAL(15,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    member_id VARCHAR(50) NOT NULL REFERENCES members(member_id) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'DISTRIBUTION', 'TRANSFER')),
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    status VARCHAR(20) DEFAULT 'COMPLETED' CHECK (status IN ('PENDING', 'COMPLETED', 'SUSPENDED', 'FAILED')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Distribution rules table
CREATE TABLE distribution_rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rule_type VARCHAR(30) NOT NULL CHECK (rule_type IN ('EQUAL', 'CONTRIBUTION_BASED', 'HYBRID')),
    parameters JSONB NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fraud alerts table
CREATE TABLE fraud_alerts (
    alert_id VARCHAR(50) PRIMARY KEY,
    transaction_id VARCHAR(50) NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    risk_score DECIMAL(5,2) NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    alert_type VARCHAR(30) NOT NULL CHECK (alert_type IN ('THRESHOLD_EXCEEDED', 'PATTERN_ANOMALY', 'VELOCITY_CHECK', 'SUSPICIOUS_BEHAVIOR')),
    description TEXT,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE')),
    investigated_by VARCHAR(255),
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance optimization
CREATE INDEX idx_members_status ON members(status);
CREATE INDEX idx_members_join_date ON members(join_date);

CREATE INDEX idx_transactions_member_id ON transactions(member_id);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_status ON transactions(status);

CREATE INDEX idx_distribution_rules_active ON distribution_rules(active);
CREATE INDEX idx_distribution_rules_type ON distribution_rules(rule_type);

CREATE INDEX idx_fraud_alerts_transaction_id ON fraud_alerts(transaction_id);
CREATE INDEX idx_fraud_alerts_status ON fraud_alerts(status);
CREATE INDEX idx_fraud_alerts_risk_score ON fraud_alerts(risk_score);
CREATE INDEX idx_fraud_alerts_timestamp ON fraud_alerts(timestamp);

-- Triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_members_updated_at BEFORE UPDATE ON members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_distribution_rules_updated_at BEFORE UPDATE ON distribution_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fraud_alerts_updated_at BEFORE UPDATE ON fraud_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing
INSERT INTO members (member_id, name, join_date, account_balance, status) VALUES
('MBR001', 'Rajesh Kumar', '2023-01-15', 5000.00, 'ACTIVE'),
('MBR002', 'Priya Sharma', '2023-02-20', 7500.50, 'ACTIVE'),
('MBR003', 'Amit Patel', '2023-03-10', 3200.75, 'ACTIVE'),
('MBR004', 'Sunita Devi', '2023-04-05', 0.00, 'INACTIVE');

INSERT INTO distribution_rules (rule_id, name, rule_type, parameters, active) VALUES
('RULE001', 'Equal Distribution', 'EQUAL', '{"description": "Equal share for all active members"}', true),
('RULE002', 'Contribution Based', 'CONTRIBUTION_BASED', '{"weight_factors": {"investment": 0.6, "participation": 0.4}}', true),
('RULE003', 'Hybrid Model', 'HYBRID', '{"equal_portion": 0.3, "contribution_portion": 0.7}', false);

INSERT INTO transactions (transaction_id, member_id, amount, transaction_type, metadata) VALUES
('TXN001', 'MBR001', 1000.00, 'DEPOSIT', '{"source": "bank_transfer", "reference": "REF123"}'),
('TXN002', 'MBR002', 500.00, 'WITHDRAWAL', '{"destination": "bank_account", "reference": "REF124"}'),
('TXN003', 'MBR001', 250.00, 'DISTRIBUTION', '{"distribution_id": "DIST001", "rule_id": "RULE001"}');