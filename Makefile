.PHONY: help pre-bootstrap-audit audit clean

help:
	@echo "Available targets:"
	@echo "  make pre-bootstrap-audit  Run mandatory pre-bootstrap alignment audit"
	@echo "  make audit                Alias for pre-bootstrap-audit"
	@echo "  make clean                Remove generated artifacts, logs, and caches"

pre-bootstrap-audit:
	@./scripts/pre_bootstrap_audit.sh

audit: pre-bootstrap-audit

clean:
	@rm -rf generated_blueprints __pycache__ python3/__pycache__
	@rm -f audit.log audit_full.log blueprint_inputs_*.json blueprint_inputs_*.md blue_print_used_on_creation_blueprint_inputs_*.md
	@mkdir -p generated_blueprints
	@echo "Repository cleaned (generated artifacts removed)."
