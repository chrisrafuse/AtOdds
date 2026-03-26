#!/usr/bin/env python3
"""
CR_ Prefix Migration Tool
Automated tool to migrate all variables to CR_ prefix compliance
"""

import os
import re
import sys
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path

class CRPrefixMigrator:
    """Automated CR_ prefix migration tool"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.migration_log = []
        self.patterns = [
            # Variable patterns (avoid existing CR_ variables)
            (r'\b(?<!CR_)(event_id|price|probability|market|finding|briefing|snapshot|game|sport|team|player|odds|line|spread|total|moneyline|home|away|bookmaker|sportsbook|outcome|data|result|value|edge|vig|stake|profit|margin|confidence|timestamp|date|time|commence|last_updated|generated|description|type|status|details|metrics|analysis|summary|report|alert|error|warning|info|debug|log|trace|session|step|tool|call|input|output|duration|performance|memory|cpu|usage|load|test|validate|check|verify|confirm|approve|reject|success|failure|complete|ready|pending|processing|running|finished|stopped|cancelled|paused|resumed|started|initialized|configured|deployed|installed|updated|upgraded|patched|fixed|resolved|closed|opened|created|deleted|removed|added|modified|changed|updated|refreshed|reloaded|restarted|reset|cleared|cleaned|optimized|enhanced|improved|upgraded|downgraded|deprecated|retired|archived|backed_up|restored|recovered|repaired|mended|healed|cured|treated|prevented|avoided|escaped|evaded|dodged|skipped|missed|ignored|overlooked|forgotten|remembered|recalled|retrieved|fetched|downloaded|uploaded|transferred|copied|moved|renamed|renumbered|reordered|reorganized|restructured|reformatted|reparsed|recompiled|reinterpreted|retranslated|reencoded|decoded|encrypted|decrypted|signed|unsigned|authenticated|authorized|permitted|denied|blocked|allowed|granted|revoked|expired|valid|invalid|active|inactive|enabled|disabled|on|off|true|false|null|none|empty|full|partial|complete|incomplete|total|subtotal|average|mean|median|mode|min|max|range|span|width|height|depth|size|scale|ratio|proportion|percentage|fraction|decimal|integer|string|number|boolean|array|object|list|dict|set|tuple|function|method|class|module|package|library|framework|system|application|service|process|thread|task|job|queue|stack|heap|tree|graph|node|edge|vertex|link|connection|network|interface|api|endpoint|route|path|url|uri|address|location|position|coordinate|index|key|value|pair|mapping|association|relationship|dependency|requirement|specification|constraint|rule|policy|standard|protocol|format|encoding|charset|language|locale|timezone|currency|symbol|unit|measure|quantity|amount|balance|budget|cost|price|fee|charge|tax|discount|surcharge|penalty|bonus|reward|incentive|commission|royalty|license|permit|certificate|credential|token|password|username|email|phone|address|contact|name|title|label|tag|category|group|set|collection|series|sequence|order|rank|priority|level|grade|score|rating|point|mark|grade|class|type|kind|sort|variety|species|genus|family|order|phylum|kingdom|domain|category|division|section|chapter|page|line|paragraph|sentence|word|character|letter|digit|symbol|sign|mark|indicator|gauge|meter|sensor|detector|monitor|scanner|reader|writer|printer|display|screen|window|dialog|form|field|input|output|button|link|menu|toolbar|statusbar|sidebar|header|footer|content|body|head|title|meta|script|style|css|html|xml|json|yaml|csv|txt|log|conf|config|ini|cfg|env|var|param|argument|option|flag|switch|setting|preference|property|attribute|feature|capability|functionality|behavior|state|condition|status|mode|type|format|style|theme|skin|layout|design|template|pattern|schema|model|entity|object|item|element|component|part|piece|segment|section|portion|fraction|share|percentage|rate|speed|velocity|acceleration|force|pressure|temperature|humidity|weather|climate|season|month|day|hour|minute|second|millisecond|microsecond|nanosecond|picosecond|femtosecond|attosecond|zeptosecond|yoctosecond)\b', 'CR_\\1'),
            
            # Function parameter patterns
            (r'\b(?<!CR_)(event_id|price|probability|market|finding|briefing|snapshot|game|sport|team|player|odds|line|spread|total|moneyline|home|away|bookmaker|sportsbook|outcome|data|result|value|edge|vig|stake|profit|margin|confidence|timestamp|date|time|commence|last_updated|generated|description|type|status|details|metrics|analysis|summary|report|alert|error|warning|info|debug|log|trace|session|step|tool|call|input|output|duration|performance|memory|cpu|usage|load|test|validate|check|verify|confirm|approve|reject|success|failure|complete|ready|pending|processing|running|finished|stopped|cancelled|paused|resumed|started|initialized|configured|deployed|installed|updated|upgraded|patched|fixed|resolved|closed|opened|created|deleted|removed|added|modified|changed|updated|refreshed|reloaded|restarted|reset|cleared|cleaned|optimized|enhanced|improved|upgraded|downgraded|deprecated|retired|archived|backed_up|restored|recovered|repaired|mended|healed|cured|treated|prevented|avoided|escaped|evaded|dodged|skipped|missed|ignored|overlooked|forgotten|remembered|recalled|retrieved|fetched|downloaded|uploaded|transferred|copied|moved|renamed|renumbered|reordered|reorganized|restructured|reformatted|reparsed|recompiled|reinterpreted|retranslated|reencoded|decoded|encrypted|decrypted|signed|unsigned|authenticated|authorized|permitted|denied|blocked|allowed|granted|revoked|expired|valid|invalid|active|inactive|enabled|disabled|on|off|true|false|null|none|empty|full|partial|complete|incomplete|total|subtotal|average|mean|median|mode|min|max|range|span|width|height|depth|size|scale|ratio|proportion|percentage|fraction|decimal|integer|string|number|boolean|array|object|list|dict|set|tuple|function|method|class|module|package|library|framework|system|application|service|process|thread|task|job|queue|stack|heap|tree|graph|node|edge|vertex|link|connection|network|interface|api|endpoint|route|path|url|uri|address|location|position|coordinate|index|key|value|pair|mapping|association|relationship|dependency|requirement|specification|constraint|rule|policy|standard|protocol|format|encoding|charset|language|locale|timezone|currency|symbol|unit|measure|quantity|amount|balance|budget|cost|price|fee|charge|tax|discount|surcharge|penalty|bonus|reward|incentive|commission|royalty|license|permit|certificate|credential|token|password|username|email|phone|address|contact|name|title|label|tag|category|group|set|collection|series|sequence|order|rank|priority|level|grade|score|rating|point|mark|grade|class|type|kind|sort|variety|species|genus|family|order|phylum|kingdom|domain|category|division|section|chapter|page|line|paragraph|sentence|word|character|letter|digit|symbol|sign|mark|indicator|gauge|meter|sensor|detector|monitor|scanner|reader|writer|printer|display|screen|window|dialog|form|field|input|output|button|link|menu|toolbar|statusbar|sidebar|header|footer|content|body|head|title|meta|script|style|css|html|xml|json|yaml|csv|txt|log|conf|config|ini|cfg|env|var|param|argument|option|flag|switch|setting|preference|property|attribute|feature|capability|functionality|behavior|state|condition|status|mode|type|format|style|theme|skin|layout|design|template|pattern|schema|model|entity|object|item|element|component|part|piece|segment|section|portion|fraction|share|percentage|rate|speed|velocity|acceleration|force|pressure|temperature|humidity|weather|climate|season|month|day|hour|minute|second|millisecond|microsecond|nanosecond|picosecond|femtosecond|attosecond|zeptosecond|yoctosecond)(?=\s*[,):=])', 'CR_\\1'),
            
            # Dictionary key patterns in string literals
            (r'["\'](?<!CR_)(event_id|price|probability|market|finding|briefing|snapshot|game|sport|team|player|odds|line|spread|total|moneyline|home|away|bookmaker|sportsbook|outcome|data|result|value|edge|vig|stake|profit|margin|confidence|timestamp|date|time|commence|last_updated|generated|description|type|status|details|metrics|analysis|summary|report|alert|error|warning|info|debug|log|trace|session|step|tool|call|input|output|duration|performance|memory|cpu|usage|load|test|validate|check|verify|confirm|approve|reject|success|failure|complete|ready|pending|processing|running|finished|stopped|cancelled|paused|resumed|started|initialized|configured|deployed|installed|updated|upgraded|patched|fixed|resolved|closed|opened|created|deleted|removed|added|modified|changed|updated|refreshed|reloaded|restarted|reset|cleared|cleaned|optimized|enhanced|improved|upgraded|downgraded|deprecated|retired|archived|backed_up|restored|recovered|repaired|mended|healed|cured|treated|prevented|avoided|escaped|evaded|dodged|skipped|missed|ignored|overlooked|forgotten|remembered|recalled|retrieved|fetched|downloaded|uploaded|transferred|copied|moved|renamed|renumbered|reordered|reorganized|restructured|reformatted|reparsed|recompiled|reinterpreted|retranslated|reencoded|decoded|encrypted|decrypted|signed|unsigned|authenticated|authorized|permitted|denied|blocked|allowed|granted|revoked|expired|valid|invalid|active|inactive|enabled|disabled|on|off|true|false|null|none|empty|full|partial|complete|incomplete|total|subtotal|average|mean|median|mode|min|max|range|span|width|height|depth|size|scale|ratio|proportion|percentage|fraction|decimal|integer|string|number|boolean|array|object|list|dict|set|tuple|function|method|class|module|package|library|framework|system|application|service|process|thread|task|job|queue|stack|heap|tree|graph|node|edge|vertex|link|connection|network|interface|api|endpoint|route|path|url|uri|address|location|position|coordinate|index|key|value|pair|mapping|association|relationship|dependency|requirement|specification|constraint|rule|policy|standard|protocol|format|encoding|charset|language|locale|timezone|currency|symbol|unit|measure|quantity|amount|balance|budget|cost|price|fee|charge|tax|discount|surcharge|penalty|bonus|reward|incentive|commission|royalty|license|permit|certificate|credential|token|password|username|email|phone|address|contact|name|title|label|tag|category|group|set|collection|series|sequence|order|rank|priority|level|grade|score|rating|point|mark|grade|class|type|kind|sort|variety|species|genus|family|order|phylum|kingdom|domain|category|division|section|chapter|page|line|paragraph|sentence|word|character|letter|digit|symbol|sign|mark|indicator|gauge|meter|sensor|detector|monitor|scanner|reader|writer|printer|display|screen|window|dialog|form|field|input|output|button|link|menu|toolbar|statusbar|sidebar|header|footer|content|body|head|title|meta|script|style|css|html|xml|json|yaml|csv|txt|log|conf|config|ini|cfg|env|var|param|argument|option|flag|switch|setting|preference|property|attribute|feature|capability|functionality|behavior|state|condition|status|mode|type|format|style|theme|skin|layout|design|template|pattern|schema|model|entity|object|item|element|component|part|piece|segment|section|portion|fraction|share|percentage|rate|speed|velocity|acceleration|force|pressure|temperature|humidity|weather|climate|season|month|day|hour|minute|second|millisecond|microsecond|nanosecond|picosecond|femtosecond|attosecond|zeptosecond|yoctosecond)["\']', '"CR_\\1"'),
        ]
        
        # Files to exclude from migration
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
        
        # Files that should be handled specially
        self.special_files = {
            'requirements.txt',
            'setup.py',
            'pyproject.toml',
            'Dockerfile',
            'docker-compose.yml',
            '.gitignore',
            'README.md',
            'CHANGELOG.md',
            'LICENSE'
        }
    
    def should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from migration"""
        file_name = os.path.basename(file_path)
        
        # Check exclude patterns
        for pattern in self.exclude_files:
            if pattern.startswith('*'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern in file_path:
                return True
        
        # Check special files
        if file_name in self.special_files:
            return True
            
        return False
    
    def migrate_file(self, file_path: str) -> Dict[str, any]:
        """Migrate a single file to CR_ prefix compliance"""
        result = {
            'file_path': file_path,
            'changes_made': 0,
            'patterns_applied': [],
            'success': False,
            'error': None,
            'backup_created': False
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            result['backup_created'] = True
            
            # Apply migration patterns
            modified_content = original_content
            total_changes = 0
            
            for pattern, replacement in self.patterns:
                matches_before = len(re.findall(pattern, modified_content))
                if matches_before > 0:
                    modified_content = re.sub(pattern, replacement, modified_content)
                    matches_after = len(re.findall(pattern, modified_content))
                    changes = matches_before - matches_after
                    total_changes += changes
                    result['patterns_applied'].append({
                        'pattern': pattern,
                        'changes': changes
                    })
            
            result['changes_made'] = total_changes
            
            # Write modified content if not dry run
            if not self.dry_run and total_changes > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
            result['success'] = True
            
            # Log migration
            self.migration_log.append({
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'changes_made': total_changes,
                'dry_run': self.dry_run
            })
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def migrate_directory(self, directory: str, recursive: bool = True) -> List[Dict[str, any]]:
        """Migrate all Python files in directory"""
        results = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self.should_exclude_file(os.path.join(root, d))]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        if not self.should_exclude_file(file_path):
                            result = self.migrate_file(file_path)
                            results.append(result)
        else:
            for file in os.listdir(directory):
                if file.endswith('.py'):
                    file_path = os.path.join(directory, file)
                    if not self.should_exclude_file(file_path):
                        result = self.migrate_file(file_path)
                        results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict[str, any]]) -> str:
        """Generate migration report"""
        total_files = len(results)
        successful_files = sum(1 for r in results if r['success'])
        total_changes = sum(r['changes_made'] for r in results)
        
        report = f"""
# CR_ Prefix Migration Report
Generated: {datetime.now().isoformat()}
Dry Run: {self.dry_run}

## Summary
- Total Files Processed: {total_files}
- Successful Migrations: {successful_files}
- Failed Migrations: {total_files - successful_files}
- Total Changes Made: {total_changes}
- Success Rate: {(successful_files/total_files*100):.1f}%

## File Details
"""
        
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            report += f"\n### {status}: {result['file_path']}\n"
            report += f"- Changes Made: {result['changes_made']}\n"
            
            if result['error']:
                report += f"- Error: {result['error']}\n"
            
            if result['patterns_applied']:
                report += "- Patterns Applied:\n"
                for pattern_info in result['patterns_applied']:
                    report += f"  - {pattern_info['pattern']}: {pattern_info['changes']} changes\n"
        
        return report
    
    def save_report(self, report: str, output_path: str = "migration_report.md"):
        """Save migration report to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Migration report saved to: {output_path}")


def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CR_ Prefix Migration Tool")
    parser.add_argument("path", help="Path to file or directory to migrate")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Perform dry run (default)")
    parser.add_argument("--execute", action="store_true", help="Execute migration (not dry run)")
    parser.add_argument("--report", default="migration_report.md", help="Report output file")
    parser.add_argument("--recursive", action="store_true", default=True, help="Process directories recursively")
    
    args = parser.parse_args()
    
    # Set dry run flag
    dry_run = not args.execute
    
    # Create migrator
    migrator = CRPrefixMigrator(dry_run=dry_run)
    
    # Check if path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        return 1
    
    # Perform migration
    if os.path.isfile(args.path):
        if args.path.endswith('.py'):
            results = [migrator.migrate_file(args.path)]
        else:
            print(f"Error: '{args.path}' is not a Python file")
            return 1
    elif os.path.isdir(args.path):
        results = migrator.migrate_directory(args.path, args.recursive)
    else:
        print(f"Error: '{args.path}' is neither a file nor a directory")
        return 1
    
    # Generate and save report
    report = migrator.generate_report(results)
    migrator.save_report(report, args.report)
    
    # Print summary
    successful_files = sum(1 for r in results if r['success'])
    total_changes = sum(r['changes_made'] for r in results)
    
    print(f"\nMigration {'(DRY RUN) ' if dry_run else ''}Complete!")
    print(f"Files Processed: {len(results)}")
    print(f"Successful: {successful_files}")
    print(f"Total Changes: {total_changes}")
    
    if dry_run:
        print("\nTo execute migration, run with --execute flag")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
