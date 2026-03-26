#!/usr/bin/env python3
"""
Migration Tools Test Suite
Tests for CR_ prefix migration and data structure transformation tools
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
from pathlib import Path
from datetime import datetime

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'migration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'validation'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'backup'))

from cr_prefix_migrator import CRPrefixMigrator
from data_structure_transformer import DataStructureTransformer
from cr_compliance_validator import CRComplianceValidator
from backup_manager import BackupManager


class TestCRPrefixMigrator(unittest.TestCase):
    """Test CR_ prefix migrator"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.migrator = CRPrefixMigrator(dry_run=True)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_variable_migration(self):
        """Test variable name migration"""
        # Create test Python file
        test_file = Path(self.temp_dir) / "test.py"
        test_content = '''
def calculate_odds(price, probability):
    event_id = "test_event"
    market = "moneyline"
    finding = {"type": "arbitrage", "confidence": 0.9}
    return event_id, market, finding

class TestClass:
    def __init__(self, sport, team):
        self.sport = sport
        self.team = team
        self.timestamp = datetime.now()
'''
        test_file.write_text(test_content)
        
        # Run migration
        result = self.migrator.migrate_file(str(test_file))
        
        # Check results
        self.assertTrue(result['success'])
        self.assertGreater(result['changes_made'], 0)
        self.assertTrue(result['backup_created'])
    
    def test_function_parameter_migration(self):
        """Test function parameter migration"""
        test_file = Path(self.temp_dir) / "test_params.py"
        test_content = '''
def analyze_event(event_id, sport, home_team, away_team):
    return {"event_id": event_id, "sport": sport}

def process_market(market, odds, line):
    return {"market": market, "odds": odds, "line": line}
'''
        test_file.write_text(test_content)
        
        # Run migration
        result = self.migrator.migrate_file(str(test_file))
        
        # Check results
        self.assertTrue(result['success'])
        self.assertGreater(result['changes_made'], 0)
    
    def test_exclude_existing_cr_prefix(self):
        """Test that existing CR_ prefixes are not modified"""
        test_file = Path(self.temp_dir) / "test_existing.py"
        test_content = '''
def test_function():
    CR_event_id = "already_cr"
    CR_market = "already_cr"
    price = 100  # This should be migrated
    return CR_event_id, CR_market, price
'''
        test_file.write_text(test_content)
        
        # Run migration
        result = self.migrator.migrate_file(str(test_file))
        
        # Check results
        self.assertTrue(result['success'])
        self.assertEqual(result['changes_made'], 1)  # Only 'price' should be migrated
    
    def test_directory_migration(self):
        """Test directory migration"""
        # Create test files
        test_dir = Path(self.temp_dir) / "test_dir"
        test_dir.mkdir()
        
        (test_dir / "file1.py").write_text("price = 100\nmarket = 'test'")
        (test_dir / "file2.py").write_text("event_id = 'test'\nsport = 'NBA'")
        
        # Run migration
        results = self.migrator.migrate_directory(str(test_dir))
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['success'] for r in results))


