"""
Fraud Alert and Response System for FPO Economics Management
Handles automatic alert generation, transaction suspension, and investigation workflow.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import json

from .anti_fraud_engine import FraudAlert, AlertType, AlertStatus, FraudRiskScore

logger = logging.getLogger(__name__)


class ResponseAction(Enum):
    ALLOW = "ALLOW"
    SUSPEND = "SUSPEND"
    BLOCK = "BLOCK"
    REQUIRE_VERIFICATION = "REQUIRE_VERIFICATION"
    ESCALATE = "ESCALATE"


@dataclass
class AlertResponse:
    """Response to a fraud alert."""
    action: ResponseAction
    reason: str
    requires_admin_approval: bool
    auto_resolve_after: Optional[timedelta] = None
    notification_recipients: List[str] = None


@dataclass
class Investigation:
    """Represents a fraud investigation."""
    investigation_id: str
    alert_id: str
    investigator_id: str
    status: str  # OPEN, IN_PROGRESS, COMPLETED
    findings: str
    resolution: str
    created_at: datetime
    updated_at: datetime


class FraudAlertManager:
    """Manages fraud alerts and their lifecycle."""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.alert_thresholds = self._load_alert_thresholds()
        self.notification_handlers = []
    
    def _load_alert_thresholds(self) -> Dict[str, float]:
        """Load alert generation thresholds."""
        return {
            'auto_suspend_score': 80.0,
            'manual_review_score': 60.0,
            'monitoring_score': 30.0,
            'escalation_score': 90.0
        }
    
    def process_fraud_risk(self, transaction: Dict[str, Any], risk_score: FraudRiskScore) -> AlertResponse:
        """
        Process fraud risk assessment and generate appropriate response.
        
        Args:
            transaction: Transaction data
            risk_score: Fraud risk assessment
            
        Returns:
            AlertResponse: Recommended action and alert details
        """
        # Generate alert if risk score exceeds threshold
        alert = None
        if risk_score.score >= self.alert_thresholds['monitoring_score']:
            alert = self._create_alert(transaction, risk_score)
            self._save_alert(alert)
        
        # Determine response action based on risk score
        response = self._determine_response_action(risk_score, alert)
        
        # Execute automatic actions
        if response.action in [ResponseAction.SUSPEND, ResponseAction.BLOCK]:
            self._suspend_transaction(transaction['transaction_id'], response.reason)
        
        # Send notifications
        if alert and response.notification_recipients:
            self._send_notifications(alert, response)
        
        return response
    
    def _create_alert(self, transaction: Dict[str, Any], risk_score: FraudRiskScore) -> FraudAlert:
        """Create a fraud alert from transaction and risk assessment."""
        alert_type = self._determine_alert_type(risk_score.factors)
        
        return FraudAlert(
            alert_id=str(uuid.uuid4()),
            transaction_id=transaction['transaction_id'],
            member_id=transaction['member_id'],
            risk_score=risk_score.score,
            alert_type=alert_type,
            description=self._generate_alert_description(risk_score),
            timestamp=datetime.now(),
            status=AlertStatus.OPEN,
            metadata={
                'risk_factors': risk_score.factors,
                'recommendations': risk_score.recommendations,
                'transaction_amount': transaction['amount'],
                'transaction_type': transaction['transaction_type']
            }
        )
    
    def _determine_alert_type(self, risk_factors: List[str]) -> AlertType:
        """Determine alert type based on risk factors."""
        factor_text = ' '.join(risk_factors).lower()
        
        if 'threshold' in factor_text or 'limit' in factor_text:
            return AlertType.THRESHOLD_EXCEEDED
        elif 'frequency' in factor_text or 'velocity' in factor_text:
            return AlertType.VELOCITY_CHECK
        elif 'pattern' in factor_text or 'anomaly' in factor_text:
            return AlertType.PATTERN_ANOMALY
        else:
            return AlertType.SUSPICIOUS_BEHAVIOR
    
    def _generate_alert_description(self, risk_score: FraudRiskScore) -> str:
        """Generate human-readable alert description."""
        primary_factors = risk_score.factors[:3]  # Top 3 factors
        return f"Fraud risk detected (Score: {risk_score.score:.1f}). Primary concerns: {', '.join(primary_factors)}"
    
    def _determine_response_action(self, risk_score: FraudRiskScore, alert: Optional[FraudAlert]) -> AlertResponse:
        """Determine appropriate response action based on risk score."""
        score = risk_score.score
        
        if score >= self.alert_thresholds['escalation_score']:
            return AlertResponse(
                action=ResponseAction.BLOCK,
                reason="Critical fraud risk detected - transaction blocked",
                requires_admin_approval=True,
                notification_recipients=['security_team', 'admin'],
                auto_resolve_after=None
            )
        elif score >= self.alert_thresholds['auto_suspend_score']:
            return AlertResponse(
                action=ResponseAction.SUSPEND,
                reason="High fraud risk - transaction suspended for review",
                requires_admin_approval=True,
                notification_recipients=['security_team'],
                auto_resolve_after=timedelta(hours=24)
            )
        elif score >= self.alert_thresholds['manual_review_score']:
            return AlertResponse(
                action=ResponseAction.REQUIRE_VERIFICATION,
                reason="Medium fraud risk - additional verification required",
                requires_admin_approval=False,
                notification_recipients=['member_services'],
                auto_resolve_after=timedelta(hours=4)
            )
        elif score >= self.alert_thresholds['monitoring_score']:
            return AlertResponse(
                action=ResponseAction.ALLOW,
                reason="Low fraud risk - enhanced monitoring enabled",
                requires_admin_approval=False,
                notification_recipients=[],
                auto_resolve_after=timedelta(hours=1)
            )
        else:
            return AlertResponse(
                action=ResponseAction.ALLOW,
                reason="No significant fraud risk detected",
                requires_admin_approval=False,
                notification_recipients=[]
            )
    
    def _save_alert(self, alert: FraudAlert) -> bool:
        """Save fraud alert to database."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO fraud_alerts 
                    (alert_id, transaction_id, risk_score, alert_type, description, 
                     timestamp, status, investigated_by, resolution_notes, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    alert.alert_id,
                    alert.transaction_id,
                    alert.risk_score,
                    alert.alert_type.value,
                    alert.description,
                    alert.timestamp,
                    alert.status.value,
                    None,  # investigated_by
                    None,  # resolution_notes
                    json.dumps(alert.metadata)
                ))
                
                self.db_connection.commit()
                logger.info(f"Fraud alert {alert.alert_id} saved successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error saving fraud alert: {e}")
            self.db_connection.rollback()
            return False
    
    def _suspend_transaction(self, transaction_id: str, reason: str) -> bool:
        """Suspend a transaction due to fraud concerns."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE transactions 
                    SET status = 'SUSPENDED', 
                        metadata = COALESCE(metadata, '{}')::jsonb || %s::jsonb
                    WHERE transaction_id = %s
                """, (
                    json.dumps({'suspension_reason': reason, 'suspended_at': datetime.now().isoformat()}),
                    transaction_id
                ))
                
                self.db_connection.commit()
                logger.info(f"Transaction {transaction_id} suspended: {reason}")
                return True
                
        except Exception as e:
            logger.error(f"Error suspending transaction {transaction_id}: {e}")
            self.db_connection.rollback()
            return False
    
    def _send_notifications(self, alert: FraudAlert, response: AlertResponse) -> None:
        """Send notifications to relevant parties."""
        for handler in self.notification_handlers:
            try:
                handler.send_alert_notification(alert, response)
            except Exception as e:
                logger.error(f"Error sending notification via {handler}: {e}")
    
    def get_alert(self, alert_id: str) -> Optional[FraudAlert]:
        """Retrieve a fraud alert by ID."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT alert_id, transaction_id, risk_score, alert_type, description,
                           timestamp, status, investigated_by, resolution_notes, metadata
                    FROM fraud_alerts 
                    WHERE alert_id = %s
                """, (alert_id,))
                
                row = cursor.fetchone()
                if row:
                    return FraudAlert(
                        alert_id=row['alert_id'],
                        transaction_id=row['transaction_id'],
                        member_id='',  # Would need to join with transactions table
                        risk_score=float(row['risk_score']),
                        alert_type=AlertType(row['alert_type']),
                        description=row['description'],
                        timestamp=row['timestamp'],
                        status=AlertStatus(row['status']),
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving alert {alert_id}: {e}")
            return None
    
    def update_alert_status(self, alert_id: str, status: AlertStatus, investigator_id: str = None, notes: str = None) -> bool:
        """Update the status of a fraud alert."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE fraud_alerts 
                    SET status = %s, 
                        investigated_by = COALESCE(%s, investigated_by),
                        resolution_notes = COALESCE(%s, resolution_notes),
                        updated_at = NOW()
                    WHERE alert_id = %s
                """, (status.value, investigator_id, notes, alert_id))
                
                self.db_connection.commit()
                logger.info(f"Alert {alert_id} status updated to {status.value}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating alert status: {e}")
            self.db_connection.rollback()
            return False


