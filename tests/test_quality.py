import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import ScanRequest, scan_records


class QualityRuleTests(unittest.TestCase):
    def test_invalid_records_are_rejected_with_reasons(self):
        request = ScanRequest(batch_name="test", records=[{"order_id": "1", "customer_id": "C1", "amount": 10}, {"order_id": "2", "customer_id": None, "amount": -4}])
        result = scan_records(request)
        self.assertEqual(result["valid_rows"], 1)
        self.assertEqual(result["rejected_rows"], 1)
        self.assertEqual(len(result["rejections"][0]["reasons"]), 2)
