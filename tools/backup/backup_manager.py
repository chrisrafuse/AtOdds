#!/usr/bin/env python3
"""
Backup Manager Tool
Automated backup and rollback procedures for CR_ migration
"""

import os
import sys
import json
import shutil
import tarfile
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

class BackupManager:
    """Automated backup and rollback manager"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.backup_log = []
        
        # Backup configuration
        self.max_backups = 10  # Keep last 10 backups
        self.compression = True  # Use compression
        self.include_git = True  # Include .git directory
        
        # File patterns to exclude from backups
        self.exclude_patterns = {
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '.DS_Store',
            'Thumbs.db',
            'node_modules',
            '.venv',
            'venv',
            'env',
            'dist',
            'build',
            '*.egg-info'
        }
    
    def create_backup(self, source_path: str, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create backup of source path"""
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        result = {
            'backup_name': backup_name,
            'source_path': source_path,
            'backup_path': '',
            'success': False,
            'error': None,
            'file_count': 0,
            'size_bytes': 0,
            'duration_seconds': 0,
            'created_at': datetime.now().isoformat()
        }
        
        start_time = datetime.now()
        
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source path '{source_path}' does not exist")
            
            # Create backup directory
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            result['backup_path'] = str(backup_path)
            
            # Create backup archive
            if self.compression:
                archive_path = backup_path / f"{backup_name}.tar.gz"
                result['backup_path'] = str(archive_path)
                
                with tarfile.open(archive_path, 'w:gz') as tar:
                    self._add_to_tar(tar, source_path, Path(source_path.name))
            else:
                # Simple directory copy
                backup_copy_path = backup_path / source_path.name
                shutil.copytree(source_path, backup_copy_path, ignore=self._ignore_patterns)
                result['backup_path'] = str(backup_copy_path)
            
            # Calculate backup stats
            if self.compression:
                result['size_bytes'] = archive_path.stat().st_size
            else:
                result['size_bytes'] = sum(
                    f.stat().st_size for f in backup_copy_path.rglob('*') if f.is_file()
                )
            
            result['file_count'] = len(list(backup_path.rglob('*'))) if not self.compression else 1
            result['success'] = True
            
            # Log backup
            self.backup_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'create_backup',
                'backup_name': backup_name,
                'source_path': str(source_path),
                'success': True
            })
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            
            # Log failure
            self.backup_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'create_backup',
                'backup_name': backup_name,
                'source_path': str(source_path),
                'success': False,
                'error': str(e)
            })
        
        finally:
            result['duration_seconds'] = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def restore_backup(self, backup_name: str, target_path: str) -> Dict[str, Any]:
        """Restore backup to target path"""
        result = {
            'backup_name': backup_name,
            'target_path': target_path,
            'success': False,
            'error': None,
            'files_restored': 0,
            'duration_seconds': 0,
            'restored_at': datetime.now().isoformat()
        }
        
        start_time = datetime.now()
        
        try:
            backup_path = self.backup_dir / backup_name
            target_path = Path(target_path)
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup '{backup_name}' not found")
            
            # Create target directory if it doesn't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Find backup archive or directory
            archive_path = backup_path / f"{backup_name}.tar.gz"
            backup_dir_path = backup_path / backup_name
            
            if archive_path.exists():
                # Restore from compressed archive
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(target_path.parent)
                    result['files_restored'] = len(tar.getnames())
            elif backup_dir_path.exists():
                # Restore from directory copy
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.copytree(backup_dir_path, target_path)
                result['files_restored'] = len(list(target_path.rglob('*')))
            else:
                raise FileNotFoundError(f"No valid backup found for '{backup_name}'")
            
            result['success'] = True
            
            # Log restore
            self.backup_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'restore_backup',
                'backup_name': backup_name,
                'target_path': str(target_path),
                'success': True
            })
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            
            # Log failure
            self.backup_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'restore_backup',
                'backup_name': backup_name,
                'target_path': str(target_path),
                'success': False,
                'error': str(e)
            })
        
        finally:
            result['duration_seconds'] = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                backup_info = {
                    'backup_name': backup_dir.name,
                    'backup_path': str(backup_dir),
                    'created_at': None,
                    'size_bytes': 0,
                    'type': 'directory'
                }
                
                # Check if it's a compressed archive
                archive_path = backup_dir / f"{backup_dir.name}.tar.gz"
                if archive_path.exists():
                    backup_info['type'] = 'compressed'
                    backup_info['size_bytes'] = archive_path.stat().st_size
                    backup_info['backup_path'] = str(archive_path)
                
                # Get creation time
                try:
                    if backup_info['type'] == 'compressed':
                        backup_info['created_at'] = datetime.fromtimestamp(
                            archive_path.stat().st_ctime
                        ).isoformat()
                    else:
                        backup_info['created_at'] = datetime.fromtimestamp(
                            backup_dir.stat().st_ctime
                        ).isoformat()
                except:
                    pass
                
                backups.append(backup_info)
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups
    
    def delete_backup(self, backup_name: str) -> Dict[str, Any]:
        """Delete a backup"""
        result = {
            'backup_name': backup_name,
            'success': False,
            'error': None,
            'deleted_at': datetime.now().isoformat()
        }
        
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup '{backup_name}' not found")
            
            # Remove backup directory
            shutil.rmtree(backup_path)
            result['success'] = True
            
            # Log deletion
            self.backup_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'delete_backup',
                'backup_name': backup_name,
                'success': True
            })
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            
            # Log failure
            self.backup_log.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'delete_backup',
                'backup_name': backup_name,
                'success': False,
                'error': str(e)
            })
        
        return result
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """Clean up old backups, keeping only the most recent ones"""
        result = {
            'backups_before': 0,
            'backups_after': 0,
            'backups_deleted': 0,
            'deleted_backups': [],
            'success': False,
            'error': None,
            'cleaned_at': datetime.now().isoformat()
        }
        
        try:
            backups = self.list_backups()
            result['backups_before'] = len(backups)
            
            if len(backups) > self.max_backups:
                # Delete oldest backups
                backups_to_delete = backups[self.max_backups:]
                
                for backup in backups_to_delete:
                    delete_result = self.delete_backup(backup['backup_name'])
                    if delete_result['success']:
                        result['deleted_backups'].append(backup['backup_name'])
                
                result['backups_deleted'] = len(result['deleted_backups'])
            
            result['backups_after'] = len(self.list_backups())
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def _add_to_tar(self, tar: tarfile.TarFile, source: Path, arcname: Path):
        """Add files to tar archive, excluding patterns"""
        if source.is_file():
            # Check if file should be excluded
            if any(source.match(pattern) for pattern in self.exclude_patterns):
                return
            
            tar.add(source, arcname)
        elif source.is_dir():
            # Recursively add directory contents
            for item in source.iterdir():
                self._add_to_tar(tar, item, arcname / item.name)
    
    def _ignore_patterns(self, path: str, names: List[str]) -> List[str]:
        """Ignore patterns for shutil.copytree"""
        ignored = []
        
        for name in names:
            for pattern in self.exclude_patterns:
                if name.startswith('.') or name.endswith(pattern.replace('*', '')):
                    ignored.append(name)
                    break
        
        return ignored
    
    def save_backup_log(self, log_path: str = "backup_log.json"):
        """Save backup log to file"""
        log_file = self.backup_dir / log_path
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_log, f, indent=2, ensure_ascii=False)
            print(f"Backup log saved to: {log_file}")
        except Exception as e:
            print(f"Error saving backup log: {e}")
    
    def load_backup_log(self, log_path: str = "backup_log.json"):
        """Load backup log from file"""
        log_file = self.backup_dir / log_path
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                self.backup_log = json.load(f)
            print(f"Backup log loaded from: {log_file}")
        except FileNotFoundError:
            print(f"Backup log file not found: {log_file}")
        except Exception as e:
            print(f"Error loading backup log: {e}")


