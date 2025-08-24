Unit Tests for AI Service
Tests all AI service components including reconciliation, fraud detection, NLP, and OCR

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

# Import the AI service components
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ai_service"))

from main import (
    ReconciliationRequest,
    ReconciliationResponse,
    FraudDetectionRequest,
    FraudDetectionResponse,
    NLPRequest,
    NLPResponse,
    OCRRequest,
    OCRResponse,
    HealthResponse,
)

class TestReconciliationModels:
    """Test reconciliation request/response models."""

    def test_reconciliation_request_creation(self):
        """Test creating a reconciliation request."""
        source_data = [{"id": "1", "name": "Test", "amount": 100}]
        target_data = [{"id": "1", "name": "Test", "amount": 100}]
        matching_fields = ["id", "name"]

        request = ReconciliationRequest(
            source_data=source_data,
            target_data=target_data,
            confidence_threshold=0.8,
            matching_fields=matching_fields,
        )

        assert request.source_data == source_data
        assert request.target_data == target_data
        assert request.confidence_threshold == 0.8
        assert request.matching_fields == matching_fields

    def test_reconciliation_response_creation(self):
        """Test creating a reconciliation response."""
        matches = [{"source": {"id": "1"}, "target": {"id": "1"}}]
        confidence_scores = [0.95]
        unmatched_source = [{"id": "2"}]
        unmatched_target = [{"id": "3"}]
        processing_time = 0.5

        response = ReconciliationResponse(
            matches=matches,
            confidence_scores=confidence_scores,
            unmatched_source=unmatched_source,
            unmatched_target=unmatched_target,
            processing_time=processing_time,
        )

        assert response.matches == matches
        assert response.confidence_scores == confidence_scores
        assert response.unmatched_source == unmatched_source
        assert response.unmatched_target == unmatched_target
        assert response.processing_time == processing_time

class TestFraudDetectionModels:
    """Test fraud detection request/response models."""

    def test_fraud_detection_request_creation(self):
        """Test creating a fraud detection request."""
        transaction_data = [{"amount": 1000, "location": "NYC", "frequency": 5}]
        user_profile = {"usual_location": "NYC"}
        risk_threshold = 0.7

        request = FraudDetectionRequest(
            transaction_data=transaction_data,
            user_profile=user_profile,
            risk_threshold=risk_threshold,
        )

        assert request.transaction_data == transaction_data
        assert request.user_profile == user_profile
        assert request.risk_threshold == risk_threshold

    def test_fraud_detection_response_creation(self):
        """Test creating a fraud detection response."""
        fraud_scores = [0.2, 0.8]
        risk_levels = ["low", "high"]
        flagged_transactions = [1]
        risk_factors = [["normal"], ["high_amount", "unusual_location"]]
        processing_time = 0.3

        response = FraudDetectionResponse(
            fraud_scores=fraud_scores,
            risk_levels=risk_levels,
            flagged_transactions=flagged_transactions,
            risk_factors=risk_factors,
            processing_time=processing_time,
        )

        assert response.fraud_scores == fraud_scores
        assert response.risk_levels == risk_levels
        assert response.flagged_transactions == flagged_transactions
        assert response.risk_factors == risk_factors
        assert response.processing_time == processing_time

class TestNLPModels:
    """Test NLP request/response models."""

    def test_nlp_request_creation(self):
        """Test creating an NLP request."""
        text = "This is a test document for NLP processing."
        language = "en"
        tasks = ["entities", "sentiment", "keywords"]

        request = NLPRequest(text=text, language=language, tasks=tasks)

        assert request.text == text
        assert request.language == language
        assert request.tasks == tasks

    def test_nlp_response_creation(self):
        """Test creating an NLP response."""
        entities = [{"text": "John Doe", "type": "PERSON"}]
        sentiment = {"positive": 0.6, "negative": 0.2, "neutral": 0.2}
        keywords = ["test", "document", "NLP"]
        summary = "Test document for NLP processing."
        processing_time = 0.4

        response = NLPResponse(
            entities=entities,
            sentiment=sentiment,
            keywords=keywords,
            summary=summary,
            processing_time=processing_time,
        )

        assert response.entities == entities
        assert response.sentiment == sentiment
        assert response.keywords == keywords
        assert response.summary == summary
        assert response.processing_time == processing_time

