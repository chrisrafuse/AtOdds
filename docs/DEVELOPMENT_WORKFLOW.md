# Development Workflow

## Branch Structure
- `feature/cr-migration-phase-0`: Current Phase 0 work
- `feature/data-structure-alignment`: Phase 1 work
- `feature/cr-signature-migration`: Phase 2 work
- `feature/system-enhancements`: Phase 3 work

## Development Process
1. Always work on feature branches
2. Create backup before major changes
3. Run validation tools before committing
4. Use pre-commit hooks for code quality

## Migration Tools
- CR Prefix Migration: `tools/migration/cr_prefix_migrator.py`
- Data Structure Transformation: `tools/migration/data_structure_transformer.py`
- Compliance Validation: `tools/validation/cr_compliance_validator.py`
- Backup Management: `tools/backup/backup_manager.py`

## Testing
- Run tests: `python -m pytest tests/ -v`
- Run coverage: `python -m pytest --cov=packages tests/`
- Run validation: `python scripts/validate_betstamp_alignment.py`

## Code Quality
- Format code: `black packages/ apps/ tests/`
- Lint code: `flake8 packages/ apps/ tests/`
- Type checking: `mypy packages/ apps/`