def main():
    """Main backup manager function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup Manager Tool")
    parser.add_argument("action", choices=['create', 'restore', 'list', 'delete', 'cleanup'], help="Action to perform")
    parser.add_argument("--source", help="Source path for backup")
    parser.add_argument("--target", help="Target path for restore")
    parser.add_argument("--backup-name", help="Backup name")
    parser.add_argument("--backup-dir", default="backups", help="Backup directory")
    parser.add_argument("--max-backups", type=int, default=10, help="Maximum backups to keep")
    
    args = parser.parse_args()
    
    # Create backup manager
    manager = BackupManager(args.backup_dir)
    manager.max_backups = args.max_backups
    
    # Load existing log
    manager.load_backup_log()
    
    if args.action == 'create':
        if not args.source:
            print("Error: --source is required for create action")
            return 1
        
        result = manager.create_backup(args.source, args.backup_name)
        
        if result['success']:
            print(f"✅ Backup created successfully!")
            print(f"Backup: {result['backup_name']}")
            print(f"Path: {result['backup_path']}")
            print(f"Size: {result['size_bytes']} bytes")
            print(f"Duration: {result['duration_seconds']:.2f} seconds")
        else:
            print(f"❌ Backup creation failed: {result['error']}")
            return 1
    
    elif args.action == 'restore':
        if not args.backup_name:
            print("Error: --backup-name is required for restore action")
            return 1
        if not args.target:
            print("Error: --target is required for restore action")
            return 1
        
        result = manager.restore_backup(args.backup_name, args.target)
        
        if result['success']:
            print(f"✅ Backup restored successfully!")
            print(f"Backup: {result['backup_name']}")
            print(f"Target: {result['target_path']}")
            print(f"Files restored: {result['files_restored']}")
            print(f"Duration: {result['duration_seconds']:.2f} seconds")
        else:
            print(f"❌ Backup restoration failed: {result['error']}")
            return 1
    
    elif args.action == 'list':
        backups = manager.list_backups()
        
        if backups:
            print(f"Available backups ({len(backups)}):")
            for backup in backups:
                print(f"  📦 {backup['backup_name']}")
                print(f"     Type: {backup['type']}")
                print(f"     Size: {backup['size_bytes']} bytes")
                print(f"     Created: {backup['created_at']}")
                print()
        else:
            print("No backups found")
    
    elif args.action == 'delete':
        if not args.backup_name:
            print("Error: --backup-name is required for delete action")
            return 1
        
        result = manager.delete_backup(args.backup_name)
        
        if result['success']:
            print(f"✅ Backup deleted successfully: {args.backup_name}")
        else:
            print(f"❌ Backup deletion failed: {result['error']}")
            return 1
    
    elif args.action == 'cleanup':
        result = manager.cleanup_old_backups()
        
        if result['success']:
            print(f"✅ Cleanup completed successfully!")
            print(f"Backups before: {result['backups_before']}")
            print(f"Backups after: {result['backups_after']}")
            print(f"Backups deleted: {result['backups_deleted']}")
            
            if result['deleted_backups']:
                print("Deleted backups:")
                for backup_name in result['deleted_backups']:
                    print(f"  - {backup_name}")
        else:
            print(f"❌ Cleanup failed: {result['error']}")
            return 1
    
    # Save backup log
    manager.save_backup_log()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
