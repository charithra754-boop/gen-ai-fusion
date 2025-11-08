"""
Fraud Reporting and Analytics System
Generates comprehensive fraud risk reports, tracks detection effectiveness, and provides security recommendations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class ReportType(Enum):
    DAILY_SUMMARY = "DAILY_SUMMARY"
    WEEKLY_ANALYSIS = "WEEKLY_ANALYSIS"
    MONTHLY_OVERVIEW = "MONTHLY_OVERVIEW"
    TREND_ANALYSIS = "TREND_ANALYSIS"
    EFFECTIVENESS_REPORT = "EFFECTIVENESS_REPORT"
    SECURITY_ASSESSMENT = "SECURITY_ASSESSMENT"


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class FraudMetrics:
    """Core fraud detection metrics."""
    total_transactions: int
    flagged_transactions: int
    confirmed_fraud: int
    false_positives: int
    detection_rate: float
    false_positive_rate: float
    average_risk_score: float
    total_amount_at_risk: float
    prevented_losses: float


@dataclass
class TrendData:
    """Trend analysis data point."""
    date: datetime
    metric_value: float
    metric_name: str
    change_percentage: float = 0.0


@dataclass
class SecurityRecommendation:
    """Security improvement recommendation."""
    recommendation_id: str
    category: str
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL
    title: str
    description: str
    impact: str
    effort: str  # LOW, MEDIUM, HIGH
    implementation_steps: List[str]
    expected_improvement: str


class FraudReportGenerator:
    """Generates comprehensive fraud reports and analytics."""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.report_cache = {}
        self.cache_ttl = timedelta(hours=1)  # Cache reports for 1 hour
    
    def generate_report(self, report_type: ReportType, start_date: datetime = None, 
                       end_date: datetime = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a fraud report of the specified type.
        
        Args:
            report_type: Type of report to generate
            start_date: Start date for report period
            end_date: End date for report period
            **kwargs: Additional parameters specific to report type
            
        Returns:
            Dict containing the generated report
        """
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            if report_type == ReportType.DAILY_SUMMARY:
                start_date = end_date - timedelta(days=1)
            elif report_type == ReportType.WEEKLY_ANALYSIS:
                start_date = end_date - timedelta(days=7)
            elif report_type == ReportType.MONTHLY_OVERVIEW:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=30)
        
        # Check cache first
        cache_key = f"{report_type.value}_{start_date.date()}_{end_date.date()}"
        if cache_key in self.report_cache:
            cached_report, cache_time = self.report_cache[cache_key]
            if datetime.now() - cache_time < self.cache_ttl:
                return cached_report
        
        # Generate report based on type
        if report_type == ReportType.DAILY_SUMMARY:
            report = self._generate_daily_summary(start_date, end_date)
        elif report_type == ReportType.WEEKLY_ANALYSIS:
            report = self._generate_weekly_analysis(start_date, end_date)
        elif report_type == ReportType.MONTHLY_OVERVIEW:
            report = self._generate_monthly_overview(start_date, end_date)
        elif report_type == ReportType.TREND_ANALYSIS:
            report = self._generate_trend_analysis(start_date, end_date, **kwargs)
        elif report_type == ReportType.EFFECTIVENESS_REPORT:
            report = self._generate_effectiveness_report(start_date, end_date)
        elif report_type == ReportType.SECURITY_ASSESSMENT:
            report = self._generate_security_assessment(start_date, end_date)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        # Cache the report
        self.report_cache[cache_key] = (report, datetime.now())
        
        return report
    
    def _generate_daily_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate daily fraud summary report."""
        metrics = self._calculate_fraud_metrics(start_date, end_date)
        alerts = self._get_alerts_summary(start_date, end_date)
        top_risks = self._get_top_risk_transactions(start_date, end_date, limit=10)
        
        return {
            'report_type': 'Daily Fraud Summary',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat(),
            'metrics': asdict(metrics),
            'alerts': alerts,
            'top_risk_transactions': top_risks,
            'summary': self._generate_summary_text(metrics, alerts)
        }
    
    def _generate_weekly_analysis(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate weekly fraud analysis report."""
        metrics = self._calculate_fraud_metrics(start_date, end_date)
        daily_trends = self._get_daily_trends(start_date, end_date)
        pattern_analysis = self._analyze_fraud_patterns(start_date, end_date)
        member_risk_analysis = self._analyze_member_risk_distribution(start_date, end_date)
        
        return {
            'report_type': 'Weekly Fraud Analysis',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat(),
            'metrics': asdict(metrics),
            'daily_trends': daily_trends,
            'pattern_analysis': pattern_analysis,
            'member_risk_analysis': member_risk_analysis,
            'recommendations': self._generate_weekly_recommendations(metrics, pattern_analysis)
        }
    
    def _generate_monthly_overview(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate monthly fraud overview report."""
        metrics = self._calculate_fraud_metrics(start_date, end_date)
        weekly_trends = self._get_weekly_trends(start_date, end_date)
        effectiveness_metrics = self._calculate_detection_effectiveness(start_date, end_date)
        cost_analysis = self._calculate_fraud_cost_analysis(start_date, end_date)
        
        return {
            'report_type': 'Monthly Fraud Overview',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat(),
            'metrics': asdict(metrics),
            'weekly_trends': weekly_trends,
            'effectiveness': effectiveness_metrics,
            'cost_analysis': cost_analysis,
            'recommendations': self._generate_monthly_recommendations(metrics, effectiveness_metrics)
        }
    
    def _generate_trend_analysis(self, start_date: datetime, end_date: datetime, **kwargs) -> Dict[str, Any]:
        """Generate fraud trend analysis report."""
        metric_name = kwargs.get('metric', 'fraud_rate')
        granularity = kwargs.get('granularity', 'daily')  # daily, weekly, monthly
        
        trend_data = self._calculate_trend_data(start_date, end_date, metric_name, granularity)
        trend_analysis = self._analyze_trends(trend_data)
        forecasts = self._generate_trend_forecasts(trend_data)
        
        return {
            'report_type': 'Fraud Trend Analysis',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat(),
            'metric': metric_name,
            'granularity': granularity,
            'trend_data': [asdict(td) for td in trend_data],
            'analysis': trend_analysis,
            'forecasts': forecasts
        }
    
    def _generate_effectiveness_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate fraud detection effectiveness report."""
        effectiveness_metrics = self._calculate_detection_effectiveness(start_date, end_date)
        model_performance = self._analyze_model_performance(start_date, end_date)
        alert_analysis = self._analyze_alert_effectiveness(start_date, end_date)
        
        return {
            'report_type': 'Fraud Detection Effectiveness',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat(),
            'effectiveness_metrics': effectiveness_metrics,
            'model_performance': model_performance,
            'alert_analysis': alert_analysis,
            'improvement_recommendations': self._generate_effectiveness_recommendations(effectiveness_metrics, model_performance)
        }
    
    def _generate_security_assessment(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate security assessment and recommendations report."""
        security_metrics = self._calculate_security_metrics(start_date, end_date)
        vulnerability_analysis = self._analyze_security_vulnerabilities(start_date, end_date)
        recommendations = self._generate_security_recommendations(security_metrics, vulnerability_analysis)
        
        return {
            'report_type': 'Security Assessment',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.now().isoformat(),
            'security_metrics': security_metrics,
            'vulnerability_analysis': vulnerability_analysis,
            'recommendations': [asdict(rec) for rec in recommendations]
        }    

    def _calculate_fraud_metrics(self, start_date: datetime, end_date: datetime) -> FraudMetrics:
        """Calculate core fraud detection metrics for the given period."""
        try:
            with self.db_connection.cursor() as cursor:
                # Get total transactions
                cursor.execute("""
                    SELECT COUNT(*) as total_transactions,
                           COALESCE(SUM(amount), 0) as total_amount
                    FROM transactions 
                    WHERE timestamp BETWEEN %s AND %s
                """, (start_date, end_date))
                
                total_result = cursor.fetchone()
                total_transactions = total_result['total_transactions']
                total_amount = float(total_result['total_amount'])
                
                # Get flagged transactions
                cursor.execute("""
                    SELECT COUNT(*) as flagged_count,
                           COALESCE(AVG(risk_score), 0) as avg_risk_score,
                           COALESCE(SUM(CASE WHEN fa.metadata->>'transaction_amount' IS NOT NULL 
                                       THEN CAST(fa.metadata->>'transaction_amount' AS DECIMAL) 
                                       ELSE 0 END), 0) as amount_at_risk
                    FROM fraud_alerts fa
                    WHERE fa.timestamp BETWEEN %s AND %s
                """, (start_date, end_date))
                
                flagged_result = cursor.fetchone()
                flagged_transactions = flagged_result['flagged_count']
                avg_risk_score = float(flagged_result['avg_risk_score'])
                amount_at_risk = float(flagged_result['amount_at_risk'])
                
                # Get confirmed fraud cases
                cursor.execute("""
                    SELECT COUNT(*) as confirmed_fraud,
                           COALESCE(SUM(CASE WHEN fa.metadata->>'transaction_amount' IS NOT NULL 
                                       THEN CAST(fa.metadata->>'transaction_amount' AS DECIMAL) 
                                       ELSE 0 END), 0) as prevented_losses
                    FROM fraud_alerts fa
                    WHERE fa.timestamp BETWEEN %s AND %s
                    AND fa.status = 'CONFIRMED'
                """, (start_date, end_date))
                
                confirmed_result = cursor.fetchone()
                confirmed_fraud = confirmed_result['confirmed_fraud']
                prevented_losses = float(confirmed_result['prevented_losses'])
                
                # Get false positives
                cursor.execute("""
                    SELECT COUNT(*) as false_positives
                    FROM fraud_alerts fa
                    WHERE fa.timestamp BETWEEN %s AND %s
                    AND fa.status = 'FALSE_POSITIVE'
                """, (start_date, end_date))
                
                false_positive_result = cursor.fetchone()
                false_positives = false_positive_result['false_positives']
                
                # Calculate rates
                detection_rate = (confirmed_fraud / total_transactions * 100) if total_transactions > 0 else 0
                false_positive_rate = (false_positives / flagged_transactions * 100) if flagged_transactions > 0 else 0
                
                return FraudMetrics(
                    total_transactions=total_transactions,
                    flagged_transactions=flagged_transactions,
                    confirmed_fraud=confirmed_fraud,
                    false_positives=false_positives,
                    detection_rate=detection_rate,
                    false_positive_rate=false_positive_rate,
                    average_risk_score=avg_risk_score,
                    total_amount_at_risk=amount_at_risk,
                    prevented_losses=prevented_losses
                )
                
        except Exception as e:
            logger.error(f"Error calculating fraud metrics: {e}")
            return FraudMetrics(
                total_transactions=0,
                flagged_transactions=0,
                confirmed_fraud=0,
                false_positives=0,
                detection_rate=0.0,
                false_positive_rate=0.0,
                average_risk_score=0.0,
                total_amount_at_risk=0.0,
                prevented_losses=0.0
            )    def 
_get_alerts_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get summary of fraud alerts for the period."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count,
                        AVG(risk_score) as avg_risk_score
                    FROM fraud_alerts 
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY status
                """, (start_date, end_date))
                
                alerts_by_status = {}
                for row in cursor.fetchall():
                    alerts_by_status[row['status']] = {
                        'count': row['count'],
                        'avg_risk_score': float(row['avg_risk_score']) if row['avg_risk_score'] else 0.0
                    }
                
                return {
                    'total_alerts': sum(alert['count'] for alert in alerts_by_status.values()),
                    'by_status': alerts_by_status,
                    'high_risk_alerts': alerts_by_status.get('HIGH', {}).get('count', 0),
                    'critical_alerts': alerts_by_status.get('CRITICAL', {}).get('count', 0)
                }
                
        except Exception as e:
            logger.error(f"Error getting alerts summary: {e}")
            return {'total_alerts': 0, 'by_status': {}, 'high_risk_alerts': 0, 'critical_alerts': 0}

    def _get_top_risk_transactions(self, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top risk transactions for the period."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        fa.alert_id,
                        fa.member_id,
                        fa.risk_score,
                        fa.alert_type,
                        fa.metadata,
                        fa.timestamp
                    FROM fraud_alerts fa
                    WHERE fa.timestamp BETWEEN %s AND %s
                    ORDER BY fa.risk_score DESC
                    LIMIT %s
                """, (start_date, end_date, limit))
                
                transactions = []
                for row in cursor.fetchall():
                    transactions.append({
                        'alert_id': row['alert_id'],
                        'member_id': row['member_id'],
                        'risk_score': float(row['risk_score']),
                        'alert_type': row['alert_type'],
                        'metadata': row['metadata'],
                        'timestamp': row['timestamp'].isoformat()
                    })
                
                return transactions
                
        except Exception as e:
            logger.error(f"Error getting top risk transactions: {e}")
            return []

    def _generate_summary_text(self, metrics: FraudMetrics, alerts: Dict[str, Any]) -> str:
        """Generate human-readable summary text."""
        summary_parts = []
        
        # Transaction overview
        summary_parts.append(f"Processed {metrics.total_transactions:,} transactions")
        
        # Detection performance
        if metrics.flagged_transactions > 0:
            summary_parts.append(f"flagged {metrics.flagged_transactions:,} ({metrics.detection_rate:.1f}% detection rate)")
        
        # Fraud confirmation
        if metrics.confirmed_fraud > 0:
            summary_parts.append(f"confirmed {metrics.confirmed_fraud} fraud cases")
            if metrics.prevented_losses > 0:
                summary_parts.append(f"preventing ${metrics.prevented_losses:,.2f} in losses")
        
        # False positives
        if metrics.false_positives > 0:
            summary_parts.append(f"with {metrics.false_positives} false positives ({metrics.false_positive_rate:.1f}% FP rate)")
        
        # Alert summary
        if alerts['total_alerts'] > 0:
            summary_parts.append(f"Generated {alerts['total_alerts']} alerts")
            if alerts['critical_alerts'] > 0:
                summary_parts.append(f"including {alerts['critical_alerts']} critical alerts")
        
        return ". ".join(summary_parts) + "."

    def _get_daily_trends(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily fraud trends for the period."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as total_alerts,
                        AVG(risk_score) as avg_risk_score,
                        COUNT(CASE WHEN status = 'CONFIRMED' THEN 1 END) as confirmed_fraud
                    FROM fraud_alerts
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """, (start_date, end_date))
                
                trends = []
                for row in cursor.fetchall():
                    trends.append({
                        'date': row['date'].isoformat(),
                        'total_alerts': row['total_alerts'],
                        'avg_risk_score': float(row['avg_risk_score']) if row['avg_risk_score'] else 0.0,
                        'confirmed_fraud': row['confirmed_fraud']
                    })
                
                return trends
                
        except Exception as e:
            logger.error(f"Error getting daily trends: {e}")
            return []

    def _analyze_fraud_patterns(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze fraud patterns and trends."""
        try:
            with self.db_connection.cursor() as cursor:
                # Pattern by alert type
                cursor.execute("""
                    SELECT 
                        alert_type,
                        COUNT(*) as count,
                        AVG(risk_score) as avg_risk_score
                    FROM fraud_alerts
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY alert_type
                    ORDER BY count DESC
                """, (start_date, end_date))
                
                patterns_by_type = {}
                for row in cursor.fetchall():
                    patterns_by_type[row['alert_type']] = {
                        'count': row['count'],
                        'avg_risk_score': float(row['avg_risk_score']) if row['avg_risk_score'] else 0.0
                    }
                
                # Time-based patterns
                cursor.execute("""
                    SELECT 
                        EXTRACT(HOUR FROM timestamp) as hour,
                        COUNT(*) as count
                    FROM fraud_alerts
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY EXTRACT(HOUR FROM timestamp)
                    ORDER BY count DESC
                    LIMIT 5
                """, (start_date, end_date))
                
                peak_hours = [{'hour': int(row['hour']), 'count': row['count']} for row in cursor.fetchall()]
                
                return {
                    'patterns_by_type': patterns_by_type,
                    'peak_fraud_hours': peak_hours,
                    'most_common_type': max(patterns_by_type.keys(), key=lambda k: patterns_by_type[k]['count']) if patterns_by_type else None
                }
                
        except Exception as e:
            logger.error(f"Error analyzing fraud patterns: {e}")
            return {'patterns_by_type': {}, 'peak_fraud_hours': [], 'most_common_type': None}

    def _analyze_member_risk_distribution(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze risk distribution across members."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        member_id,
                        COUNT(*) as alert_count,
                        AVG(risk_score) as avg_risk_score,
                        MAX(risk_score) as max_risk_score
                    FROM fraud_alerts
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY member_id
                    ORDER BY alert_count DESC
                    LIMIT 20
                """, (start_date, end_date))
                
                member_risks = []
                for row in cursor.fetchall():
                    member_risks.append({
                        'member_id': row['member_id'],
                        'alert_count': row['alert_count'],
                        'avg_risk_score': float(row['avg_risk_score']) if row['avg_risk_score'] else 0.0,
                        'max_risk_score': float(row['max_risk_score']) if row['max_risk_score'] else 0.0
                    })
                
                # Risk score distribution
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN risk_score < 30 THEN 'LOW'
                            WHEN risk_score < 60 THEN 'MEDIUM'
                            WHEN risk_score < 80 THEN 'HIGH'
                            ELSE 'CRITICAL'
                        END as risk_category,
                        COUNT(*) as count
                    FROM fraud_alerts
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY risk_category
                """, (start_date, end_date))
                
                risk_distribution = {}
                for row in cursor.fetchall():
                    risk_distribution[row['risk_category']] = row['count']
                
                return {
                    'top_risk_members': member_risks,
                    'risk_distribution': risk_distribution,
                    'total_flagged_members': len(member_risks)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing member risk distribution: {e}")
            return {'top_risk_members': [], 'risk_distribution': {}, 'total_flagged_members': 0}

    def _generate_weekly_recommendations(self, metrics: FraudMetrics, pattern_analysis: Dict[str, Any]) -> List[str]:
        """Generate weekly recommendations based on metrics and patterns."""
        recommendations = []
        
        # False positive rate recommendations
        if metrics.false_positive_rate > 15:
            recommendations.append("Consider adjusting fraud detection thresholds to reduce false positive rate")
        
        # Detection rate recommendations
        if metrics.detection_rate < 5:
            recommendations.append("Review and enhance fraud detection algorithms for better coverage")
        
        # Pattern-based recommendations
        if pattern_analysis.get('most_common_type'):
            most_common = pattern_analysis['most_common_type']
            recommendations.append(f"Focus on improving detection for {most_common} fraud patterns")
        
        # Peak hours recommendations
        peak_hours = pattern_analysis.get('peak_fraud_hours', [])
        if peak_hours:
            top_hour = peak_hours[0]['hour']
            recommendations.append(f"Increase monitoring during peak fraud hour: {top_hour}:00")
        
        # Risk score recommendations
        if metrics.average_risk_score < 40:
            recommendations.append("Consider recalibrating risk scoring models for better discrimination")
        
        return recommendations

    def _get_weekly_trends(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get weekly fraud trends for the period."""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        DATE_TRUNC('week', timestamp) as week_start,
                        COUNT(*) as total_alerts,
                        AVG(risk_score) as avg_risk_score,
                        COUNT(CASE WHEN status = 'CONFIRMED' THEN 1 END) as confirmed_fraud,
                        COUNT(CASE WHEN status = 'FALSE_POSITIVE' THEN 1 END) as false_positives
                    FROM fraud_alerts
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY DATE_TRUNC('week', timestamp)
                    ORDER BY week_start
                """, (start_date, end_date))
                
                trends = []
                for row in cursor.fetchall():
                    trends.append({
                        'week_start': row['week_start'].isoformat(),
                        'total_alerts': row['total_alerts'],
                        'avg_risk_score': float(row['avg_risk_score']) if row['avg_risk_score'] else 0.0,
                        'confirmed_fraud': row['confirmed_fraud'],
                        'false_positives': row['false_positives']
                    })
                
                return trends
                
        except Exception as e:
            logger.error(f"Error getting weekly trends: {e}")
            return []

    def _calculate_detection_effectiveness(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate fraud detection effectiveness metrics."""
        try:
            with self.db_connection.cursor() as cursor:
                # Get detection metrics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_alerts,
                        COUNT(CASE WHEN status = 'CONFIRMED' THEN 1 END) as true_positives,
                        COUNT(CASE WHEN status = 'FALSE_POSITIVE' THEN 1 END) as false_positives,
                        COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending_review,
                        AVG(risk_score) as avg_risk_score
                    FROM fraud_alerts
                    WHERE timestamp BETWEEN %s AND %s
                """, (start_date, end_date))
                
                result = cursor.fetchone()
                total_alerts = result['total_alerts']
                true_positives = result['true_positives']
                false_positives = result['false_positives']
                pending_review = result['pending_review']
                avg_risk_score = float(result['avg_risk_score']) if result['avg_risk_score'] else 0.0
                
                # Calculate effectiveness metrics
                precision = (true_positives / total_alerts * 100) if total_alerts > 0 else 0
                false_positive_rate = (false_positives / total_alerts * 100) if total_alerts > 0 else 0
                
                return {
                    'total_alerts': total_alerts,
                    'true_positives': true_positives,
                    'false_positives': false_positives,
                    'pending_review': pending_review,
                    'precision': precision,
                    'false_positive_rate': false_positive_rate,
                    'avg_risk_score': avg_risk_score,
                    'effectiveness_score': precision - (false_positive_rate * 0.5)  # Custom effectiveness metric
                }
                
        except Exception as e:
            logger.error(f"Error calculating detection effectiveness: {e}")
            return {
                'total_alerts': 0, 'true_positives': 0, 'false_positives': 0,
                'pending_review': 0, 'precision': 0, 'false_positive_rate': 0,
                'avg_risk_score': 0, 'effectiveness_score': 0
            }

    def _calculate_fraud_cost_analysis(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate fraud cost analysis and ROI of detection system."""
        try:
            with self.db_connection.cursor() as cursor:
                # Get financial impact data
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN status = 'CONFIRMED' THEN 1 END) as confirmed_cases,
                        COALESCE(SUM(CASE WHEN status = 'CONFIRMED' AND metadata->>'transaction_amount' IS NOT NULL 
                                    THEN CAST(metadata->>'transaction_amount' AS DECIMAL) 
                                    ELSE 0 END), 0) as prevented_losses,
                        COALESCE(SUM(CASE WHEN status = 'FALSE_POSITIVE' AND metadata->>'transaction_amount' IS NOT NULL 
                                    THEN CAST(metadata->>'transaction_amount' AS DECIMAL) 
                                    ELSE 0 END), 0) as false_positive_impact
                    FROM fraud_alerts
                    WHERE timestamp BETWEEN %s AND %s
                """, (start_date, end_date))
                
                result = cursor.fetchone()
                confirmed_cases = result['confirmed_cases']
                prevented_losses = float(result['prevented_losses'])
                false_positive_impact = float(result['false_positive_impact'])
                
                # Estimate operational costs (simplified calculation)
                investigation_cost_per_alert = 50.0  # Estimated cost per alert investigation
                total_investigation_costs = confirmed_cases * investigation_cost_per_alert
                
                # Calculate ROI
                net_benefit = prevented_losses - total_investigation_costs
                roi_percentage = (net_benefit / total_investigation_costs * 100) if total_investigation_costs > 0 else 0
                
                return {
                    'prevented_losses': prevented_losses,
                    'investigation_costs': total_investigation_costs,
                    'false_positive_impact': false_positive_impact,
                    'net_benefit': net_benefit,
                    'roi_percentage': roi_percentage,
                    'cost_per_prevented_case': (total_investigation_costs / confirmed_cases) if confirmed_cases > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Error calculating fraud cost analysis: {e}")
            return {
                'prevented_losses': 0, 'investigation_costs': 0, 'false_positive_impact': 0,
                'net_benefit': 0, 'roi_percentage': 0, 'cost_per_prevented_case': 0
            }

    def _generate_monthly_recommendations(self, metrics: FraudMetrics, effectiveness_metrics: Dict[str, Any]) -> List[str]:
        """Generate monthly recommendations based on comprehensive analysis."""
        recommendations = []
        
        # Effectiveness-based recommendations
        if effectiveness_metrics['effectiveness_score'] < 50:
            recommendations.append("Overall fraud detection effectiveness is below target - consider model retraining")
        
        # Precision recommendations
        if effectiveness_metrics['precision'] < 60:
            recommendations.append("Low precision detected - review and refine detection algorithms")
        
        # Volume-based recommendations
        if metrics.flagged_transactions > metrics.total_transactions * 0.1:
            recommendations.append("High alert volume detected - consider adjusting sensitivity thresholds")
        
        # Cost-effectiveness recommendations
        if metrics.prevented_losses < 10000:
            recommendations.append("Low prevented losses - evaluate detection coverage for high-value transactions")
        
        # Risk score recommendations
        if metrics.average_risk_score > 70:
            recommendations.append("High average risk scores - investigate potential systematic issues")
        
        return recommendations

    def _calculate_trend_data(self, start_date: datetime, end_date: datetime, 
                            metric_name: str, granularity: str) -> List[TrendData]:
        """Calculate trend data for specified metric and granularity."""
        try:
            with self.db_connection.cursor() as cursor:
                # Determine date truncation based on granularity
                if granularity == 'daily':
                    date_trunc = "DATE(timestamp)"
                elif granularity == 'weekly':
                    date_trunc = "DATE_TRUNC('week', timestamp)"
                else:  # monthly
                    date_trunc = "DATE_TRUNC('month', timestamp)"
                
                # Build query based on metric
                if metric_name == 'fraud_rate':
                    query = f"""
                        SELECT 
                            {date_trunc} as period,
                            COUNT(CASE WHEN status = 'CONFIRMED' THEN 1 END)::float / 
                            NULLIF(COUNT(*), 0) * 100 as metric_value
                        FROM fraud_alerts
                        WHERE timestamp BETWEEN %s AND %s
                        GROUP BY {date_trunc}
                        ORDER BY period
                    """
                elif metric_name == 'avg_risk_score':
                    query = f"""
                        SELECT 
                            {date_trunc} as period,
                            AVG(risk_score) as metric_value
                        FROM fraud_alerts
                        WHERE timestamp BETWEEN %s AND %s
                        GROUP BY {date_trunc}
                        ORDER BY period
                    """
                else:  # alert_volume
                    query = f"""
                        SELECT 
                            {date_trunc} as period,
                            COUNT(*) as metric_value
                        FROM fraud_alerts
                        WHERE timestamp BETWEEN %s AND %s
                        GROUP BY {date_trunc}
                        ORDER BY period
                    """
                
                cursor.execute(query, (start_date, end_date))
                
                trend_data = []
                previous_value = None
                
                for row in cursor.fetchall():
                    current_value = float(row['metric_value']) if row['metric_value'] else 0.0
                    change_percentage = 0.0
                    
                    if previous_value is not None and previous_value != 0:
                        change_percentage = ((current_value - previous_value) / previous_value) * 100
                    
                    trend_data.append(TrendData(
                        date=row['period'],
                        metric_value=current_value,
                        metric_name=metric_name,
                        change_percentage=change_percentage
                    ))
                    
                    previous_value = current_value
                
                return trend_data
                
        except Exception as e:
            logger.error(f"Error calculating trend data: {e}")
            return []

    def _analyze_trends(self, trend_data: List[TrendData]) -> Dict[str, Any]:
        """Analyze trend data for patterns and insights."""
        if not trend_data:
            return {'trend_direction': 'unknown', 'volatility': 0, 'insights': []}
        
        values = [td.metric_value for td in trend_data]
        changes = [td.change_percentage for td in trend_data if td.change_percentage != 0]
        
        # Calculate trend direction
        if len(values) >= 2:
            overall_change = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
            if overall_change > 5:
                trend_direction = 'increasing'
            elif overall_change < -5:
                trend_direction = 'decreasing'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'unknown'
        
        # Calculate volatility
        volatility = statistics.stdev(changes) if len(changes) > 1 else 0
        
        # Generate insights
        insights = []
        if trend_direction == 'increasing':
            insights.append("Metric shows upward trend - monitor for potential issues")
        elif trend_direction == 'decreasing':
            insights.append("Metric shows downward trend - investigate causes")
        
        if volatility > 20:
            insights.append("High volatility detected - consider stabilization measures")
        
        return {
            'trend_direction': trend_direction,
            'overall_change_percentage': overall_change if 'overall_change' in locals() else 0,
            'volatility': volatility,
            'insights': insights
        }

    def _generate_trend_forecasts(self, trend_data: List[TrendData]) -> Dict[str, Any]:
        """Generate simple trend forecasts based on historical data."""
        if len(trend_data) < 3:
            return {'forecast_available': False, 'reason': 'Insufficient data for forecasting'}
        
        values = [td.metric_value for td in trend_data]
        
        # Simple linear trend calculation
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope using least squares
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return {'forecast_available': False, 'reason': 'Cannot calculate trend slope'}
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Forecast next 3 periods
        forecasts = []
        for i in range(1, 4):
            forecast_value = slope * (n + i - 1) + intercept
            forecasts.append({
                'period': i,
                'forecast_value': max(0, forecast_value)  # Ensure non-negative
            })
        
        return {
            'forecast_available': True,
            'trend_slope': slope,
            'forecasts': forecasts,
            'confidence': 'low' if abs(slope) < 1 else 'medium'
        }