class TransactionSuspensionManager:
    """Manages transaction suspension and administrative override capabilities."""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def suspend_transaction(self, transaction_id: str, reason: str, admin_id: str) -> bool:
        """
        Suspend a transaction with administrative override capability.
        
        Args:
            transaction_id: ID of transaction to suspend
            reason: Reason for suspension
            admin_id: ID of administrator performing the action
            
        Returns:
            bool: Success status
        """
        try:
            with self.db_connection.cursor() as cursor:
                # Check if transaction exists and is not already completed
                cursor.execute("""
                    SELECT status FROM transactions WHERE transaction_id = %s
                """, (transaction_id,))
                
                result = cursor.fetchone()
                if not result:
                    logger.error(f"Transaction {transaction_id} not found")
                    return False
                
                if result['status'] == 'COMPLETED':
                    logger.error(f"Cannot suspend completed transaction {transaction_id}")
                    return False
                
                # Suspend the transaction
                cursor.execute("""
                    UPDATE transactions 
                    SET status = 'SUSPENDED',
                        metadata = COALESCE(metadata, '{}')::jsonb || %s::jsonb
                    WHERE transaction_id = %s
                """, (
                    json.dumps({
                        'suspension_reason': reason,
                        'suspended_by': admin_id,
                        'suspended_at': datetime.now().isoformat(),
                        'can_override': True
                    }),
                    transaction_id
                ))
                
                self.db_connection.commit()
                logger.info(f"Transaction {transaction_id} suspended by admin {admin_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error suspending transaction: {e}")
            self.db_connection.rollback()
            return False
    
    def override_suspension(self, transaction_id: str, admin_id: str, override_reason: str) -> bool:
        """
        Override transaction suspension with administrative approval.
        
        Args:
            transaction_id: ID of suspended transaction
            admin_id: ID of administrator performing override
            override_reason: Reason for override
            
        Returns:
            bool: Success status
        """
        try:
            with self.db_connection.cursor() as cursor:
                # Verify transaction is suspended
                cursor.execute("""
                    SELECT status, metadata FROM transactions WHERE transaction_id = %s
                """, (transaction_id,))
                
                result = cursor.fetchone()
                if not result or result['status'] != 'SUSPENDED':
                    logger.error(f"Transaction {transaction_id} is not suspended")
                    return False
                
                # Update transaction to pending with override information
                metadata = json.loads(result['metadata']) if result['metadata'] else {}
                metadata.update({
                    'override_by': admin_id,
                    'override_reason': override_reason,
                    'override_at': datetime.now().isoformat()
                })
                
                cursor.execute("""
                    UPDATE transactions 
                    SET status = 'PENDING',
                        metadata = %s
                    WHERE transaction_id = %s
                """, (json.dumps(metadata), transaction_id))
                
                self.db_connection.commit()
                logger.info(f"Transaction {transaction_id} suspension overridden by admin {admin_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error overriding suspension: {e}")
            self.db_connection.rollback()
            return False
    
    def get_suspended_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of currently suspended transactions."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT t.transaction_id, t.member_id, t.amount, t.transaction_type,
                           t.timestamp, t.metadata, m.name as member_name
                    FROM transactions t
                    JOIN members m ON t.member_id = m.member_id
                    WHERE t.status = 'SUSPENDED'
                    ORDER BY t.timestamp DESC
                    LIMIT %s
                """, (limit,))
                
                return cursor.fetchall()
                
        except Exception as e:
            logger.error(f"Error retrieving suspended transactions: {e}")
            return []


class InvestigationWorkflow:
    """Manages fraud investigation workflow and case management."""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_investigation(self, alert_id: str, investigator_id: str) -> str:
        """
        Create a new fraud investigation case.
        
        Args:
            alert_id: ID of the fraud alert
            investigator_id: ID of the investigator
            
        Returns:
            str: Investigation ID
        """
        investigation_id = str(uuid.uuid4())
        
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO fraud_investigations 
                    (investigation_id, alert_id, investigator_id, status, created_at, updated_at)
                    VALUES (%s, %s, %s, 'OPEN', NOW(), NOW())
                """, (investigation_id, alert_id, investigator_id))
                
                # Update alert status to investigating
                cursor.execute("""
                    UPDATE fraud_alerts 
                    SET status = 'INVESTIGATING', investigated_by = %s, updated_at = NOW()
                    WHERE alert_id = %s
                """, (investigator_id, alert_id))
                
                self.db_connection.commit()
                logger.info(f"Investigation {investigation_id} created for alert {alert_id}")
                return investigation_id
                
        except Exception as e:
            logger.error(f"Error creating investigation: {e}")
            self.db_connection.rollback()
            return ""
    
    def update_investigation(self, investigation_id: str, findings: str, status: str = None) -> bool:
        """Update investigation with findings and status."""
        try:
            with self.db_connection.cursor() as cursor:
                if status:
                    cursor.execute("""
                        UPDATE fraud_investigations 
                        SET findings = %s, status = %s, updated_at = NOW()
                        WHERE investigation_id = %s
                    """, (findings, status, investigation_id))
                else:
                    cursor.execute("""
                        UPDATE fraud_investigations 
                        SET findings = %s, updated_at = NOW()
                        WHERE investigation_id = %s
                    """, (findings, investigation_id))
                
                self.db_connection.commit()
                logger.info(f"Investigation {investigation_id} updated")
                return True
                
        except Exception as e:
            logger.error(f"Error updating investigation: {e}")
            self.db_connection.rollback()
            return False
    
    def close_investigation(self, investigation_id: str, resolution: str, alert_status: AlertStatus) -> bool:
        """Close an investigation with resolution."""
        try:
            with self.db_connection.cursor() as cursor:
                # Update investigation
                cursor.execute("""
                    UPDATE fraud_investigations 
                    SET status = 'COMPLETED', resolution = %s, updated_at = NOW()
                    WHERE investigation_id = %s
                """, (resolution, investigation_id))
                
                # Update related alert
                cursor.execute("""
                    UPDATE fraud_alerts 
                    SET status = %s, resolution_notes = %s, updated_at = NOW()
                    WHERE alert_id = (
                        SELECT alert_id FROM fraud_investigations 
                        WHERE investigation_id = %s
                    )
                """, (alert_status.value, resolution, investigation_id))
                
                self.db_connection.commit()
                logger.info(f"Investigation {investigation_id} closed with resolution: {resolution}")
                return True
                
        except Exception as e:
            logger.error(f"Error closing investigation: {e}")
            self.db_connection.rollback()
            return False
    
    def get_open_investigations(self, investigator_id: str = None) -> List[Dict[str, Any]]:
        """Get list of open investigations."""
        try:
            with self.db_connection.cursor() as cursor:
                if investigator_id:
                    cursor.execute("""
                        SELECT fi.investigation_id, fi.alert_id, fi.investigator_id, fi.status,
                               fi.created_at, fa.description, fa.risk_score, fa.transaction_id
                        FROM fraud_investigations fi
                        JOIN fraud_alerts fa ON fi.alert_id = fa.alert_id
                        WHERE fi.status IN ('OPEN', 'IN_PROGRESS') AND fi.investigator_id = %s
                        ORDER BY fi.created_at DESC
                    """, (investigator_id,))
                else:
                    cursor.execute("""
                        SELECT fi.investigation_id, fi.alert_id, fi.investigator_id, fi.status,
                               fi.created_at, fa.description, fa.risk_score, fa.transaction_id
                        FROM fraud_investigations fi
                        JOIN fraud_alerts fa ON fi.alert_id = fa.alert_id
                        WHERE fi.status IN ('OPEN', 'IN_PROGRESS')
                        ORDER BY fi.created_at DESC
                    """)
                
                return cursor.fetchall()
                
        except Exception as e:
            logger.error(f"Error retrieving investigations: {e}")
            return []


# Notification handlers
class NotificationHandler:
    """Base class for notification handlers."""
    
    def send_alert_notification(self, alert: FraudAlert, response: AlertResponse) -> None:
        """Send notification for fraud alert."""
        raise NotImplementedError


class EmailNotificationHandler(NotificationHandler):
    """Email notification handler for fraud alerts."""
    
    def __init__(self, email_config: Dict[str, str]):
        self.email_config = email_config
    
    def send_alert_notification(self, alert: FraudAlert, response: AlertResponse) -> None:
        """Send email notification for fraud alert."""
        # Implementation would integrate with email service
        logger.info(f"Email notification sent for alert {alert.alert_id}")


class SMSNotificationHandler(NotificationHandler):
    """SMS notification handler for critical fraud alerts."""
    
    def __init__(self, sms_config: Dict[str, str]):
        self.sms_config = sms_config
    
    def send_alert_notification(self, alert: FraudAlert, response: AlertResponse) -> None:
        """Send SMS notification for critical fraud alert."""
        if alert.risk_score >= 80.0:  # Only for high-risk alerts
            # Implementation would integrate with SMS service
            logger.info(f"SMS notification sent for critical alert {alert.alert_id}")