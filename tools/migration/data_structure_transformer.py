#!/usr/bin/env python3
"""
Data Structure Transformation Tool
Transform data structures to CR_ specification compliance
"""

import os
import json
import sys
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class DataStructureTransformer:
    """Data structure transformation tool for CR_ compliance"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.transformation_log = []
        
        # Transformation mappings
        self.field_mappings = {
            # Event fields
            'id': 'CR_event_id',
            'name': 'CR_event_name',
            'sport': 'CR_sport',
            'home_team': 'CR_home_team',
            'away_team': 'CR_away_team',
            'commence_time': 'CR_commence_time',
            'start_time': 'CR_start_time',
            'game_time': 'CR_game_time',
            
            # Market fields
            'market': 'CR_market',
            'markets': 'CR_markets',
            'bookmaker': 'CR_bookmaker',
            'sportsbook': 'CR_sportsbook',
            'last_update': 'CR_last_update',
            'last_updated': 'CR_last_updated',
            'updated_at': 'CR_updated_at',
            
            # Outcome fields
            'outcome': 'CR_outcome',
            'outcomes': 'CR_outcomes',
            'price': 'CR_price',
            'odds': 'CR_odds',
            'line': 'CR_line',
            'value': 'CR_value',
            
            # Analysis fields
            'finding': 'CR_finding',
            'findings': 'CR_findings',
            'type': 'CR_type',
            'confidence': 'CR_confidence',
            'description': 'CR_description',
            'details': 'CR_details',
            
            # Snapshot fields
            'snapshot': 'CR_snapshot',
            'events': 'CR_events',
            'timestamp': 'CR_timestamp',
            'generated_at': 'CR_generated_at',
            'source': 'CR_source',
            
            # Briefing fields
            'briefing': 'CR_briefing',
            'summary': 'CR_summary',
            'total_events': 'CR_total_events',
            'total_markets': 'CR_total_markets',
            'top_findings': 'CR_top_findings',
            'recommendations': 'CR_recommendations',
            
            # Performance fields
            'performance': 'CR_performance',
            'metrics': 'CR_metrics',
            'duration': 'CR_duration',
            'memory_usage': 'CR_memory_usage',
            'cpu_usage': 'CR_cpu_usage',
            
            # Tool fields
            'tool': 'CR_tool',
            'tools': 'CR_tools',
            'tool_name': 'CR_tool_name',
            'tool_call': 'CR_tool_call',
            'tool_calls': 'CR_tool_calls',
            'inputs': 'CR_inputs',
            'outputs': 'CR_outputs',
            
            # Step fields
            'step': 'CR_step',
            'steps': 'CR_steps',
            'step_name': 'CR_step_name',
            'execution': 'CR_execution',
            
            # Session fields
            'session': 'CR_session',
            'sessions': 'CR_sessions',
            'session_id': 'CR_session_id',
            'trace': 'CR_trace',
            'traces': 'CR_traces',
        }
        
        # Type conversion mappings
        self.type_conversions = {
            'decimal_odds': 'american_odds',
            'decimal_price': 'american_price',
            'float_odds': 'american_odds',
            'float_price': 'american_price',
            'datetime': 'iso_string',
            'date': 'iso_string',
            'time': 'iso_string',
        }
    
    def transform_dict_keys(self, data: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
        """Transform dictionary keys to CR_ compliance"""
        if not isinstance(data, dict):
            return data
        
        transformed = {}
        
        for key, value in data.items():
            # Skip if already CR_ compliant
            if key.startswith('CR_'):
                transformed[key] = value
                continue
            
            # Apply field mapping
            new_key = self.field_mappings.get(key, f'CR_{key}')
            
            # Recursively transform nested structures
            if isinstance(value, dict):
                transformed[new_key] = self.transform_dict_keys(value, new_key)
            elif isinstance(value, list):
                transformed[new_key] = self.transform_list(value, new_key)
            else:
                transformed[new_key] = self.transform_value(value, new_key)
        
        return transformed
    
    def transform_list(self, data: List[Any], parent_key: str = "") -> List[Any]:
        """Transform list elements to CR_ compliance"""
        if not isinstance(data, list):
            return data
        
        transformed = []
        
        for i, item in enumerate(data):
            if isinstance(item, dict):
                transformed.append(self.transform_dict_keys(item, f"{parent_key}[{i}]"))
            elif isinstance(item, list):
                transformed.append(self.transform_list(item, f"{parent_key}[{i}]"))
            else:
                transformed.append(item)
        
        return transformed
    
    def transform_value(self, value: Any, key: str = "") -> Any:
        """Transform individual values to CR_ compliance"""
        # Convert decimal odds to American odds
        if isinstance(value, (int, float)) and any(keyword in key.lower() for keyword in ['price', 'odds']):
            if value > 1:  # Decimal odds
                return self.decimal_to_american(value)
        
        # Convert datetime objects to ISO strings
        if isinstance(value, datetime):
            return value.isoformat()
        
        return value
    
    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American odds"""
        if decimal_odds <= 1:
            return 0  # Invalid odds
        
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    def transform_json_file(self, file_path: str) -> Dict[str, Any]:
        """Transform JSON file to CR_ compliance"""
        result = {
            'file_path': file_path,
            'changes_made': 0,
            'success': False,
            'error': None,
            'backup_created': False,
            'original_size': 0,
            'transformed_size': 0
        }
        
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
                original_content = f.read()
            
            result['original_size'] = len(original_content)
            
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(original_data, f, indent=2, ensure_ascii=False)
            result['backup_created'] = True
            
            # Transform data
            transformed_data = self.transform_dict_keys(original_data)
            
            # Count changes (simplified)
            original_keys = self.extract_all_keys(original_data)
            transformed_keys = self.extract_all_keys(transformed_data)
            result['changes_made'] = len(set(original_keys) - set(transformed_keys))
            
            # Write transformed data if not dry run
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(transformed_data, f, indent=2, ensure_ascii=False)
                
                # Get transformed size
                with open(file_path, 'r', encoding='utf-8') as f:
                    result['transformed_size'] = len(f.read())
            else:
                # Calculate transformed size for dry run
                transformed_content = json.dumps(transformed_data, indent=2, ensure_ascii=False)
                result['transformed_size'] = len(transformed_content)
            
            result['success'] = True
            
            # Log transformation
            self.transformation_log.append({
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'changes_made': result['changes_made'],
                'dry_run': self.dry_run
            })
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def extract_all_keys(self, data: Any, keys: set = None) -> set:
        """Extract all keys from nested data structure"""
        if keys is None:
            keys = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                keys.add(key)
                self.extract_all_keys(value, keys)
        elif isinstance(data, list):
            for item in data:
                self.extract_all_keys(item, keys)
        
        return keys
    
    def transform_python_file(self, file_path: str) -> Dict[str, Any]:
        """Transform Python file data structures to CR_ compliance"""
        result = {
            'file_path': file_path,
            'changes_made': 0,
            'success': False,
            'error': None,
            'backup_created': False
        }
        
        try:
            # Read Python file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            result['backup_created'] = True
            
            # Transform string literals (dictionary keys)
            modified_content = original_content
            total_changes = 0
            
            # Dictionary key patterns
            for old_key, new_key in self.field_mappings.items():
                # Pattern for dictionary keys in string literals
                pattern = f'["\']{old_key}["\']'
                replacement = f'"{new_key}"'
                matches_before = len(re.findall(pattern, modified_content))
                if matches_before > 0:
                    modified_content = re.sub(pattern, replacement, modified_content)
                    matches_after = len(re.findall(pattern, modified_content))
                    changes = matches_before - matches_after
                    total_changes += changes
            
            result['changes_made'] = total_changes
            
            # Write modified content if not dry run
            if not self.dry_run and total_changes > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
            result['success'] = True
            
            # Log transformation
            self.transformation_log.append({
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'changes_made': total_changes,
                'dry_run': self.dry_run
            })
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def transform_directory(self, directory: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """Transform all files in directory"""
        results = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common exclusions
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Transform JSON files
                    if file.endswith('.json'):
                        result = self.transform_json_file(file_path)
                        results.append(result)
                    
                    # Transform Python files
                    elif file.endswith('.py'):
                        result = self.transform_python_file(file_path)
                        results.append(result)
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                
                if file.endswith('.json'):
                    result = self.transform_json_file(file_path)
                    results.append(result)
                elif file.endswith('.py'):
                    result = self.transform_python_file(file_path)
                    results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate transformation report"""
        total_files = len(results)
        successful_files = sum(1 for r in results if r['success'])
        total_changes = sum(r['changes_made'] for r in results)
        
        report = f"""
# Data Structure Transformation Report
Generated: {datetime.now().isoformat()}
Dry Run: {self.dry_run}

## Summary
- Total Files Processed: {total_files}
- Successful Transformations: {successful_files}
- Failed Transformations: {total_files - successful_files}
- Total Changes Made: {total_changes}
- Success Rate: {(successful_files/total_files*100):.1f}%

## File Details
"""
        
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            report += f"\n### {status}: {result['file_path']}\n"
            report += f"- Changes Made: {result['changes_made']}\n"
            
            if 'original_size' in result:
                report += f"- Size Change: {result['original_size']} → {result['transformed_size']} bytes\n"
            
            if result['error']:
                report += f"- Error: {result['error']}\n"
        
        return report
    
    def save_report(self, report: str, output_path: str = "data_structure_transformation_report.md"):
        """Save transformation report to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Transformation report saved to: {output_path}")


def main():
    """Main transformation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Structure Transformation Tool")
    parser.add_argument("path", help="Path to file or directory to transform")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Perform dry run (default)")
    parser.add_argument("--execute", action="store_true", help="Execute transformation (not dry run)")
    parser.add_argument("--report", default="data_structure_transformation_report.md", help="Report output file")
    parser.add_argument("--recursive", action="store_true", default=True, help="Process directories recursively")
    
    args = parser.parse_args()
    
    # Set dry run flag
    dry_run = not args.execute
    
    # Create transformer
    transformer = DataStructureTransformer(dry_run=dry_run)
    
    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        return 1
    
    # Perform transformation
    if os.path.isfile(args.path):
        if args.path.endswith('.json'):
            results = [transformer.transform_json_file(args.path)]
        elif args.path.endswith('.py'):
            results = [transformer.transform_python_file(args.path)]
        else:
            print(f"Error: '{args.path}' is not a supported file type (.json, .py)")
            return 1
    elif os.path.isdir(args.path):
        results = transformer.transform_directory(args.path, args.recursive)
    else:
        print(f"Error: '{args.path}' is neither a file nor a directory")
        return 1
    
    # Generate and save report
    report = transformer.generate_report(results)
    transformer.save_report(report, args.report)
    
    # Print summary
    successful_files = sum(1 for r in results if r['success'])
    total_changes = sum(r['changes_made'] for r in results)
    
    print(f"\nTransformation {'(DRY RUN) ' if dry_run else ''}Complete!")
    print(f"Files Processed: {len(results)}")
    print(f"Successful: {successful_files}")
    print(f"Total Changes: {total_changes}")
    
    if dry_run:
        print("\nTo execute transformation, run with --execute flag")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