class TestDataStructureTransformer(unittest.TestCase):
    """Test data structure transformer"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.transformer = DataStructureTransformer(dry_run=True)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_json_key_transformation(self):
        """Test JSON key transformation"""
        # Create test JSON file
        test_file = Path(self.temp_dir) / "test.json"
        test_data = {
            "event_id": "test_event",
            "sport": "NBA",
            "markets": [
                {
                    "market": "moneyline",
                    "odds": {"home": -110, "away": 110},
                    "bookmaker": "DraftKings"
                }
            ],
            "findings": [
                {
                    "type": "arbitrage",
                    "confidence": 0.95,
                    "description": "Test arbitrage"
                }
            ]
        }
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        # Run transformation
        result = self.transformer.transform_json_file(str(test_file))
        
        # Check results
        self.assertTrue(result['success'])
        self.assertGreater(result['changes_made'], 0)
        self.assertTrue(result['backup_created'])
    
    def test_python_file_transformation(self):
        """Test Python file string literal transformation"""
        test_file = Path(self.temp_dir) / "test.py"
        test_content = '''
data = {
    "event_id": "test_event",
    "sport": "NBA",
    "market": "moneyline"
}

finding = {
    "type": "arbitrage",
    "confidence": 0.9
}
'''
        test_file.write_text(test_content)
        
        # Run transformation
        result = self.transformer.transform_python_file(str(test_file))
        
        # Check results
        self.assertTrue(result['success'])
        self.assertGreater(result['changes_made'], 0)
    
    def test_decimal_to_american_conversion(self):
        """Test decimal odds to American odds conversion"""
        # Test positive conversion
        american = self.transformer.decimal_to_american(2.5)
        self.assertEqual(american, 150)
        
        # Test negative conversion
        american = self.transformer.decimal_to_american(1.8)
        self.assertEqual(american, -125)
        
        # Test edge cases
        american = self.transformer.decimal_to_american(2.0)
        self.assertEqual(american, 100)
        
        american = self.transformer.decimal_to_american(1.0)
        self.assertEqual(american, 0)  # Invalid odds


class TestCRComplianceValidator(unittest.TestCase):
    """Test CR_ compliance validator"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.validator = CRComplianceValidator()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_python_file_validation(self):
        """Test Python file validation"""
        # Create test Python file
        test_file = Path(self.temp_dir) / "test.py"
        test_content = '''
def calculate_odds(CR_price, CR_probability):
    event_id = "test_event"  # Non-compliant
    CR_market = "moneyline"  # Compliant
    finding = {"type": "arbitrage"}  # Non-compliant
    return CR_market, finding

class TestClass:
    def __init__(self, CR_sport, team):  # team is non-compliant
        self.CR_sport = CR_sport
        self.team = team  # Non-compliant
'''
        test_file.write_text(test_content)
        
        # Run validation
        result = self.validator.validate_python_file(str(test_file))
        
        # Check results
        self.assertTrue(result['success'])
        self.assertGreater(result['total_variables'], 0)
        self.assertLess(result['compliance_rate'], 100.0)  # Should not be 100% compliant
        self.assertGreater(len(result['non_compliant_variables']), 0)
    
    def test_json_file_validation(self):
        """Test JSON file validation"""
        # Create test JSON file
        test_file = Path(self.temp_dir) / "test.json"
        test_data = {
            "CR_event_id": "test_event",  # Compliant
            "sport": "NBA",  # Non-compliant
            "CR_markets": [  # Compliant
                {
                    "market": "moneyline",  # Non-compliant
                    "CR_odds": {"home": -110, "away": 110}  # Compliant
                }
            ]
        }
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        # Run validation
        result = self.validator.validate_json_file(str(test_file))
        
        # Check results
        self.assertTrue(result['success'])
        self.assertGreater(result['total_keys'], 0)
        self.assertLess(result['compliance_rate'], 100.0)  # Should not be 100% compliant
        self.assertGreater(len(result['non_compliant_keys']), 0)
    
    def test_excluded_variables(self):
        """Test that excluded variables are not flagged"""
        test_file = Path(self.temp_dir) / "test_excluded.py"
        test_content = '''
def test_function(self, args, kwargs):
    # Common programming patterns should be excluded
    for i in range(10):
        item = items[i]
        if item is not None:
            result = process_item(item)
    return result
'''
        test_file.write_text(test_content)
        
        # Run validation
        result = self.validator.validate_python_file(str(test_file))
        
        # Check results
        self.assertTrue(result['success'])
        # Most variables should be excluded, resulting in high compliance
        self.assertGreater(result['compliance_rate'], 80.0)
    
    def test_directory_validation(self):
        """Test directory validation"""
        # Create test files
        test_dir = Path(self.temp_dir) / "test_dir"
        test_dir.mkdir()
        
        (test_dir / "test1.py").write_text("CR_var = 'test'\nnon_cr = 'bad'")
        (test_dir / "test2.json").write_text('{"CR_key": "good", "bad_key": "bad"}')
        
        # Run validation
        results = self.validator.validate_directory(str(test_dir))
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['success'] for r in results))


