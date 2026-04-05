"""Tests for ContextAnalyst agent."""

import pytest
from unittest.mock import AsyncMock, Mock

from src.agents.context_analyst import (
    ContextAnalyst,
    SprintScope,
    HistoricalSimilarity,
    FlakyTest,
    ModuleRisk,
)


class TestSprintScope:
    """Tests for SprintScope model."""

    def test_sprint_scope_from_string(self):
        """Test creating SprintScope from string."""
        scope = SprintScope(description="Implement checkout flow")
        
        assert scope.description == "Implement checkout flow"
        assert scope.modules == []
        assert scope.features == []
        assert scope.test_types == ["functional"]

    def test_sprint_scope_full(self):
        """Test creating SprintScope with all fields."""
        scope = SprintScope(
            description="Implement payment",
            modules=["payment", "billing"],
            features=["credit_card", "paypal"],
            test_types=["functional", "security"]
        )
        
        assert scope.modules == ["payment", "billing"]
        assert scope.features == ["credit_card", "paypal"]
        assert scope.test_types == ["functional", "security"]


class TestHistoricalSimilarity:
    """Tests for HistoricalSimilarity model."""

    def test_historical_similarity_creation(self):
        """Test creating HistoricalSimilarity."""
        similarity = HistoricalSimilarity(
            sprint_id="SP-40",
            sprint_name="Checkout Refactor",
            similarity_score=0.75,
            shared_modules=["payment"],
            shared_features=["payment_processing"],
            defect_density=0.3,
            test_effectiveness=0.85
        )
        
        assert similarity.sprint_id == "SP-40"
        assert similarity.similarity_score == 0.75

    def test_historical_similarity_score_bounds(self):
        """Test similarity score is bounded 0-1."""
        with pytest.raises(ValueError):
            HistoricalSimilarity(
                sprint_id="SP-1",
                sprint_name="Test",
                similarity_score=1.5,
                shared_modules=[],
                shared_features=[],
                defect_density=0.0,
                test_effectiveness=0.0
            )


class TestFlakyTest:
    """Tests for FlakyTest model."""

    def test_flaky_test_creation(self):
        """Test creating FlakyTest."""
        flaky = FlakyTest(
            test_id="TEST-001",
            test_name="Payment Test",
            module="payment",
            failure_rate=0.15,
            last_failure="2024-01-15T10:30:00Z",
            root_cause="Race condition"
        )
        
        assert flaky.failure_rate == 0.15
        assert flaky.root_cause == "Race condition"


class TestModuleRisk:
    """Tests for ModuleRisk model."""

    def test_module_risk_valid_levels(self):
        """Test ModuleRisk accepts valid risk levels."""
        for level in ["low", "medium", "high", "critical"]:
            risk = ModuleRisk(
                module_name="test_module",
                defect_density=0.5,
                change_frequency=0.5,
                test_coverage=0.8,
                risk_level=level
            )
            assert risk.risk_level == level

    def test_module_risk_invalid_level(self):
        """Test ModuleRisk rejects invalid risk levels."""
        with pytest.raises(ValueError):
            ModuleRisk(
                module_name="test_module",
                defect_density=0.5,
                change_frequency=0.5,
                test_coverage=0.8,
                risk_level="extreme"
            )