class TestOCRModels:
    """Test OCR request/response models."""

    def test_ocr_request_creation(self):
        """Test creating an OCR request."""
        document_data = b"Sample document content"
        document_type = "pdf"
        language = "en"

        request = OCRRequest(
            document_data=document_data, document_type=document_type, language=language
        )

        assert request.document_data == document_data
        assert request.document_type == document_type
        assert request.language == language

    def test_ocr_response_creation(self):
        """Test creating an OCR response."""
        extracted_text = "Sample extracted text from document"
        confidence = 0.85
        metadata = {"document_type": "pdf", "language": "en", "size": 100}
        processing_time = 0.6

        response = OCRResponse(
            extracted_text=extracted_text,
            confidence=confidence,
            metadata=metadata,
            processing_time=processing_time,
        )

        assert response.extracted_text == extracted_text
        assert response.confidence == confidence
        assert response.metadata == metadata
        assert response.processing_time == processing_time

class TestHealthResponse:
    """Test health response model."""

    def test_health_response_creation(self):
        """Test creating a health response."""
        status = "healthy"
        timestamp = datetime.utcnow()
        version = "1.0.0"
        uptime = 3600.0

        response = HealthResponse(
            status=status, timestamp=timestamp, version=version, uptime=uptime
        )

        assert response.status == status
        assert response.timestamp == timestamp
        assert response.version == version
        assert response.uptime == uptime

class TestDataValidation:
    """Test data validation for all models."""

    def test_reconciliation_request_validation(self):
        """Test reconciliation request validation."""
        # Valid request
        valid_request = ReconciliationRequest(
            source_data=[{"id": "1"}], target_data=[{"id": "1"}], matching_fields=["id"]
        )
        assert valid_request.confidence_threshold == 0.8  # Default value

        # Test with custom confidence threshold
        custom_request = ReconciliationRequest(
            source_data=[{"id": "1"}],
            target_data=[{"id": "1"}],
            matching_fields=["id"],
            confidence_threshold=0.9,
        )
        assert custom_request.confidence_threshold == 0.9

    def test_fraud_detection_request_validation(self):
        """Test fraud detection request validation."""
        # Valid request
        valid_request = FraudDetectionRequest(
            transaction_data=[{"amount": 100}], risk_threshold=0.8
        )
        assert valid_request.risk_threshold == 0.8

        # Test with user profile
        request_with_profile = FraudDetectionRequest(
            transaction_data=[{"amount": 100}],
            user_profile={"usual_location": "NYC"},
            risk_threshold=0.7,
        )
        assert request_with_profile.user_profile["usual_location"] == "NYC"

    def test_nlp_request_validation(self):
        """Test NLP request validation."""
        # Valid request
        valid_request = NLPRequest(text="Test text", tasks=["entities", "sentiment"])
        assert valid_request.language == "en"  # Default value
        assert valid_request.tasks == ["entities", "sentiment"]

    def test_ocr_request_validation(self):
        """Test OCR request validation."""
        # Valid request
        valid_request = OCRRequest(document_data=b"test", document_type="pdf")
        assert valid_request.language == "en"  # Default value
        assert valid_request.document_type == "pdf"

class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_reconciliation_request_serialization(self):
        """Test reconciliation request can be serialized to JSON."""
        request = ReconciliationRequest(
            source_data=[{"id": "1"}], target_data=[{"id": "1"}], matching_fields=["id"]
        )

        # Convert to dict
        request_dict = request.dict()
        assert "source_data" in request_dict
        assert "target_data" in request_dict
        assert "matching_fields" in request_dict

        # Convert to JSON
        request_json = request.json()
        assert isinstance(request_json, str)

        # Parse back to dict
        parsed_dict = json.loads(request_json)
        assert parsed_dict["source_data"] == [{"id": "1"}]

    def test_fraud_detection_response_serialization(self):
        """Test fraud detection response can be serialized to JSON."""
        response = FraudDetectionResponse(
            fraud_scores=[0.2, 0.8],
            risk_levels=["low", "high"],
            flagged_transactions=[1],
            risk_factors=[["normal"], ["high_amount"]],
            processing_time=0.3,
        )

        # Convert to dict
        response_dict = response.dict()
        assert "fraud_scores" in response_dict
        assert "risk_levels" in response_dict
        assert "flagged_transactions" in response_dict

        # Convert to JSON
        response_json = response.json()
        assert isinstance(response_json, str)

        # Parse back to dict
        parsed_dict = json.loads(response_json)
        assert parsed_dict["fraud_scores"] == [0.2, 0.8]

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
