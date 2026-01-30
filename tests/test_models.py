"""Tests for Stack Forge."""

import pytest
from stack_forge.models import StackConfig, CloudProvider, Environment


class TestStackConfig:
    """Test StackConfig model."""

    def test_create_basic_stack(self):
        """Test creating a basic stack configuration."""
        stack = StackConfig(
            name="test-stack",
            description="Test stack for CI",
        )
        assert stack.name == "test-stack"
        assert stack.provider == CloudProvider.AWS
        assert stack.environment == Environment.DEV

    def test_default_tags(self):
        """Test default tags generation."""
        stack = StackConfig(
            name="test-stack",
            organization="testorg",
            project="testproject",
        )
        tags = stack.get_default_tags()
        assert tags["ManagedBy"] == "stack-forge"
        assert tags["Organization"] == "testorg"
        assert tags["Project"] == "testproject"