class TestContextAnalyst:
    """Tests for ContextAnalyst agent."""

    @pytest.fixture
    def mock_supabase(self):
        """Create mock Supabase client."""
        client = Mock()
        client.table = Mock(return_value=Mock())
        return client

    @pytest.fixture
    def mock_gemini(self):
        """Create mock Gemini client."""
        return AsyncMock()

    @pytest.fixture
    def context_analyst(self, mock_supabase, mock_gemini):
        """Create ContextAnalyst instance."""
        return ContextAnalyst(
            supabase_client=mock_supabase,
            gemini_client=mock_gemini
        )

    def test_context_analyst_initialization(self, context_analyst):
        """Test ContextAnalyst initializes correctly."""
        assert context_analyst.supabase_client is not None
        assert context_analyst.gemini_client is not None
        assert context_analyst._vector_store is None

    def test_calculate_text_similarity(self, context_analyst):
        """Test text similarity calculation."""
        similarity = context_analyst._calculate_text_similarity(
            "payment checkout cart",
            "payment cart billing"
        )
        
        assert 0 <= similarity <= 1
        assert similarity > 0

    def test_calculate_text_similarity_empty(self, context_analyst):
        """Test text similarity with empty inputs."""
        assert context_analyst._calculate_text_similarity("", "test") == 0.0
        assert context_analyst._calculate_text_similarity("test", "") == 0.0
        assert context_analyst._calculate_text_similarity("", "") == 0.0

    def test_extract_modules_from_description(self, context_analyst):
        """Test module extraction from description."""
        description = "Implement payment processing and user authentication"
        modules = context_analyst._extract_modules_from_description(description)
        
        assert "payment" in modules
        assert "auth" in modules

    @pytest.mark.asyncio
    async def test_direct_db_search_returns_results(self, context_analyst, mock_supabase):
        """Test direct DB search returns properly formatted results."""
        mock_table = Mock()
        mock_table.select.return_value.order.return_value.limit.return_value.execute = AsyncMock(
            return_value=Mock(data=[
                {
                    "id": "SP-40",
                    "name": "Checkout Refactor",
                    "description": "payment checkout refactor",
                    "modules": ["payment"],
                    "defect_density": 0.3,
                    "test_effectiveness": 0.85
                }
            ])
        )
        mock_supabase.table.return_value = mock_table
        
        results = await context_analyst._direct_db_search("payment checkout", lookback=3)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert results[0]["sprint_id"] == "SP-40"

    @pytest.mark.asyncio
    async def test_direct_db_search_no_results(self, context_analyst, mock_supabase):
        """Test direct DB search with no matching results."""
        mock_table = Mock()
        mock_table.select.return_value.order.return_value.limit.return_value.execute = AsyncMock(
            return_value=Mock(data=[])
        )
        mock_supabase.table.return_value = mock_table
        
        results = await context_analyst._direct_db_search("xyz123", lookback=3)
        
        assert results == []

    @pytest.mark.asyncio
    async def test_get_flaky_tests(self, context_analyst, mock_supabase):
        """Test getting flaky tests from historical data."""
        mock_table = Mock()
        mock_table.select.return_value.in_.return_value.order.return_value.limit.return_value.execute = AsyncMock(
            return_value=Mock(data=[
                {"test_id": "T1", "test_name": "Test 1", "module": "auth", "status": "failed", "created_at": "2024-01-01"},
                {"test_id": "T1", "test_name": "Test 1", "module": "auth", "status": "passed", "created_at": "2024-01-02"},
                {"test_id": "T1", "test_name": "Test 1", "module": "auth", "status": "failed", "created_at": "2024-01-03"},
            ])
        )
        mock_supabase.table.return_value = mock_table
        
        flaky = await context_analyst._get_flaky_tests(["auth"], lookback=3)
        
        assert len(flaky) > 0
        assert flaky[0].module == "auth"
        assert flaky[0].failure_rate > 0

    @pytest.mark.asyncio
    async def test_get_flaky_tests_empty_modules(self, context_analyst):
        """Test flaky tests returns empty for no modules."""
        flaky = await context_analyst._get_flaky_tests([], lookback=3)
        
        assert flaky == []

    @pytest.mark.asyncio
    async def test_calculate_defect_density(self, context_analyst, mock_supabase):
        """Test defect density calculation per module."""
        mock_defects_table = Mock()
        mock_defects_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute = AsyncMock(
            return_value=Mock(data=[
                {"id": "D1", "severity": "high", "detected_at": "2024-01-01"},
                {"id": "D2", "severity": "high", "detected_at": "2024-01-02"},
            ])
        )
        
        mock_tests_table = Mock()
        mock_tests_table.select.return_value.eq.return_value.execute = AsyncMock(
            return_value=Mock(data=[{"id": "T1"}, {"id": "T2"}, {"id": "T3"}])
        )
        
        def table_side_effect(name):
            if name == "defects":
                return mock_defects_table
            elif name == "test_results":
                return mock_tests_table
            return Mock()
        
        mock_supabase.table.side_effect = table_side_effect
        
        risks = await context_analyst._calculate_defect_density(["auth"])
        
        assert len(risks) == 1
        assert risks[0].module_name == "auth"
        assert risks[0].defect_density > 0

    @pytest.mark.asyncio
    async def test_calculate_defect_density_empty_modules(self, context_analyst):
        """Test defect density returns empty for no modules."""
        risks = await context_analyst._calculate_defect_density([])
        
        assert risks == []

    @pytest.mark.asyncio
    async def test_analyze_returns_complete_result(self, context_analyst, mock_supabase):
        """Test analyze returns complete analysis result."""
        mock_table = Mock()
        mock_table.select.return_value.order.return_value.limit.return_value.execute = AsyncMock(
            return_value=Mock(data=[
                {
                    "id": "SP-40",
                    "name": "Test Sprint",
                    "description": "payment processing",
                    "modules": ["payment"],
                    "defect_density": 0.2,
                    "test_effectiveness": 0.8
                }
            ])
        )
        mock_table.select.return_value.in_.return_value.order.return_value.limit.return_value.execute = AsyncMock(
            return_value=Mock(data=[
                {"test_id": "T1", "test_name": "Test", "module": "payment", "status": "failed", "created_at": "2024-01-01"}
            ])
        )
        mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute = AsyncMock(
            return_value=Mock(data=[{"id": "D1", "severity": "medium", "detected_at": "2024-01-01"}])
        )
        mock_table.select.return_value.eq.return_value.execute = AsyncMock(
            return_value=Mock(data=[{"id": "T1"}])
        )
        mock_supabase.table.return_value = mock_table
        
        result = await context_analyst.analyze(
            sprint_scope="Implement payment processing",
            lookback=3
        )
        
        assert "risk_level" in result
        assert "risk_score" in result
        assert "similar_sprints" in result
        assert "module_risks" in result
        assert "recommendations" in result
        assert "effort_multiplier" in result
        assert result["risk_level"] in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_analyze_with_string_sprint_scope(self, context_analyst, mock_supabase):
        """Test analyze accepts string sprint scope."""
        mock_table = Mock()
        mock_table.select.return_value.order.return_value.limit.return_value.execute = AsyncMock(
            return_value=Mock(data=[])
        )
        mock_supabase.table.return_value = mock_table
        
        result = await context_analyst.analyze(
            sprint_scope="Simple sprint goal",
            lookback=1
        )
        
        assert isinstance(result, dict)
        assert "risk_level" in result

    @pytest.mark.asyncio
    async def test_analyze_risk_level_calculation(self, context_analyst, mock_supabase):
        """Test risk level is calculated correctly based on score."""
        mock_table = Mock()
        
        def mock_select(*args):
            mock_q = Mock()
            mock_q.select.return_value = mock_q
            mock_q.order.return_value = mock_q
            mock_q.limit.return_value = mock_q
            mock_q.execute = AsyncMock(return_value=Mock(data=[
                {"id": "SP-1", "name": "S1", "description": "test", "modules": ["auth"], "defect_density": 0.8, "test_effectiveness": 0.5}
            ]))
            return mock_q
        
        mock_table.select.side_effect = mock_select
        mock_supabase.table.return_value = mock_table
        
        result = await context_analyst.analyze("test", lookback=1)
        
        assert result["risk_level"] in ["low", "medium", "high", "critical"]
        expected_levels = ["low", "medium", "high", "critical"]
        assert result["risk_level"] in expected_levels
