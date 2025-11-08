"""
Fraud Detection Rule Management System
Manages configurable fraud detection rules, thresholds, and pattern matching capabilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
import re

logger = logging.getLogger(__name__)


class RuleType(Enum):
    THRESHOLD = "THRESHOLD"
    PATTERN = "PATTERN"
    VELOCITY = "VELOCITY"
    BEHAVIORAL = "BEHAVIORAL"
    COMPOSITE = "COMPOSITE"


class RuleOperator(Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUALS = "="
    NOT_EQUALS = "!="
    CONTAINS = "CONTAINS"
    MATCHES = "MATCHES"
    IN_RANGE = "IN_RANGE"
    NOT_IN_RANGE = "NOT_IN_RANGE"


@dataclass
class FraudRule:
    """Represents a configurable fraud detection rule."""
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    conditions: List[Dict[str, Any]]
    actions: List[str]
    priority: int  # 1-10, higher is more important
    active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str
    metadata: Dict[str, Any]


@dataclass
class RuleCondition:
    """Represents a condition within a fraud rule."""
    field: str
    operator: RuleOperator
    value: Any
    weight: float = 1.0  # Contribution to overall rule score


@dataclass
class FraudIndicator:
    """Represents a known fraud indicator pattern."""
    indicator_id: str
    name: str
    pattern_type: str  # IP, DEVICE, BEHAVIOR, TRANSACTION
    pattern_value: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    active: bool
    created_at: datetime
    match_count: int = 0
    last_matched: Optional[datetime] = None


class FraudRuleManager:
    """Manages fraud detection rules and their evaluation."""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.rules_cache = {}
        self.indicators_cache = {}
        self._load_rules()
        self._load_indicators()
    
    def _load_rules(self) -> None:
        """Load fraud detection rules from database into cache."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rule_id, name, description, rule_type, conditions, actions,
                           priority, active, created_at, updated_at, created_by, metadata
                    FROM fraud_rules 
                    WHERE active = TRUE
                    ORDER BY priority DESC
                """)
                
                rules = cursor.fetchall()
                self.rules_cache = {}
                
                for rule_data in rules:
                    rule = FraudRule(
                        rule_id=rule_data['rule_id'],
                        name=rule_data['name'],
                        description=rule_data['description'],
                        rule_type=RuleType(rule_data['rule_type']),
                        conditions=json.loads(rule_data['conditions']),
                        actions=json.loads(rule_data['actions']),
                        priority=rule_data['priority'],
                        active=rule_data['active'],
                        created_at=rule_data['created_at'],
                        updated_at=rule_data['updated_at'],
                        created_by=rule_data['created_by'],
                        metadata=json.loads(rule_data['metadata']) if rule_data['metadata'] else {}
                    )
                    self.rules_cache[rule.rule_id] = rule
                
                logger.info(f"Loaded {len(self.rules_cache)} fraud detection rules")
                
        except Exception as e:
            logger.error(f"Error loading fraud rules: {e}")
            self.rules_cache = {}
    
    def _load_indicators(self) -> None:
        """Load fraud indicators from database into cache."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT indicator_id, name, pattern_type, pattern_value, risk_level,
                           description, active, created_at, match_count, last_matched
                    FROM fraud_indicators 
                    WHERE active = TRUE
                """)
                
                indicators = cursor.fetchall()
                self.indicators_cache = {}
                
                for indicator_data in indicators:
                    indicator = FraudIndicator(
                        indicator_id=indicator_data['indicator_id'],
                        name=indicator_data['name'],
                        pattern_type=indicator_data['pattern_type'],
                        pattern_value=indicator_data['pattern_value'],
                        risk_level=indicator_data['risk_level'],
                        description=indicator_data['description'],
                        active=indicator_data['active'],
                        created_at=indicator_data['created_at'],
                        match_count=indicator_data['match_count'] or 0,
                        last_matched=indicator_data['last_matched']
                    )
                    self.indicators_cache[indicator.indicator_id] = indicator
                
                logger.info(f"Loaded {len(self.indicators_cache)} fraud indicators")
                
        except Exception as e:
            logger.error(f"Error loading fraud indicators: {e}")
            self.indicators_cache = {}
    
    def create_rule(self, rule_data: Dict[str, Any], created_by: str) -> str:
        """
        Create a new fraud detection rule.
        
        Args:
            rule_data: Rule configuration data
            created_by: ID of user creating the rule
            
        Returns:
            str: Rule ID if successful, empty string if failed
        """
        rule_id = str(uuid.uuid4())
        
        try:
            # Validate rule data
            if not self._validate_rule_data(rule_data):
                logger.error("Invalid rule data provided")
                return ""
            
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO fraud_rules 
                    (rule_id, name, description, rule_type, conditions, actions,
                     priority, active, created_at, updated_at, created_by, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s)
                """, (
                    rule_id,
                    rule_data['name'],
                    rule_data['description'],
                    rule_data['rule_type'],
                    json.dumps(rule_data['conditions']),
                    json.dumps(rule_data['actions']),
                    rule_data.get('priority', 5),
                    rule_data.get('active', True),
                    created_by,
                    json.dumps(rule_data.get('metadata', {}))
                ))
                
                self.db_connection.commit()
                
                # Reload rules cache
                self._load_rules()
                
                logger.info(f"Created fraud rule {rule_id}: {rule_data['name']}")
                return rule_id
                
        except Exception as e:
            logger.error(f"Error creating fraud rule: {e}")
            self.db_connection.rollback()
            return ""
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any], updated_by: str) -> bool:
        """
        Update an existing fraud detection rule.
        
        Args:
            rule_id: ID of rule to update
            updates: Fields to update
            updated_by: ID of user making the update
            
        Returns:
            bool: Success status
        """
        try:
            if rule_id not in self.rules_cache:
                logger.error(f"Rule {rule_id} not found")
                return False
            
            # Build update query dynamically
            update_fields = []
            update_values = []
            
            for field, value in updates.items():
                if field in ['name', 'description', 'rule_type', 'priority', 'active']:
                    update_fields.append(f"{field} = %s")
                    update_values.append(value)
                elif field in ['conditions', 'actions', 'metadata']:
                    update_fields.append(f"{field} = %s")
                    update_values.append(json.dumps(value))
            
            if not update_fields:
                logger.error("No valid fields to update")
                return False
            
            update_fields.append("updated_at = NOW()")
            update_values.append(rule_id)
            
            with self.db_connection.cursor() as cursor:
                query = f"""
                    UPDATE fraud_rules 
                    SET {', '.join(update_fields)}
                    WHERE rule_id = %s
                """
                cursor.execute(query, update_values)
                
                self.db_connection.commit()
                
                # Reload rules cache
                self._load_rules()
                
                logger.info(f"Updated fraud rule {rule_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating fraud rule: {e}")
            self.db_connection.rollback()
            return False
    
    def delete_rule(self, rule_id: str, deleted_by: str) -> bool:
        """
        Delete (deactivate) a fraud detection rule.
        
        Args:
            rule_id: ID of rule to delete
            deleted_by: ID of user deleting the rule
            
        Returns:
            bool: Success status
        """
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE fraud_rules 
                    SET active = FALSE, updated_at = NOW()
                    WHERE rule_id = %s
                """, (rule_id,))
                
                self.db_connection.commit()
                
                # Remove from cache
                if rule_id in self.rules_cache:
                    del self.rules_cache[rule_id]
                
                logger.info(f"Deleted fraud rule {rule_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting fraud rule: {e}")
            self.db_connection.rollback()
            return False
    
    def evaluate_rules(self, transaction: Dict[str, Any], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Evaluate all active fraud rules against a transaction.
        
        Args:
            transaction: Transaction data
            context: Additional context (member data, patterns, etc.)
            
        Returns:
            List of rule violations with scores and actions
        """
        violations = []
        context = context or {}
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.rules_cache.values(), key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            try:
                violation = self._evaluate_single_rule(rule, transaction, context)
                if violation:
                    violations.append(violation)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        return violations
    
    def _evaluate_single_rule(self, rule: FraudRule, transaction: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate a single fraud rule against transaction data."""
        if rule.rule_type == RuleType.THRESHOLD:
            return self._evaluate_threshold_rule(rule, transaction, context)
        elif rule.rule_type == RuleType.PATTERN:
            return self._evaluate_pattern_rule(rule, transaction, context)
        elif rule.rule_type == RuleType.VELOCITY:
            return self._evaluate_velocity_rule(rule, transaction, context)
        elif rule.rule_type == RuleType.BEHAVIORAL:
            return self._evaluate_behavioral_rule(rule, transaction, context)
        elif rule.rule_type == RuleType.COMPOSITE:
            return self._evaluate_composite_rule(rule, transaction, context)
        
        return None
    
    def _evaluate_threshold_rule(self, rule: FraudRule, transaction: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate threshold-based rules."""
        total_score = 0.0
        matched_conditions = []
        
        for condition in rule.conditions:
            field = condition['field']
            operator = RuleOperator(condition['operator'])
            threshold = condition['value']
            weight = condition.get('weight', 1.0)
            
            # Get field value from transaction or context
            field_value = self._get_field_value(field, transaction, context)
            if field_value is None:
                continue
            
            # Evaluate condition
            if self._evaluate_condition(field_value, operator, threshold):
                total_score += weight
                matched_conditions.append({
                    'field': field,
                    'operator': operator.value,
                    'threshold': threshold,
                    'actual_value': field_value,
                    'weight': weight
                })
        
        # Check if rule threshold is met
        rule_threshold = rule.metadata.get('threshold', len(rule.conditions) * 0.5)
        if total_score >= rule_threshold:
            return {
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'rule_type': rule.rule_type.value,
                'score': total_score,
                'max_score': sum(c.get('weight', 1.0) for c in rule.conditions),
                'matched_conditions': matched_conditions,
                'actions': rule.actions,
                'priority': rule.priority
            }
        
        return None
    
    def _evaluate_pattern_rule(self, rule: FraudRule, transaction: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate pattern-based rules."""
        matched_patterns = []
        
        for condition in rule.conditions:
            field = condition['field']
            pattern = condition['value']
            weight = condition.get('weight', 1.0)
            
            field_value = self._get_field_value(field, transaction, context)
            if field_value is None:
                continue
            
            # Check pattern match
            if self._match_pattern(str(field_value), pattern):
                matched_patterns.append({
                    'field': field,
                    'pattern': pattern,
                    'matched_value': field_value,
                    'weight': weight
                })
        
        if matched_patterns:
            total_score = sum(p['weight'] for p in matched_patterns)
            return {
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'rule_type': rule.rule_type.value,
                'score': total_score,
                'matched_patterns': matched_patterns,
                'actions': rule.actions,
                'priority': rule.priority
            }
        
        return None
    
    def _evaluate_velocity_rule(self, rule: FraudRule, transaction: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate velocity-based rules."""
        member_id = transaction.get('member_id')
        if not member_id:
            return None
        
        violations = []
        
        for condition in rule.conditions:
            time_window = condition.get('time_window', 3600)  # seconds
            max_count = condition.get('max_count', 10)
            max_amount = condition.get('max_amount')
            weight = condition.get('weight', 1.0)
            
            # Get recent transactions
            recent_count, recent_amount = self._get_recent_activity(member_id, time_window)
            
            # Check velocity violations
            if recent_count > max_count:
                violations.append({
                    'type': 'transaction_count',
                    'limit': max_count,
                    'actual': recent_count,
                    'weight': weight
                })
            
            if max_amount and recent_amount > max_amount:
                violations.append({
                    'type': 'transaction_amount',
                    'limit': max_amount,
                    'actual': recent_amount,
                    'weight': weight
                })
        
        if violations:
            total_score = sum(v['weight'] for v in violations)
            return {
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'rule_type': rule.rule_type.value,
                'score': total_score,
                'velocity_violations': violations,
                'actions': rule.actions,
                'priority': rule.priority
            }
        
        return None
    
    def _evaluate_behavioral_rule(self, rule: FraudRule, transaction: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate behavioral anomaly rules."""
        member_id = transaction.get('member_id')
        if not member_id:
            return None
        
        # Get member's behavioral baseline
        baseline = context.get('member_baseline') or self._get_member_baseline(member_id)
        if not baseline:
            return None
        
        anomalies = []
        
        for condition in rule.conditions:
            behavior_type = condition['behavior_type']
            deviation_threshold = condition.get('deviation_threshold', 2.0)
            weight = condition.get('weight', 1.0)
            
            # Check specific behavioral anomalies
            if behavior_type == 'amount_deviation':
                current_amount = float(transaction['amount'])
                avg_amount = baseline.get('avg_amount', 0)
                std_dev = baseline.get('amount_std_dev', 1)
                
                if std_dev > 0:
                    deviation = abs(current_amount - avg_amount) / std_dev
                    if deviation > deviation_threshold:
                        anomalies.append({
                            'type': behavior_type,
                            'deviation': deviation,
                            'threshold': deviation_threshold,
                            'weight': weight
                        })
            
            elif behavior_type == 'time_anomaly':
                current_hour = datetime.fromisoformat(transaction['timestamp'].replace('Z', '+00:00')).hour
                typical_hours = baseline.get('typical_hours', [])
                
                if typical_hours and current_hour not in typical_hours:
                    anomalies.append({
                        'type': behavior_type,
                        'unusual_hour': current_hour,
                        'typical_hours': typical_hours,
                        'weight': weight
                    })
        
        if anomalies:
            total_score = sum(a['weight'] for a in anomalies)
            return {
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'rule_type': rule.rule_type.value,
                'score': total_score,
                'behavioral_anomalies': anomalies,
                'actions': rule.actions,
                'priority': rule.priority
            }
        
        return None
    
    def _evaluate_composite_rule(self, rule: FraudRule, transaction: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate composite rules that combine multiple rule types."""
        # Composite rules would combine results from other rule types
        # This is a simplified implementation
        sub_results = []
        
        for condition in rule.conditions:
            sub_rule_type = condition.get('sub_rule_type')
            if sub_rule_type:
                # Create temporary rule for evaluation
                temp_rule = FraudRule(
                    rule_id=f"temp_{uuid.uuid4()}",
                    name=f"Sub-rule of {rule.name}",
                    description="Temporary sub-rule",
                    rule_type=RuleType(sub_rule_type),
                    conditions=condition.get('sub_conditions', []),
                    actions=[],
                    priority=rule.priority,
                    active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    created_by="system",
                    metadata=condition.get('metadata', {})
                )
                
                result = self._evaluate_single_rule(temp_rule, transaction, context)
                if result:
                    sub_results.append(result)
        
        # Combine results based on composite logic
        if sub_results:
            total_score = sum(r['score'] for r in sub_results)
            return {
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'rule_type': rule.rule_type.value,
                'score': total_score,
                'sub_results': sub_results,
                'actions': rule.actions,
                'priority': rule.priority
            }
        
        return None
    
    def _get_field_value(self, field: str, transaction: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Get field value from transaction or context data."""
        # Check transaction first
        if field in transaction:
            return transaction[field]
        
        # Check context
        if field in context:
            return context[field]
        
        # Handle nested fields (e.g., "metadata.source")
        if '.' in field:
            parts = field.split('.')
            data = transaction
            for part in parts:
                if isinstance(data, dict) and part in data:
                    data = data[part]
                else:
                    return None
            return data
        
        return None
    
    def _evaluate_condition(self, field_value: Any, operator: RuleOperator, threshold: Any) -> bool:
        """Evaluate a single condition."""
        try:
            if operator == RuleOperator.GREATER_THAN:
                return float(field_value) > float(threshold)
            elif operator == RuleOperator.LESS_THAN:
                return float(field_value) < float(threshold)
            elif operator == RuleOperator.EQUALS:
                return field_value == threshold
            elif operator == RuleOperator.NOT_EQUALS:
                return field_value != threshold
            elif operator == RuleOperator.CONTAINS:
                return str(threshold).lower() in str(field_value).lower()
            elif operator == RuleOperator.MATCHES:
                return re.match(str(threshold), str(field_value)) is not None
            elif operator == RuleOperator.IN_RANGE:
                if isinstance(threshold, list) and len(threshold) == 2:
                    return threshold[0] <= float(field_value) <= threshold[1]
            elif operator == RuleOperator.NOT_IN_RANGE:
                if isinstance(threshold, list) and len(threshold) == 2:
                    return not (threshold[0] <= float(field_value) <= threshold[1])
        except (ValueError, TypeError):
            pass
        
        return False
    
    def _match_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches the given pattern."""
        try:
            # Support regex patterns
            return re.search(pattern, value, re.IGNORECASE) is not None
        except re.error:
            # Fallback to simple string matching
            return pattern.lower() in value.lower()
    
    def _get_recent_activity(self, member_id: str, time_window: int) -> Tuple[int, float]:
        """Get recent transaction count and amount for velocity checks."""
        try:
            cutoff_time = datetime.now() - timedelta(seconds=time_window)
            
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total_amount
                    FROM transactions 
                    WHERE member_id = %s AND timestamp >= %s
                """, (member_id, cutoff_time))
                
                result = cursor.fetchone()
                return result['count'], float(result['total_amount'])
                
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return 0, 0.0
    
    def _get_member_baseline(self, member_id: str) -> Dict[str, Any]:
        """Get member's behavioral baseline for anomaly detection."""
        try:
            # Get last 30 days of transactions for baseline
            cutoff_date = datetime.now() - timedelta(days=30)
            
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT amount, EXTRACT(HOUR FROM timestamp) as hour, transaction_type
                    FROM transactions 
                    WHERE member_id = %s AND timestamp >= %s
                """, (member_id, cutoff_date))
                
                transactions = cursor.fetchall()
                
                if len(transactions) < 5:  # Need minimum data
                    return {}
                
                amounts = [float(t['amount']) for t in transactions]
                hours = [int(t['hour']) for t in transactions]
                
                import statistics
                
                return {
                    'avg_amount': statistics.mean(amounts),
                    'amount_std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                    'typical_hours': list(set(hours)),
                    'transaction_count': len(transactions)
                }
                
        except Exception as e:
            logger.error(f"Error getting member baseline: {e}")
            return {}
    
    def _validate_rule_data(self, rule_data: Dict[str, Any]) -> bool:
        """Validate rule data before creation."""
        required_fields = ['name', 'description', 'rule_type', 'conditions', 'actions']
        
        for field in required_fields:
            if field not in rule_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate rule type
        try:
            RuleType(rule_data['rule_type'])
        except ValueError:
            logger.error(f"Invalid rule type: {rule_data['rule_type']}")
            return False
        
        # Validate conditions
        if not isinstance(rule_data['conditions'], list) or not rule_data['conditions']:
            logger.error("Conditions must be a non-empty list")
            return False
        
        # Validate actions
        if not isinstance(rule_data['actions'], list) or not rule_data['actions']:
            logger.error("Actions must be a non-empty list")
            return False
        
        return True
    
    def get_rule(self, rule_id: str) -> Optional[FraudRule]:
        """Get a specific fraud rule by ID."""
        return self.rules_cache.get(rule_id)
    
    def get_all_rules(self) -> List[FraudRule]:
        """Get all active fraud rules."""
        return list(self.rules_cache.values())
    
    def reload_rules(self) -> None:
        """Reload rules from database."""
        self._load_rules()
        self._load_indicators()


class FraudIndicatorManager:
    """Manages fraud indicators and pattern matching."""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_indicator(self, indicator_data: Dict[str, Any]) -> str:
        """Create a new fraud indicator."""
        indicator_id = str(uuid.uuid4())
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO fraud_indicators 
                    (indicator_id, name, pattern_type, pattern_value, risk_level,
                     description, active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    indicator_id,
                    indicator_data['name'],
                    indicator_data['pattern_type'],
                    indicator_data['pattern_value'],
                    indicator_data['risk_level'],
                    indicator_data['description'],
                    indicator_data.get('active', True)
                ))
                
                self.db_connection.commit()
                logger.info(f"Created fraud indicator {indicator_id}")
                return indicator_id
                
        except Exception as e:
            logger.error(f"Error creating fraud indicator: {e}")
            self.db_connection.rollback()
            return ""
    
    def match_indicators(self, transaction: Dict[str, Any], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Match transaction against known fraud indicators."""
        matches = []
        context = context or {}
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT indicator_id, name, pattern_type, pattern_value, risk_level, description
                    FROM fraud_indicators 
                    WHERE active = TRUE
                """)
                
                indicators = cursor.fetchall()
                
                for indicator in indicators:
                    if self._match_indicator(transaction, context, indicator):
                        matches.append({
                            'indicator_id': indicator['indicator_id'],
                            'name': indicator['name'],
                            'pattern_type': indicator['pattern_type'],
                            'risk_level': indicator['risk_level'],
                            'description': indicator['description']
                        })
                        
                        # Update match count
                        self._update_indicator_match(indicator['indicator_id'])
                
        except Exception as e:
            logger.error(f"Error matching indicators: {e}")
        
        return matches
    
    def _match_indicator(self, transaction: Dict[str, Any], context: Dict[str, Any], indicator: Dict[str, Any]) -> bool:
        """Check if transaction matches a specific indicator."""
        pattern_type = indicator['pattern_type']
        pattern_value = indicator['pattern_value']
        
        if pattern_type == 'TRANSACTION':
            # Match transaction patterns
            return self._match_transaction_pattern(transaction, pattern_value)
        elif pattern_type == 'BEHAVIOR':
            # Match behavioral patterns
            return self._match_behavior_pattern(transaction, context, pattern_value)
        elif pattern_type == 'IP':
            # Match IP patterns (if available in metadata)
            ip_address = transaction.get('metadata', {}).get('ip_address')
            return ip_address and self._match_pattern(ip_address, pattern_value)
        elif pattern_type == 'DEVICE':
            # Match device patterns
            device_id = transaction.get('metadata', {}).get('device_id')
            return device_id and self._match_pattern(device_id, pattern_value)
        
        return False
    
    def _match_transaction_pattern(self, transaction: Dict[str, Any], pattern: str) -> bool:
        """Match transaction-specific patterns."""
        # Example patterns: "amount>100000", "type=WITHDRAWAL", etc.
        try:
            if '>' in pattern:
                field, value = pattern.split('>')
                return float(transaction.get(field, 0)) > float(value)
            elif '=' in pattern:
                field, value = pattern.split('=')
                return str(transaction.get(field, '')).upper() == value.upper()
            elif 'contains:' in pattern:
                field, value = pattern.split('contains:')
                return value.lower() in str(transaction.get(field, '')).lower()
        except (ValueError, KeyError):
            pass
        
        return False
    
    def _match_behavior_pattern(self, transaction: Dict[str, Any], context: Dict[str, Any], pattern: str) -> bool:
        """Match behavioral patterns."""
        # Example: "night_transaction", "weekend_activity", etc.
        timestamp = datetime.fromisoformat(transaction['timestamp'].replace('Z', '+00:00'))
        
        if pattern == 'night_transaction':
            return timestamp.hour >= 22 or timestamp.hour <= 6
        elif pattern == 'weekend_activity':
            return timestamp.weekday() >= 5  # Saturday = 5, Sunday = 6
        elif pattern == 'rapid_succession':
            # Check if there were recent transactions
            recent_count = context.get('recent_transaction_count', 0)
            return recent_count > 5
        
        return False
    
    def _match_pattern(self, value: str, pattern: str) -> bool:
        """Generic pattern matching."""
        try:
            return re.search(pattern, value, re.IGNORECASE) is not None
        except re.error:
            return pattern.lower() in value.lower()
    
    def _update_indicator_match(self, indicator_id: str) -> None:
        """Update indicator match statistics."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE fraud_indicators 
                    SET match_count = match_count + 1, last_matched = NOW()
                    WHERE indicator_id = %s
                """, (indicator_id,))
                
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"Error updating indicator match: {e}")
            self.db_connection.rollback()


class AlgorithmTuningManager:
    """Manages fraud detection algorithm updates and tuning."""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.performance_metrics = {}
    
    def update_algorithm_parameters(self, algorithm_name: str, parameters: Dict[str, Any]) -> bool:
        """Update algorithm parameters based on performance feedback."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO algorithm_parameters (algorithm_name, parameters, updated_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (algorithm_name) 
                    DO UPDATE SET parameters = %s, updated_at = NOW()
                """, (algorithm_name, json.dumps(parameters), json.dumps(parameters)))
                
                self.db_connection.commit()
                logger.info(f"Updated algorithm parameters for {algorithm_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating algorithm parameters: {e}")
            self.db_connection.rollback()
            return False
    
    def calculate_detection_effectiveness(self, time_period: timedelta = timedelta(days=30)) -> Dict[str, float]:
        """Calculate fraud detection effectiveness metrics."""
        try:
            cutoff_date = datetime.now() - time_period
            
            with self.db_connection.cursor() as cursor:
                # Get alert statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_alerts,
                        COUNT(CASE WHEN status = 'RESOLVED' THEN 1 END) as resolved_alerts,
                        COUNT(CASE WHEN status = 'FALSE_POSITIVE' THEN 1 END) as false_positives,
                        AVG(risk_score) as avg_risk_score
                    FROM fraud_alerts 
                    WHERE timestamp >= %s
                """, (cutoff_date,))
                
                stats = cursor.fetchone()
                
                if stats['total_alerts'] > 0:
                    effectiveness = {
                        'total_alerts': stats['total_alerts'],
                        'resolution_rate': stats['resolved_alerts'] / stats['total_alerts'],
                        'false_positive_rate': stats['false_positives'] / stats['total_alerts'],
                        'average_risk_score': float(stats['avg_risk_score'] or 0),
                        'precision': (stats['resolved_alerts'] - stats['false_positives']) / stats['total_alerts'] if stats['total_alerts'] > 0 else 0
                    }
                else:
                    effectiveness = {
                        'total_alerts': 0,
                        'resolution_rate': 0,
                        'false_positive_rate': 0,
                        'average_risk_score': 0,
                        'precision': 0
                    }
                
                return effectiveness
                
        except Exception as e:
            logger.error(f"Error calculating detection effectiveness: {e}")
            return {}
    
    def tune_thresholds(self, target_false_positive_rate: float = 0.1) -> Dict[str, float]:
        """Automatically tune detection thresholds to achieve target false positive rate."""
        try:
            # Get recent alert data for analysis
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT risk_score, status
                    FROM fraud_alerts 
                    WHERE timestamp >= %s
                    ORDER BY risk_score
                """, (datetime.now() - timedelta(days=30),))
                
                alerts = cursor.fetchall()
                
                if len(alerts) < 50:  # Need sufficient data
                    logger.warning("Insufficient data for threshold tuning")
                    return {}
                
                # Analyze false positive rates at different thresholds
                thresholds = {}
                for threshold in range(10, 100, 5):
                    alerts_above_threshold = [a for a in alerts if a['risk_score'] >= threshold]
                    if alerts_above_threshold:
                        false_positives = len([a for a in alerts_above_threshold if a['status'] == 'FALSE_POSITIVE'])
                        fp_rate = false_positives / len(alerts_above_threshold)
                        
                        if fp_rate <= target_false_positive_rate:
                            thresholds['monitoring_threshold'] = threshold
                            thresholds['review_threshold'] = threshold + 20
                            thresholds['suspend_threshold'] = threshold + 40
                            break
                
                return thresholds
                
        except Exception as e:
            logger.error(f"Error tuning thresholds: {e}")
            return {}