import importlib.util
import sys
import unittest
from pathlib import Path

class TestSchemasImport(unittest.TestCase):
    def test_import_schemas(self):
        """Test that schemas.py can be imported and TOOLS_SCHEMAS is a list."""
        # read under the repository root, whatever the working directory (TASK 129 R1.3)
        spec = importlib.util.spec_from_file_location(
            "schemas", str(Path(__file__).resolve().parents[1] / ".agent" / "tools" / "schemas.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules["schemas"] = module
        spec.loader.exec_module(module)
        
        self.assertTrue(hasattr(module, "TOOLS_SCHEMAS"))
        self.assertIsInstance(module.TOOLS_SCHEMAS, list)

if __name__ == "__main__":
    unittest.main()
