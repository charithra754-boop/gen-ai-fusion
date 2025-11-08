-- Sample data for FPO Economics Management System
-- Provides initial test data for development and testing

-- Sample members
INSERT INTO members (member_id, name, join_date, account_balance, status) VALUES
('MBR001', 'Rajesh Kumar', '2023-01-15', 5000.00, 'ACTIVE'),
('MBR002', 'Priya Sharma', '2023-02-20', 7500.50, 'ACTIVE'),
('MBR003', 'Amit Patel', '2023-03-10', 3200.75, 'ACTIVE'),
('MBR004', 'Sunita Devi', '2023-04-05', 0.00, 'INACTIVE'),
('MBR005', 'Vikram Singh', '2023-05-12', 4800.25, 'ACTIVE'),
('MBR006', 'Meera Gupta', '2023-06-08', 6200.00, 'ACTIVE')
ON CONFLICT (member_id) DO NOTHING;

-- Sample distribution rules
INSERT INTO distribution_rules (rule_id, name, rule_type, parameters, active) VALUES
('RULE001', 'Equal Distribution', 'EQUAL', '{"description": "Equal share for all active members"}', true),
('RULE002', 'Contribution Based', 'CONTRIBUTION_BASED', '{"weight_factors": {"investment": 0.6, "participation": 0.4}}', true),
('RULE003', 'Hybrid Model', 'HYBRID', '{"equal_portion": 0.3, "contribution_portion": 0.7}', false),
('RULE004', 'Seasonal Distribution', 'CONTRIBUTION_BASED', '{"weight_factors": {"seasonal_contribution": 0.8, "base_participation": 0.2}}', true)
ON CONFLICT (rule_id) DO NOTHING;

-- Sample transactions
INSERT INTO transactions (transaction_id, member_id, amount, transaction_type, metadata, status) VALUES
('TXN001', 'MBR001', 1000.00, 'DEPOSIT', '{"source": "bank_transfer", "reference": "REF123"}', 'COMPLETED'),
('TXN002', 'MBR002', 500.00, 'WITHDRAWAL', '{"destination": "bank_account", "reference": "REF124"}', 'COMPLETED'),
('TXN003', 'MBR001', 250.00, 'DISTRIBUTION', '{"distribution_id": "DIST001", "rule_id": "RULE001"}', 'COMPLETED'),
('TXN004', 'MBR003', 750.00, 'DEPOSIT', '{"source": "cash_deposit", "reference": "REF125"}', 'COMPLETED'),
('TXN005', 'MBR005', 300.00, 'DISTRIBUTION', '{"distribution_id": "DIST001", "rule_id": "RULE001"}', 'COMPLETED'),
('TXN006', 'MBR002', 1500.00, 'TRANSFER', '{"from_member": "MBR006", "reference": "REF126"}', 'PENDING'),
('TXN007', 'MBR004', 200.00, 'DEPOSIT', '{"source": "mobile_payment", "reference": "REF127"}', 'COMPLETED')
ON CONFLICT (transaction_id) DO NOTHING;

-- Sample fraud alerts (for testing fraud detection)
INSERT INTO fraud_alerts (alert_id, transaction_id, risk_score, alert_type, description, status) VALUES
('ALERT001', 'TXN006', 75.5, 'THRESHOLD_EXCEEDED', 'Transaction amount exceeds normal pattern for member', 'OPEN'),
('ALERT002', 'TXN007', 45.2, 'PATTERN_ANOMALY', 'Unusual transaction pattern detected for inactive member', 'INVESTIGATING'),
('ALERT003', 'TXN002', 30.8, 'VELOCITY_CHECK', 'Multiple transactions in short time period', 'RESOLVED')
ON CONFLICT (alert_id) DO NOTHING;