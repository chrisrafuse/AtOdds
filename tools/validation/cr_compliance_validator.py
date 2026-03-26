#!/usr/bin/env python3
"""
CR_ Compliance Validation Tool
Validates CR_ prefix compliance across the codebase
"""

import os
import re
import sys
import json
import ast
from datetime import datetime
from typing import Dict, List, Set, Any, Optional, Tuple
from pathlib import Path

class CRComplianceValidator:
    """CR_ prefix compliance validator"""
    
    def __init__(self):
        self.validation_log = []
        self.compliance_issues = []
        
        # CR_ compliance patterns
        self.cr_prefix_pattern = re.compile(r'\bCR_[a-zA-Z_][a-zA-Z0-9_]*\b')
        self.non_cr_variable_pattern = re.compile(r'\b(?<!CR_)[a-z][a-zA-Z0-9_]*\b')
        self.function_param_pattern = re.compile(r'\b(?<!CR_)[a-z][a-zA-Z0-9_]*(?=\s*[,):=])')
        
        # Files to exclude from validation
        self.exclude_files = {
            '__pycache__',
            '.git',
            'node_modules',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '.venv',
            'venv',
            'env',
            'dist',
            'build',
            '*.egg-info',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.DS_Store',
            'Thumbs.db'
        }
        
        # Variables that don't need CR_ prefix
        self.excluded_variables = {
            # Python built-ins and standard library
            'self', 'cls', 'args', 'kwargs', 'item', 'items', 'key', 'value',
            'i', 'j', 'k', 'index', 'idx', 'count', 'length', 'len', 'size',
            'path', 'file', 'dir', 'directory', 'name', 'filename', 'filepath',
            'data', 'content', 'text', 'string', 'str', 'number', 'num',
            'bool', 'true', 'false', 'none', 'null', 'undefined',
            'list', 'dict', 'set', 'tuple', 'array', 'object',
            'type', 'kind', 'sort', 'order', 'mode', 'state', 'status',
            'result', 'output', 'input', 'return', 'response', 'request',
            'error', 'exception', 'exc', 'e', 'err',
            'time', 'date', 'now', 'today', 'current', 'start', 'end',
            'new', 'old', 'original', 'modified', 'updated', 'created',
            'min', 'max', 'sum', 'avg', 'mean', 'total', 'count',
            'tmp', 'temp', 'temporary', 'cache', 'buffer',
            # Common programming patterns
            'x', 'y', 'z', 'a', 'b', 'c', 'n', 'm', 't', 'f',
            'is', 'has', 'can', 'should', 'must', 'will', 'would',
            'get', 'set', 'add', 'remove', 'delete', 'create', 'update',
            'load', 'save', 'read', 'write', 'open', 'close',
            'init', 'setup', 'config', 'configure', 'prepare',
            'test', 'check', 'verify', 'validate', 'confirm',
            'run', 'execute', 'start', 'stop', 'pause', 'resume',
            'import', 'from', 'as', 'def', 'class', 'if', 'else', 'elif',
            'for', 'while', 'with', 'try', 'except', 'finally', 'raise',
            'pass', 'break', 'continue', 'return', 'yield', 'lambda',
            'and', 'or', 'not', 'in', 'is', 'del', 'global', 'nonlocal'
        }
        
        # Context patterns where CR_ prefix is not required
        self.context_exclusions = [
            # Import statements
            r'^\s*(?:from\s+\S+\s+)?import\s+',
            # Function definitions
            r'^\s*def\s+',
            # Class definitions
            r'^\s*class\s+',
            # Decorators
            r'^\s*@\w+',
            # Comments
            r'^\s*#',
            # String literals
            r'["\'][^"\']*["\']',
        ]
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from validation"""
        file_name = os.path.basename(file_path)
        
        # Check exclude patterns
        for pattern in self.exclude_files:
            if pattern.startswith('*'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern in file_path:
                return True
        
        return False
    
    def extract_variables_from_ast(self, tree: ast.AST) -> Set[str]:
        """Extract variable names from AST"""
        variables = set()
        
        class VariableVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if isinstance(node.ctx, (ast.Store, ast.Load)):
                    variables.add(node.id)
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                # Add function parameters
                for arg in node.args.args:
                    variables.add(arg.arg)
                self.generic_visit(node)
            
            def visit_AsyncFunctionDef(self, node):
                # Add async function parameters
                for arg in node.args.args:
                    variables.add(arg.arg)
                self.generic_visit(node)
        
        visitor = VariableVisitor()
        visitor.visit(tree)
        return variables
    
    def validate_python_file(self, file_path: str) -> Dict[str, Any]:
        """Validate Python file for CR_ compliance"""
        result = {
            'file_path': file_path,
            'total_variables': 0,
            'cr_compliant_variables': 0,
            'non_compliant_variables': [],
            'excluded_variables': [],
            'compliance_rate': 0.0,
            'success': False,
            'error': None,
            'issues': []
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract variables from AST
            all_variables = self.extract_variables_from_ast(tree)
            
            # Filter variables
            cr_compliant = set()
            non_compliant = set()
            excluded = set()
            
            for var in all_variables:
                # Skip excluded variables
                if var in self.excluded_variables:
                    excluded.add(var)
                # Check CR_ compliance
                elif var.startswith('CR_'):
                    cr_compliant.add(var)
                else:
                    non_compliant.add(var)
            
            result['total_variables'] = len(all_variables)
            result['cr_compliant_variables'] = len(cr_compliant)
            result['non_compliant_variables'] = list(non_compliant)
            result['excluded_variables'] = list(excluded)
            
            # Calculate compliance rate
            if result['total_variables'] > 0:
                result['compliance_rate'] = (len(cr_compliant) / result['total_variables']) * 100
            
            # Check for specific issues
            issues = []
            
            # Check function parameters
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for arg in node.args.args:
                        if not arg.arg.startswith('CR_') and arg.arg not in self.excluded_variables:
                            issues.append({
                                'type': 'non_compliant_parameter',
                                'line': node.lineno,
                                'function': node.name,
                                'parameter': arg.arg
                            })
            
            # Check variable assignments
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if not target.id.startswith('CR_') and target.id not in self.excluded_variables:
                                issues.append({
                                    'type': 'non_compliant_assignment',
                                    'line': node.lineno,
                                    'variable': target.id
                                })
            
            result['issues'] = issues
            result['success'] = True
            
            # Log validation
            self.validation_log.append({
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'compliance_rate': result['compliance_rate'],
                'issues_found': len(issues)
            })
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def validate_json_file(self, file_path: str) -> Dict[str, Any]:
        """Validate JSON file for CR_ compliance"""
        result = {
            'file_path': file_path,
            'total_keys': 0,
            'cr_compliant_keys': 0,
            'non_compliant_keys': [],
            'compliance_rate': 0.0,
            'success': False,
            'error': None,
            'issues': []
        }
        
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract all keys
            all_keys = self.extract_json_keys(data)
            
            # Filter keys
            cr_compliant = set()
            non_compliant = set()
            
            for key in all_keys:
                # Skip excluded keys
                if key in self.excluded_variables:
                    continue
                # Check CR_ compliance
                elif key.startswith('CR_'):
                    cr_compliant.add(key)
                else:
                    non_compliant.add(key)
            
            result['total_keys'] = len(all_keys)
            result['cr_compliant_keys'] = len(cr_compliant)
            result['non_compliant_keys'] = list(non_compliant)
            
            # Calculate compliance rate
            if result['total_keys'] > 0:
                result['compliance_rate'] = (len(cr_compliant) / result['total_keys']) * 100
            
            result['success'] = True
            
            # Log validation
            self.validation_log.append({
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'compliance_rate': result['compliance_rate'],
                'issues_found': len(non_compliant)
            })
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def extract_json_keys(self, data: Any, keys: Set[str] = None) -> Set[str]:
        """Extract all keys from JSON data"""
        if keys is None:
            keys = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                keys.add(key)
                self.extract_json_keys(value, keys)
        elif isinstance(data, list):
            for item in data:
                self.extract_json_keys(item, keys)
        
        return keys
    
    def validate_directory(self, directory: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """Validate all files in directory"""
        results = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if not self.should_exclude_file(file_path):
                        if file.endswith('.py'):
                            result = self.validate_python_file(file_path)
                            results.append(result)
                        elif file.endswith('.json'):
                            result = self.validate_json_file(file_path)
                            results.append(result)
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                
                if not self.should_exclude_file(file_path):
                    if file.endswith('.py'):
                        result = self.validate_python_file(file_path)
                        results.append(result)
                    elif file.endswith('.json'):
                        result = self.validate_json_file(file_path)
                        results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate validation report"""
        total_files = len(results)
        successful_files = sum(1 for r in results if r['success'])
        
        # Calculate overall compliance
        total_variables = sum(r.get('total_variables', 0) + r.get('total_keys', 0) for r in results)
        total_compliant = sum(r.get('cr_compliant_variables', 0) + r.get('cr_compliant_keys', 0) for r in results)
        overall_compliance = (total_compliant / total_variables * 100) if total_variables > 0 else 0
        
        report = f"""
# CR_ Compliance Validation Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Files Processed: {total_files}
- Successful Validations: {successful_files}
- Failed Validations: {total_files - successful_files}
- Overall Compliance Rate: {overall_compliance:.1f}%
- Total Variables/Keys: {total_variables}
- CR_ Compliant: {total_compliant}

## File Details
"""
        
        for result in results:
            status = "✅ COMPLIANT" if result['success'] and result.get('compliance_rate', 0) >= 80 else "❌ NON-COMPLIANT"
            compliance_rate = result.get('compliance_rate', 0)
            
            report += f"\n### {status}: {result['file_path']}\n"
            report += f"- Compliance Rate: {compliance_rate:.1f}%\n"
            
            if 'total_variables' in result:
                report += f"- Variables: {result['total_variables']} (CR_: {result['cr_compliant_variables']})\n"
            elif 'total_keys' in result:
                report += f"- Keys: {result['total_keys']} (CR_: {result['cr_compliant_keys']})\n"
            
            if result['error']:
                report += f"- Error: {result['error']}\n"
            
            # Show non-compliant items
            non_compliant = result.get('non_compliant_variables', []) or result.get('non_compliant_keys', [])
            if non_compliant:
                report += f"- Non-compliant: {', '.join(non_compliant[:10])}"
                if len(non_compliant) > 10:
                    report += f" (and {len(non_compliant) - 10} more)"
                report += "\n"
            
            # Show issues
            if result.get('issues'):
                report += "- Issues:\n"
                for issue in result['issues'][:5]:
                    if issue['type'] == 'non_compliant_parameter':
                        report += f"  - Line {issue['line']}: Parameter '{issue['parameter']}' in function '{issue['function']}'\n"
                    elif issue['type'] == 'non_compliant_assignment':
                        report += f"  - Line {issue['line']}: Variable '{issue['variable']}' assignment\n"
                
                if len(result['issues']) > 5:
                    report += f"  - (and {len(result['issues']) - 5} more issues)\n"
        
        return report
    
    def save_report(self, report: str, output_path: str = "cr_compliance_validation_report.md"):
        """Save validation report to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Validation report saved to: {output_path}")


def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CR_ Compliance Validation Tool")
    parser.add_argument("path", help="Path to file or directory to validate")
    parser.add_argument("--report", default="cr_compliance_validation_report.md", help="Report output file")
    parser.add_argument("--recursive", action="store_true", default=True, help="Process directories recursively")
    parser.add_argument("--threshold", type=float, default=80.0, help="Compliance threshold percentage")
    
    args = parser.parse_args()
    
    # Create validator
    validator = CRComplianceValidator()
    
    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        return 1
    
    # Perform validation
    if os.path.isfile(args.path):
        if args.path.endswith('.py'):
            results = [validator.validate_python_file(args.path)]
        elif args.path.endswith('.json'):
            results = [validator.validate_json_file(args.path)]
        else:
            print(f"Error: '{args.path}' is not a supported file type (.py, .json)")
            return 1
    elif os.path.isdir(args.path):
        results = validator.validate_directory(args.path, args.recursive)
    else:
        print(f"Error: '{args.path}' is neither a file nor a directory")
        return 1
    
    # Generate and save report
    report = validator.generate_report(results)
    validator.save_report(report, args.report)
    
    # Print summary
    successful_files = sum(1 for r in results if r['success'])
    total_variables = sum(r.get('total_variables', 0) + r.get('total_keys', 0) for r in results)
    total_compliant = sum(r.get('cr_compliant_variables', 0) + r.get('cr_compliant_keys', 0) for r in results)
    overall_compliance = (total_compliant / total_variables * 100) if total_variables > 0 else 0
    
    print(f"\nValidation Complete!")
    print(f"Files Processed: {len(results)}")
    print(f"Successful: {successful_files}")
    print(f"Overall Compliance: {overall_compliance:.1f}%")
    
    # Check threshold
    if overall_compliance >= args.threshold:
        print(f"✅ Compliance threshold ({args.threshold}%) met!")
        return 0
    else:
        print(f"❌ Compliance threshold ({args.threshold}%) not met!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