class TestBackupManager(unittest.TestCase):
    """Test backup manager"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.temp_dir) / "backups"
        self.backup_manager = BackupManager(str(self.backup_dir))
        
        # Create test data
        self.test_data_dir = Path(self.temp_dir) / "test_data"
        self.test_data_dir.mkdir()
        (self.test_data_dir / "file1.txt").write_text("test content 1")
        (self.test_data_dir / "file2.txt").write_text("test content 2")
        (self.test_data_dir / "subdir").mkdir()
        (self.test_data_dir / "subdir" / "file3.txt").write_text("test content 3")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_create_backup(self):
        """Test backup creation"""
        # Create backup
        result = self.backup_manager.create_backup(str(self.test_data_dir), "test_backup")
        
        # Check results
        self.assertTrue(result['success'])
        self.assertEqual(result['backup_name'], "test_backup")
        self.assertGreater(result['size_bytes'], 0)
        self.assertTrue(Path(result['backup_path']).exists())
    
    def test_restore_backup(self):
        """Test backup restoration"""
        # Create backup first
        backup_result = self.backup_manager.create_backup(str(self.test_data_dir), "test_backup")
        self.assertTrue(backup_result['success'])
        
        # Remove original data
        shutil.rmtree(self.test_data_dir)
        
        # Restore backup
        restore_dir = Path(self.temp_dir) / "restored_data"
        result = self.backup_manager.restore_backup("test_backup", str(restore_dir))
        
        # Check results
        self.assertTrue(result['success'])
        self.assertTrue(restore_dir.exists())
        self.assertTrue((restore_dir / "file1.txt").exists())
        self.assertTrue((restore_dir / "file2.txt").exists())
        self.assertTrue((restore_dir / "subdir" / "file3.txt").exists())
    
    def test_list_backups(self):
        """Test backup listing"""
        # Create multiple backups
        self.backup_manager.create_backup(str(self.test_data_dir), "backup1")
        self.backup_manager.create_backup(str(self.test_data_dir), "backup2")
        
        # List backups
        backups = self.backup_manager.list_backups()
        
        # Check results
        self.assertEqual(len(backups), 2)
        backup_names = {b['backup_name'] for b in backups}
        self.assertIn("backup1", backup_names)
        self.assertIn("backup2", backup_names)
    
    def test_delete_backup(self):
        """Test backup deletion"""
        # Create backup
        backup_result = self.backup_manager.create_backup(str(self.test_data_dir), "test_backup")
        self.assertTrue(backup_result['success'])
        
        # Delete backup
        result = self.backup_manager.delete_backup("test_backup")
        
        # Check results
        self.assertTrue(result['success'])
        
        # Verify backup is gone
        backups = self.backup_manager.list_backups()
        backup_names = {b['backup_name'] for b in backups}
        self.assertNotIn("test_backup", backup_names)
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups"""
        # Set max backups to 2
        self.backup_manager.max_backups = 2
        
        # Create 4 backups
        self.backup_manager.create_backup(str(self.test_data_dir), "backup1")
        self.backup_manager.create_backup(str(self.test_data_dir), "backup2")
        self.backup_manager.create_backup(str(self.test_data_dir), "backup3")
        self.backup_manager.create_backup(str(self.test_data_dir), "backup4")
        
        # Run cleanup
        result = self.backup_manager.cleanup_old_backups()
        
        # Check results
        self.assertTrue(result['success'])
        self.assertEqual(result['backups_before'], 4)
        self.assertEqual(result['backups_after'], 2)
        self.assertEqual(result['backups_deleted'], 2)


class TestIntegration(unittest.TestCase):
    """Integration tests for migration tools"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_full_migration_workflow(self):
        """Test complete migration workflow"""
        # Create test project structure
        project_dir = Path(self.temp_dir) / "test_project"
        project_dir.mkdir()
        
        # Create test files
        (project_dir / "data.py").write_text('''
event_id = "test_event"
sport = "NBA"
price = 100
market = "moneyline"
''')
        
        (project_dir / "config.json").write_text(json.dumps({
            "event_id": "test_event",
            "sport": "NBA",
            "market": "moneyline",
            "price": 100
        }, indent=2))
        
        # Step 1: Create backup
        backup_manager = BackupManager(str(Path(self.temp_dir) / "backups"))
        backup_result = backup_manager.create_backup(str(project_dir), "pre_migration_backup")
        self.assertTrue(backup_result['success'])
        
        # Step 2: Validate before migration
        validator = CRComplianceValidator()
        validation_before = validator.validate_directory(str(project_dir))
        self.assertGreater(len(validation_before), 0)
        
        # Step 3: Run migration (dry run first)
        migrator = CRPrefixMigrator(dry_run=True)
        migration_dry_run = migrator.migrate_directory(str(project_dir))
        self.assertTrue(all(r['success'] for r in migration_dry_run))
        
        # Step 4: Run data structure transformation (dry run first)
        transformer = DataStructureTransformer(dry_run=True)
        transformation_dry_run = transformer.transform_directory(str(project_dir))
        self.assertTrue(all(r['success'] for r in transformation_dry_run))
        
        # Step 5: Verify workflow completed successfully
        self.assertTrue(backup_result['success'])
        self.assertGreater(len(validation_before), 0)
        self.assertGreater(len(migration_dry_run), 0)
        self.assertGreater(len(transformation_dry_run), 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
