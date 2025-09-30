"""
CSV exporter for generating final email_list.csv from processed speaker data.
"""
import csv
from pathlib import Path
from typing import List

from utils.models import ProcessedSpeaker


class CSVExporter:
    def __init__(self):
        """Initialize CSV exporter."""
        pass

    def export_to_csv(self, processed_speakers: List[ProcessedSpeaker], output_file: str) -> None:
        """
        Export processed speaker data to CSV format.

        Args:
            processed_speakers: List of ProcessedSpeaker objects
            output_file: Path to output CSV file
        """
        # Define CSV columns as specified in requirements
        csv_columns = [
            "Speaker Name",
            "Speaker Title",
            "Speaker Company",
            "Company Category",
            "Email Subject",
            "Email Body"
        ]

        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()

            for speaker in processed_speakers:
                writer.writerow({
                    "Speaker Name": speaker.name,
                    "Speaker Title": speaker.title,
                    "Speaker Company": speaker.company,
                    "Company Category": speaker.category.value,
                    "Email Subject": speaker.email_subject,
                    "Email Body": speaker.email_body
                })

        print(f"✅ CSV exported: {output_file}")
        print(f"   Total records: {len(processed_speakers)}")
        print(f"   Records with emails: {len([s for s in processed_speakers if s.email_subject])}")