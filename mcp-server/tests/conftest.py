"""Pytest configuration and shared fixtures for Isabl MCP Server tests."""

import pytest


# Configure pytest-asyncio to use auto mode for async tests
pytest_plugins = ['pytest_asyncio']


@pytest.fixture
def mock_settings(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("ISABL_API_URL", "https://test.isabl.io/api/v1/")
    monkeypatch.setenv("ISABL_API_TOKEN", "test-token-12345")
    monkeypatch.setenv("ISABL_TIMEOUT", "30")
    monkeypatch.setenv("ISABL_VERIFY_SSL", "true")
    monkeypatch.setenv("ISABL_LOG_LEVEL", "WARNING")


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for testing."""
    return {
        "pk": 12345,
        "status": "SUCCEEDED",
        "storage_url": "/data/analyses/12345",
        "results": {
            "vcf": "/data/analyses/12345/variants.vcf",
            "bam": "/data/analyses/12345/aligned.bam",
            "metrics": "/data/analyses/12345/metrics.tsv",
        },
        "application": {
            "pk": 1,
            "name": "MUTECT",
            "version": "2.4.3",
        },
        "targets": [
            {"pk": 100, "system_id": "ISB_E000001"}
        ],
        "references": [
            {"pk": 101, "system_id": "ISB_E000002"}
        ],
    }


@pytest.fixture
def sample_individual_tree():
    """Sample individual tree for testing."""
    return {
        "pk": 1,
        "system_id": "ISB_H000001",
        "identifier": "PATIENT001",
        "species": "HUMAN",
        "samples": [
            {
                "pk": 10,
                "system_id": "ISB_S000001",
                "category": "TUMOR",
                "experiments": [
                    {
                        "pk": 100,
                        "system_id": "ISB_E000001",
                        "technique": {"method": "WGS"},
                    },
                    {
                        "pk": 101,
                        "system_id": "ISB_E000002",
                        "technique": {"method": "RNA-Seq"},
                    },
                ],
            },
            {
                "pk": 11,
                "system_id": "ISB_S000002",
                "category": "NORMAL",
                "experiments": [
                    {
                        "pk": 102,
                        "system_id": "ISB_E000003",
                        "technique": {"method": "WGS"},
                    },
                ],
            },
        ],
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "pk": 102,
        "title": "Whole Genome Sequencing Study",
        "short_title": "WGS_STUDY",
        "description": "A comprehensive WGS study of cancer samples",
        "storage_usage": 5_000_000_000_000,  # 5TB in bytes
    }


@pytest.fixture
def sample_application_data():
    """Sample application data for testing."""
    return {
        "pk": 1,
        "name": "MUTECT",
        "version": "2.4.3",
        "assembly": "GRCh38",
        "species": "HUMAN",
        "description": "Somatic variant calling using MuTect2 with panel of normals",
        "application_class": "isabl_apps.somatic.Mutect2",
        "application_settings": {
            "pon_path": "/data/references/pon.vcf.gz",
            "gnomad_path": "/data/references/gnomad.vcf.gz",
            "threads": 8,
            "memory_gb": 32,
        },
        "application_results": {
            "vcf": {
                "frontend_type": "igv-vcf",
                "description": "Filtered somatic variants",
                "verbose_name": "VCF Output",
            },
            "stats": {
                "frontend_type": "text-file",
                "description": "Variant statistics",
                "verbose_name": "Stats",
            },
        },
    }


@pytest.fixture
def sample_experiments_list():
    """Sample list of experiments for testing."""
    return [
        {
            "pk": 100,
            "system_id": "ISB_E000001",
            "technique": {"method": "WGS", "pk": 1},
            "sample": {"pk": 10, "category": "TUMOR"},
            "projects": [{"pk": 102}],
        },
        {
            "pk": 101,
            "system_id": "ISB_E000002",
            "technique": {"method": "WGS", "pk": 1},
            "sample": {"pk": 11, "category": "NORMAL"},
            "projects": [{"pk": 102}],
        },
        {
            "pk": 102,
            "system_id": "ISB_E000003",
            "technique": {"method": "RNA-Seq", "pk": 2},
            "sample": {"pk": 10, "category": "TUMOR"},
            "projects": [{"pk": 102}],
        },
    ]


@pytest.fixture
def sample_analyses_list():
    """Sample list of analyses for testing."""
    return [
        {
            "pk": 1000,
            "status": "SUCCEEDED",
            "application": {"pk": 1, "name": "MUTECT"},
        },
        {
            "pk": 1001,
            "status": "SUCCEEDED",
            "application": {"pk": 1, "name": "MUTECT"},
        },
        {
            "pk": 1002,
            "status": "FAILED",
            "application": {"pk": 2, "name": "STAR"},
        },
        {
            "pk": 1003,
            "status": "STARTED",
            "application": {"pk": 2, "name": "STAR"},
        },
    ]
