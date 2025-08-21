"""
Confidence Scorer - Advanced Confidence Scoring for Forensic Analysis

This module implements the ConfidenceScorer class that provides
sophisticated confidence scoring capabilities for forensic investigations.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json
import statistics
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from ...taskmaster.models.job import Job, JobStatus, JobPriority, JobType


class ConfidenceFactor(Enum):
    """Confidence scoring factors."""
    DATA_QUALITY = "data_quality"          # Quality of source data
    MATCH_STRENGTH = "match_strength"      # Strength of match
    ALGORITHM_RELIABILITY = "algorithm_reliability"  # Algorithm confidence
    HISTORICAL_ACCURACY = "historical_accuracy"  # Historical performance
    CONTEXT_RELEVANCE = "context_relevance"  # Contextual relevance
    SOURCE_CREDIBILITY = "source_credibility"  # Source reliability
    TIMESTAMP_FRESHNESS = "timestamp_freshness"  # Data freshness
    COMPLETENESS = "completeness"          # Data completeness
    CONSISTENCY = "consistency"             # Data consistency
    VERIFICATION_STATUS = "verification_status"  # Verification level


class ConfidenceLevel(Enum):
    """Confidence levels."""
    CERTAIN = "certain"                    # 95-100% confidence
    VERY_HIGH = "very_high"                # 90-94% confidence
    HIGH = "high"                          # 80-89% confidence
    MODERATE = "moderate"                  # 70-79% confidence
    LOW = "low"                            # 60-69% confidence
    VERY_LOW = "very_low"                  # Below 60% confidence


class ScoringMethod(Enum):
    """Confidence scoring methods."""
    WEIGHTED_AVERAGE = "weighted_average"  # Weighted factor average
    MACHINE_LEARNING = "ml_based"          # ML-based scoring
    RULE_BASED = "rule_based"              # Rule-based scoring
    HYBRID = "hybrid"                      # Combination approach
    ADAPTIVE = "adaptive"                  # Self-adjusting scoring


@dataclass
class ConfidenceScore:
    """Confidence score result."""
    
    record_id: str
    overall_score: float
    confidence_level: ConfidenceLevel
    factor_scores: Dict[ConfidenceFactor, float]
    method: ScoringMethod
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class ScoringConfig:
    """Configuration for confidence scoring."""
    
    method: ScoringMethod
    weights: Dict[ConfidenceFactor, float] = field(default_factory=dict)
    thresholds: Dict[ConfidenceLevel, float] = field(default_factory=dict)
    enable_ml_training: bool = True
    enable_adaptive_scoring: bool = True
    min_confidence_threshold: float = 0.6
    
    def __post_init__(self):
        if not self.weights:
            self.weights = {
                ConfidenceFactor.DATA_QUALITY: 0.25,
                ConfidenceFactor.MATCH_STRENGTH: 0.30,
                ConfidenceFactor.ALGORITHM_RELIABILITY: 0.20,
                ConfidenceFactor.HISTORICAL_ACCURACY: 0.15,
                ConfidenceFactor.CONTEXT_RELEVANCE: 0.10
            }
        
        if not self.thresholds:
            self.thresholds = {
                ConfidenceLevel.CERTAIN: 0.95,
                ConfidenceLevel.VERY_HIGH: 0.90,
                ConfidenceLevel.HIGH: 0.80,
                ConfidenceLevel.MODERATE: 0.70,
                ConfidenceLevel.LOW: 0.60
            }


class ConfidenceScorer:
    """
    Advanced confidence scoring system for forensic analysis.
    
    The ConfidenceScorer is responsible for:
    - Calculating confidence scores for forensic matches
    - Using multiple scoring methods and factors
    - Providing adaptive scoring based on historical data
    - Generating confidence level classifications
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the ConfidenceScorer."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.default_method = ScoringMethod(config.get('default_method', 'hybrid'))
        self.enable_ml_training = config.get('enable_ml_training', True)
        self.enable_adaptive_scoring = config.get('enable_adaptive_scoring', True)
        self.min_confidence_threshold = config.get('min_confidence_threshold', 0.6)
        
        # ML components
        self.ml_model = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        
        # Internal state
        self.scoring_history: List[ConfidenceScore] = []
        self.factor_statistics: Dict[ConfidenceFactor, Dict[str, float]] = {}
        self.performance_metrics: Dict[str, Any] = {}
        
        # Performance tracking
        self.total_scores_calculated = 0
        self.average_scoring_time = 0.0
        self.scoring_accuracy = 0.0
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info("ConfidenceScorer initialized successfully")
    
    async def start(self):
        """Start the ConfidenceScorer."""
        self.logger.info("Starting ConfidenceScorer...")
        
        # Initialize ML model if enabled
        if self.enable_ml_training:
            await self._initialize_ml_model()
        
        # Start background tasks
        asyncio.create_task(self._update_performance_metrics())
        asyncio.create_task(self._cleanup_old_scores())
        
        self.logger.info("ConfidenceScorer started successfully")
    
    async def stop(self):
        """Stop the ConfidenceScorer."""
        self.logger.info("Stopping ConfidenceScorer...")
        self.logger.info("ConfidenceScorer stopped")
    
    async def calculate_confidence(self, record_data: Dict[str, Any], 
                                 match_data: Dict[str, Any],
                                 method: ScoringMethod = None,
                                 config: ScoringConfig = None) -> ConfidenceScore:
        """Calculate confidence score for a forensic match."""
        try:
            start_time = datetime.utcnow()
            
            # Use default method if none specified
            if not method:
                method = self.default_method
            
            # Use default config if none specified
            if not config:
                config = ScoringConfig(method=method)
            
            self.logger.info(f"Calculating confidence using {method.value} method")
            
            # Calculate confidence based on method
            if method == ScoringMethod.WEIGHTED_AVERAGE:
                score = await self._weighted_average_scoring(record_data, match_data, config)
            elif method == ScoringMethod.MACHINE_LEARNING:
                score = await self._ml_based_scoring(record_data, match_data, config)
            elif method == ScoringMethod.RULE_BASED:
                score = await self._rule_based_scoring(record_data, match_data, config)
            elif method == ScoringMethod.HYBRID:
                score = await self._hybrid_scoring(record_data, match_data, config)
            elif method == ScoringMethod.ADAPTIVE:
                score = await self._adaptive_scoring(record_data, match_data, config)
            else:
                score = await self._weighted_average_scoring(record_data, match_data, config)
            
            # Update statistics
            self.total_scores_calculated += 1
            
            # Store score
            self.scoring_history.append(score)
            
            # Update processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_scoring_time(processing_time)
            
            self.logger.info(f"Confidence calculation completed: {score.confidence_level.value} ({score.overall_score:.3f})")
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error in confidence calculation: {e}")
            return None
    
    async def _weighted_average_scoring(self, record_data: Dict[str, Any], 
                                      match_data: Dict[str, Any],
                                      config: ScoringConfig) -> ConfidenceScore:
        """Calculate confidence using weighted average method."""
        try:
            factor_scores = {}
            
            # Calculate individual factor scores
            factor_scores[ConfidenceFactor.DATA_QUALITY] = self._calculate_data_quality_score(record_data)
            factor_scores[ConfidenceFactor.MATCH_STRENGTH] = self._calculate_match_strength_score(match_data)
            factor_scores[ConfidenceFactor.ALGORITHM_RELIABILITY] = self._calculate_algorithm_reliability_score(match_data)
            factor_scores[ConfidenceFactor.HISTORICAL_ACCURACY] = self._calculate_historical_accuracy_score(record_data)
            factor_scores[ConfidenceFactor.CONTEXT_RELEVANCE] = self._calculate_context_relevance_score(record_data, match_data)
            
            # Calculate weighted average
            total_score = 0.0
            total_weight = 0.0
            
            for factor, score in factor_scores.items():
                weight = config.weights.get(factor, 1.0)
                total_score += score * weight
                total_weight += weight
            
            overall_score = total_score / total_weight if total_weight > 0 else 0.0
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(overall_score, config.thresholds)
            
            # Create confidence score
            score = ConfidenceScore(
                record_id=record_data.get('id', 'unknown'),
                overall_score=overall_score,
                confidence_level=confidence_level,
                factor_scores=factor_scores,
                method=ScoringMethod.WEIGHTED_AVERAGE,
                metadata={'scoring_method': 'weighted_average'}
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error in weighted average scoring: {e}")
            return None
    
    async def _ml_based_scoring(self, record_data: Dict[str, Any], 
                               match_data: Dict[str, Any],
                               config: ScoringConfig) -> ConfidenceScore:
        """Calculate confidence using machine learning method."""
        try:
            if not self.ml_model:
                # Fall back to weighted average if ML model not available
                return await self._weighted_average_scoring(record_data, match_data, config)
            
            # Extract features for ML model
            features = self._extract_ml_features(record_data, match_data)
            
            if not features:
                return await self._weighted_average_scoring(record_data, match_data, config)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict confidence score
            predicted_score = self.ml_model.predict(features_scaled)[0]
            
            # Ensure score is within valid range
            predicted_score = max(0.0, min(1.0, predicted_score))
            
            # Calculate factor scores for transparency
            factor_scores = {
                ConfidenceFactor.DATA_QUALITY: self._calculate_data_quality_score(record_data),
                ConfidenceFactor.MATCH_STRENGTH: self._calculate_match_strength_score(match_data),
                ConfidenceFactor.ALGORITHM_RELIABILITY: self._calculate_algorithm_reliability_score(match_data),
                ConfidenceFactor.HISTORICAL_ACCURACY: self._calculate_historical_accuracy_score(record_data),
                ConfidenceFactor.CONTEXT_RELEVANCE: self._calculate_context_relevance_score(record_data, match_data)
            }
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(predicted_score, config.thresholds)
            
            # Create confidence score
            score = ConfidenceScore(
                record_id=record_data.get('id', 'unknown'),
                overall_score=predicted_score,
                confidence_level=confidence_level,
                factor_scores=factor_scores,
                method=ScoringMethod.MACHINE_LEARNING,
                metadata={
                    'scoring_method': 'ml_based',
                    'ml_model_used': 'random_forest',
                    'feature_importance': self.feature_importance
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error in ML-based scoring: {e}")
            return await self._weighted_average_scoring(record_data, match_data, config)
    
    async def _rule_based_scoring(self, record_data: Dict[str, Any], 
                                 match_data: Dict[str, Any],
                                 config: ScoringConfig) -> ConfidenceScore:
        """Calculate confidence using rule-based method."""
        try:
            factor_scores = {}
            
            # Apply rule-based scoring for each factor
            factor_scores[ConfidenceFactor.DATA_QUALITY] = self._apply_data_quality_rules(record_data)
            factor_scores[ConfidenceFactor.MATCH_STRENGTH] = self._apply_match_strength_rules(match_data)
            factor_scores[ConfidenceFactor.ALGORITHM_RELIABILITY] = self._apply_algorithm_reliability_rules(match_data)
            factor_scores[ConfidenceFactor.HISTORICAL_ACCURACY] = self._apply_historical_accuracy_rules(record_data)
            factor_scores[ConfidenceFactor.CONTEXT_RELEVANCE] = self._apply_context_relevance_rules(record_data, match_data)
            
            # Apply rule-based combination logic
            overall_score = self._apply_combination_rules(factor_scores)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(overall_score, config.thresholds)
            
            # Create confidence score
            score = ConfidenceScore(
                record_id=record_data.get('id', 'unknown'),
                overall_score=overall_score,
                confidence_level=confidence_level,
                factor_scores=factor_scores,
                method=ScoringMethod.RULE_BASED,
                metadata={'scoring_method': 'rule_based'}
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error in rule-based scoring: {e}")
            return None
    
    async def _hybrid_scoring(self, record_data: Dict[str, Any], 
                             match_data: Dict[str, Any],
                             config: ScoringConfig) -> ConfidenceScore:
        """Calculate confidence using hybrid method."""
        try:
            # Get scores from multiple methods
            weighted_score = await self._weighted_average_scoring(record_data, match_data, config)
            rule_score = await self._rule_based_scoring(record_data, match_data, config)
            
            if not weighted_score or not rule_score:
                return weighted_score or rule_score
            
            # Combine scores with weights
            hybrid_score = (weighted_score.overall_score * 0.6) + (rule_score.overall_score * 0.4)
            
            # Combine factor scores
            combined_factor_scores = {}
            for factor in ConfidenceFactor:
                if factor in weighted_score.factor_scores and factor in rule_score.factor_scores:
                    combined_factor_scores[factor] = (
                        weighted_score.factor_scores[factor] * 0.6 +
                        rule_score.factor_scores[factor] * 0.4
                    )
                elif factor in weighted_score.factor_scores:
                    combined_factor_scores[factor] = weighted_score.factor_scores[factor]
                elif factor in rule_score.factor_scores:
                    combined_factor_scores[factor] = rule_score.factor_scores[factor]
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(hybrid_score, config.thresholds)
            
            # Create confidence score
            score = ConfidenceScore(
                record_id=record_data.get('id', 'unknown'),
                overall_score=hybrid_score,
                confidence_level=confidence_level,
                factor_scores=combined_factor_scores,
                method=ScoringMethod.HYBRID,
                metadata={
                    'scoring_method': 'hybrid',
                    'weighted_score': weighted_score.overall_score,
                    'rule_score': rule_score.overall_score
                }
            )
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error in hybrid scoring: {e}")
            return await self._weighted_average_scoring(record_data, match_data, config)
    
    async def _adaptive_scoring(self, record_data: Dict[str, Any], 
                               match_data: Dict[str, Any],
                               config: ScoringConfig) -> ConfidenceScore:
        """Calculate confidence using adaptive method."""
        try:
            # Start with hybrid scoring
            base_score = await self._hybrid_scoring(record_data, match_data, config)
            
            if not base_score:
                return None
            
            # Apply adaptive adjustments based on historical performance
            adjusted_score = self._apply_adaptive_adjustments(base_score, record_data)
            
            # Update the score
            base_score.overall_score = adjusted_score
            base_score.confidence_level = self._determine_confidence_level(adjusted_score, config.thresholds)
            base_score.method = ScoringMethod.ADAPTIVE
            base_score.metadata['scoring_method'] = 'adaptive'
            base_score.metadata['adjustment_applied'] = adjusted_score - base_score.overall_score
            
            return base_score
            
        except Exception as e:
            self.logger.error(f"Error in adaptive scoring: {e}")
            return await self._hybrid_scoring(record_data, match_data, config)
    
    def _calculate_data_quality_score(self, record_data: Dict[str, Any]) -> float:
        """Calculate data quality score."""
        try:
            score = 0.0
            factors = 0
            
            # Completeness
            if 'completeness' in record_data:
                score += record_data['completeness']
                factors += 1
            
            # Consistency
            if 'consistency' in record_data:
                score += record_data['consistency']
                factors += 1
            
            # Freshness
            if 'timestamp' in record_data:
                age_hours = (datetime.utcnow() - record_data['timestamp']).total_seconds() / 3600
                freshness_score = max(0.0, 1.0 - (age_hours / 8760))  # 1 year max
                score += freshness_score
                factors += 1
            
            # Source credibility
            if 'source_credibility' in record_data:
                score += record_data['source_credibility']
                factors += 1
            
            return score / factors if factors > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating data quality score: {e}")
            return 0.5
    
    def _calculate_match_strength_score(self, match_data: Dict[str, Any]) -> float:
        """Calculate match strength score."""
        try:
            score = 0.0
            factors = 0
            
            # Similarity score
            if 'similarity' in match_data:
                score += match_data['similarity']
                factors += 1
            
            # Match confidence
            if 'confidence' in match_data:
                score += match_data['confidence']
                factors += 1
            
            # Algorithm score
            if 'algorithm_score' in match_data:
                score += match_data['algorithm_score']
                factors += 1
            
            return score / factors if factors > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating match strength score: {e}")
            return 0.5
    
    def _calculate_algorithm_reliability_score(self, match_data: Dict[str, Any]) -> float:
        """Calculate algorithm reliability score."""
        try:
            # Base reliability scores for different algorithms
            algorithm_reliability = {
                'exact_match': 1.0,
                'hash_match': 0.95,
                'fuzzy_match': 0.85,
                'ai_fuzzy': 0.90,
                'statistical': 0.80,
                'ml_based': 0.88
            }
            
            algorithm = match_data.get('algorithm', 'fuzzy_match')
            return algorithm_reliability.get(algorithm, 0.75)
            
        except Exception as e:
            self.logger.error(f"Error calculating algorithm reliability score: {e}")
            return 0.75
    
    def _calculate_historical_accuracy_score(self, record_data: Dict[str, Any]) -> float:
        """Calculate historical accuracy score."""
        try:
            # This would integrate with historical performance data
            # For now, return a default score
            return 0.80
            
        except Exception as e:
            self.logger.error(f"Error calculating historical accuracy score: {e}")
            return 0.80
    
    def _calculate_context_relevance_score(self, record_data: Dict[str, Any], 
                                         match_data: Dict[str, Any]) -> float:
        """Calculate context relevance score."""
        try:
            score = 0.0
            factors = 0
            
            # Domain relevance
            if 'domain' in record_data and 'domain' in match_data:
                if record_data['domain'] == match_data['domain']:
                    score += 1.0
                else:
                    score += 0.5
                factors += 1
            
            # Time relevance
            if 'timestamp' in record_data and 'timestamp' in match_data:
                time_diff = abs((record_data['timestamp'] - match_data['timestamp']).total_seconds())
                if time_diff < 3600:  # 1 hour
                    score += 1.0
                elif time_diff < 86400:  # 1 day
                    score += 0.8
                elif time_diff < 604800:  # 1 week
                    score += 0.6
                else:
                    score += 0.4
                factors += 1
            
            # Geographic relevance
            if 'location' in record_data and 'location' in match_data:
                if record_data['location'] == match_data['location']:
                    score += 1.0
                else:
                    score += 0.5
                factors += 1
            
            return score / factors if factors > 0 else 0.7
            
        except Exception as e:
            self.logger.error(f"Error calculating context relevance score: {e}")
            return 0.7
    
    def _apply_data_quality_rules(self, record_data: Dict[str, Any]) -> float:
        """Apply rule-based data quality scoring."""
        try:
            score = 0.0
            rules_passed = 0
            
            # Rule 1: Required fields present
            required_fields = ['id', 'timestamp', 'source']
            if all(field in record_data for field in required_fields):
                score += 1.0
                rules_passed += 1
            
            # Rule 2: Data freshness
            if 'timestamp' in record_data:
                age_hours = (datetime.utcnow() - record_data['timestamp']).total_seconds() / 3600
                if age_hours < 24:
                    score += 1.0
                elif age_hours < 168:  # 1 week
                    score += 0.8
                elif age_hours < 720:  # 1 month
                    score += 0.6
                else:
                    score += 0.4
                rules_passed += 1
            
            # Rule 3: Data completeness
            if 'completeness' in record_data and record_data['completeness'] > 0.8:
                score += 1.0
                rules_passed += 1
            
            return score / rules_passed if rules_passed > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Error applying data quality rules: {e}")
            return 0.5
    
    def _apply_match_strength_rules(self, match_data: Dict[str, Any]) -> float:
        """Apply rule-based match strength scoring."""
        try:
            score = 0.0
            rules_passed = 0
            
            # Rule 1: High similarity threshold
            if 'similarity' in match_data:
                if match_data['similarity'] > 0.9:
                    score += 1.0
                elif match_data['similarity'] > 0.8:
                    score += 0.9
                elif match_data['similarity'] > 0.7:
                    score += 0.8
                else:
                    score += 0.6
                rules_passed += 1
            
            # Rule 2: Multiple algorithm agreement
            if 'algorithms_used' in match_data:
                algorithm_count = len(match_data['algorithms_used'])
                if algorithm_count >= 3:
                    score += 1.0
                elif algorithm_count >= 2:
                    score += 0.9
                else:
                    score += 0.7
                rules_passed += 1
            
            return score / rules_passed if rules_passed > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Error applying match strength rules: {e}")
            return 0.5
    
    def _apply_algorithm_reliability_rules(self, match_data: Dict[str, Any]) -> float:
        """Apply rule-based algorithm reliability scoring."""
        try:
            algorithm = match_data.get('algorithm', 'unknown')
            
            # Rule-based reliability scores
            if algorithm in ['exact_match', 'hash_match']:
                return 1.0
            elif algorithm in ['ai_fuzzy', 'fuzzy_match']:
                return 0.9
            elif algorithm in ['statistical', 'ml_based']:
                return 0.8
            else:
                return 0.7
                
        except Exception as e:
            self.logger.error(f"Error applying algorithm reliability rules: {e}")
            return 0.7
    
    def _apply_historical_accuracy_rules(self, record_data: Dict[str, Any]) -> float:
        """Apply rule-based historical accuracy scoring."""
        try:
            # This would integrate with historical performance data
            # For now, return a default score based on source type
            source_type = record_data.get('source_type', 'unknown')
            
            if source_type in ['verified', 'trusted']:
                return 0.9
            elif source_type in ['standard', 'normal']:
                return 0.8
            else:
                return 0.7
                
        except Exception as e:
            self.logger.error(f"Error applying historical accuracy rules: {e}")
            return 0.7
    
    def _apply_context_relevance_rules(self, record_data: Dict[str, Any], 
                                     match_data: Dict[str, Any]) -> float:
        """Apply rule-based context relevance scoring."""
        try:
            score = 0.0
            rules_passed = 0
            
            # Rule 1: Domain match
            if 'domain' in record_data and 'domain' in match_data:
                if record_data['domain'] == match_data['domain']:
                    score += 1.0
                else:
                    score += 0.5
                rules_passed += 1
            
            # Rule 2: Time proximity
            if 'timestamp' in record_data and 'timestamp' in match_data:
                time_diff = abs((record_data['timestamp'] - match_data['timestamp']).total_seconds())
                if time_diff < 3600:  # 1 hour
                    score += 1.0
                elif time_diff < 86400:  # 1 day
                    score += 0.9
                elif time_diff < 604800:  # 1 week
                    score += 0.8
                else:
                    score += 0.6
                rules_passed += 1
            
            return score / rules_passed if rules_passed > 0 else 0.7
            
        except Exception as e:
            self.logger.error(f"Error applying context relevance rules: {e}")
            return 0.7
    
    def _apply_combination_rules(self, factor_scores: Dict[ConfidenceFactor, float]) -> float:
        """Apply rules for combining factor scores."""
        try:
            # Rule 1: Minimum threshold for critical factors
            critical_factors = [ConfidenceFactor.DATA_QUALITY, ConfidenceFactor.MATCH_STRENGTH]
            for factor in critical_factors:
                if factor in factor_scores and factor_scores[factor] < 0.5:
                    return 0.0  # Fail if critical factor is too low
            
            # Rule 2: Weighted average with penalties
            total_score = 0.0
            total_weight = 0.0
            
            for factor, score in factor_scores.items():
                weight = 1.0
                if factor in critical_factors:
                    weight = 1.5  # Higher weight for critical factors
                
                total_score += score * weight
                total_weight += weight
            
            overall_score = total_score / total_weight if total_weight > 0 else 0.0
            
            # Rule 3: Apply penalties for low scores
            penalty_factors = [score for score in factor_scores.values() if score < 0.6]
            if penalty_factors:
                penalty = np.mean(penalty_factors) * 0.2
                overall_score -= penalty
            
            return max(0.0, min(1.0, overall_score))
            
        except Exception as e:
            self.logger.error(f"Error applying combination rules: {e}")
            return 0.5
    
    def _determine_confidence_level(self, score: float, thresholds: Dict[ConfidenceLevel, float]) -> ConfidenceLevel:
        """Determine confidence level based on score and thresholds."""
        try:
            if score >= thresholds.get(ConfidenceLevel.CERTAIN, 0.95):
                return ConfidenceLevel.CERTAIN
            elif score >= thresholds.get(ConfidenceLevel.VERY_HIGH, 0.90):
                return ConfidenceLevel.VERY_HIGH
            elif score >= thresholds.get(ConfidenceLevel.HIGH, 0.80):
                return ConfidenceLevel.HIGH
            elif score >= thresholds.get(ConfidenceLevel.MODERATE, 0.70):
                return ConfidenceLevel.MODERATE
            elif score >= thresholds.get(ConfidenceLevel.LOW, 0.60):
                return ConfidenceLevel.LOW
            else:
                return ConfidenceLevel.VERY_LOW
                
        except Exception as e:
            self.logger.error(f"Error determining confidence level: {e}")
            return ConfidenceLevel.MODERATE
    
    def _extract_ml_features(self, record_data: Dict[str, Any], 
                            match_data: Dict[str, Any]) -> List[float]:
        """Extract features for ML model."""
        try:
            features = []
            
            # Data quality features
            features.append(self._calculate_data_quality_score(record_data))
            features.append(self._calculate_match_strength_score(match_data))
            features.append(self._calculate_algorithm_reliability_score(match_data))
            features.append(self._calculate_historical_accuracy_score(record_data))
            features.append(self._calculate_context_relevance_score(record_data, match_data))
            
            # Additional features
            features.append(record_data.get('completeness', 0.5))
            features.append(record_data.get('consistency', 0.5))
            features.append(match_data.get('similarity', 0.5))
            features.append(match_data.get('confidence', 0.5))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting ML features: {e}")
            return []
    
    def _apply_adaptive_adjustments(self, base_score: ConfidenceScore, 
                                  record_data: Dict[str, Any]) -> float:
        """Apply adaptive adjustments to base score."""
        try:
            adjusted_score = base_score.overall_score
            
            # Adjust based on historical performance
            if self.performance_metrics:
                accuracy = self.performance_metrics.get('scoring_accuracy', 0.8)
                if accuracy < 0.7:
                    adjusted_score *= 0.9  # Reduce confidence if historical accuracy is low
                elif accuracy > 0.9:
                    adjusted_score *= 1.1  # Increase confidence if historical accuracy is high
                
                # Ensure score stays within bounds
                adjusted_score = max(0.0, min(1.0, adjusted_score))
            
            return adjusted_score
            
        except Exception as e:
            self.logger.error(f"Error applying adaptive adjustments: {e}")
            return base_score.overall_score
    
    async def _initialize_ml_model(self):
        """Initialize machine learning model."""
        try:
            # Initialize Random Forest model
            self.ml_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Initialize scaler
            self.scaler = StandardScaler()
            
            self.logger.info("ML model initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML model: {e}")
    
    async def _update_performance_metrics(self):
        """Update performance metrics periodically."""
        while True:
            try:
                # Calculate scoring accuracy based on historical data
                if len(self.scoring_history) > 10:
                    recent_scores = self.scoring_history[-100:]  # Last 100 scores
                    
                    # This would integrate with actual validation data
                    # For now, use a simple heuristic
                    self.scoring_accuracy = 0.85  # Placeholder
                
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                self.logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_scores(self):
        """Clean up old confidence scores."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=30)
                
                # Remove old scores
                self.scoring_history = [
                    score for score in self.scoring_history
                    if score.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up old scores: {e}")
                await asyncio.sleep(3600)
    
    def _update_average_scoring_time(self, new_time: float):
        """Update average scoring time."""
        self.average_scoring_time = (
            (self.average_scoring_time * self.total_scores_calculated + new_time) /
            (self.total_scores_calculated + 1)
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'total_scores_calculated': self.total_scores_calculated,
            'average_scoring_time': self.average_scoring_time,
            'scoring_accuracy': self.scoring_accuracy,
            'scoring_methods_enabled': {
                'weighted_average': True,
                'ml_based': self.enable_ml_training,
                'rule_based': True,
                'hybrid': True,
                'adaptive': self.enable_adaptive_scoring
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'default_method': 'hybrid',
        'enable_ml_training': True,
        'enable_adaptive_scoring': True,
        'min_confidence_threshold': 0.6
    }
    
    # Initialize confidence scorer
    scorer = ConfidenceScorer(config)
    
    print("ConfidenceScorer system initialized successfully!")
