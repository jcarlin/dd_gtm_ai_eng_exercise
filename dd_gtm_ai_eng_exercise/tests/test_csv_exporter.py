"""Tests for CSV exporter."""
import csv
import pytest
from pathlib import Path
from utils.csv_exporter import CSVExporter


class TestCSVExporter:
    """Test CSVExporter class."""

    def test_export_valid_data(self, sample_processed_speakers, temp_output_dir):
        """Test exporting valid processed speaker data to CSV."""
        exporter = CSVExporter()
        output_file = temp_output_dir / "test_email_list.csv"

        exporter.export_to_csv(sample_processed_speakers, str(output_file))

        # Verify file was created
        assert output_file.exists()

        # Read and verify CSV contents
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3

        # Verify headers
        expected_headers = [
            "Speaker Name",
            "Speaker Title",
            "Speaker Company",
            "Company Category",
            "Email Subject",
            "Email Body"
        ]
        assert list(rows[0].keys()) == expected_headers

        # Verify first row (Builder with Large company - has email)
        assert rows[0]["Speaker Name"] == "John Smith"
        assert rows[0]["Speaker Title"] == "Project Manager"
        assert rows[0]["Speaker Company"] == "ABC Construction"
        assert rows[0]["Company Category"] == "Builder"
        assert rows[0]["Email Subject"] == "See DroneDeploy at DCW Booth #42"
        assert "John" in rows[0]["Email Body"]

        # Verify second row (Partner - no email)
        assert rows[1]["Speaker Name"] == "Jane Doe"
        assert rows[1]["Company Category"] == "Partner"
        assert rows[1]["Email Subject"] == ""
        assert rows[1]["Email Body"] == ""

        # Verify third row (Builder but Small company - no email)
        assert rows[2]["Speaker Name"] == "Bob Builder"
        assert rows[2]["Company Category"] == "Builder"
        assert rows[2]["Email Subject"] == ""
        assert rows[2]["Email Body"] == ""

    def test_export_empty_list(self, temp_output_dir):
        """Test exporting empty speaker list."""
        exporter = CSVExporter()
        output_file = temp_output_dir / "empty.csv"

        exporter.export_to_csv([], str(output_file))

        # Verify file was created
        assert output_file.exists()

        # Read and verify only headers exist
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 0

    def test_export_creates_directory(self, tmp_path):
        """Test that export creates parent directory if it doesn't exist."""
        exporter = CSVExporter()
        output_file = tmp_path / "new_dir" / "output.csv"

        # Create minimal valid speaker for testing
        from utils.models import ProcessedSpeaker, Category, CompanySize
        speaker = ProcessedSpeaker(
            name="Test",
            title="Manager",
            company="TestCo",
            category=Category.OTHER,
            company_size=CompanySize.UNKNOWN,
            reasoning="Test reasoning string"
        )

        exporter.export_to_csv([speaker], str(output_file))

        # Verify directory and file were created
        assert output_file.parent.exists()
        assert output_file.exists()

    def test_export_utf8_encoding(self, temp_output_dir):
        """Test that CSV handles UTF-8 characters correctly."""
        from utils.models import ProcessedSpeaker, Category, CompanySize

        # Create speaker with special characters
        speaker = ProcessedSpeaker(
            name="José García",
            title="Directeur Général",
            company="Société française",
            category=Category.OWNER,
            company_size=CompanySize.LARGE,
            reasoning="French company with accented characters",
            email_subject="Visitez notre stand",
            email_body="Bonjour José, venez voir notre démonstration..."
        )

        exporter = CSVExporter()
        output_file = temp_output_dir / "utf8_test.csv"

        exporter.export_to_csv([speaker], str(output_file))

        # Read and verify UTF-8 characters preserved
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "José García" in content
        assert "Directeur Général" in content
        assert "Société française" in content
        assert "Visitez notre stand" in content

    def test_csv_column_order(self, sample_processed_speakers, temp_output_dir):
        """Test that CSV columns are in the exact required order."""
        exporter = CSVExporter()
        output_file = temp_output_dir / "column_order.csv"

        exporter.export_to_csv(sample_processed_speakers, str(output_file))

        with open(output_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()

        expected_order = "Speaker Name,Speaker Title,Speaker Company,Company Category,Email Subject,Email Body"
        assert first_line == expected_order