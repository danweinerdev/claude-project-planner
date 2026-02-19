test:
	@python -m pytest tests/ -v

.PHONY: dashboard open clean test bump-patch bump-minor bump-major

dashboard:
	@python3 generate-dashboard.py

open: dashboard
	@xdg-open Dashboard/index.html 2>/dev/null || open Dashboard/index.html 2>/dev/null || echo "Open Dashboard/index.html in your browser"

clean:
	@rm -rf Dashboard/

bump-patch:
	$(eval VERSION := $(shell python3 bump-version.py patch))
	@git add ../. && git commit -m "v$(VERSION)" && git tag "v$(VERSION)"
	@echo "Bumped to v$(VERSION)"

bump-minor:
	$(eval VERSION := $(shell python3 bump-version.py minor))
	@git add ../. && git commit -m "v$(VERSION)" && git tag "v$(VERSION)"
	@echo "Bumped to v$(VERSION)"

bump-major:
	$(eval VERSION := $(shell python3 bump-version.py major))
	@git add ../. && git commit -m "v$(VERSION)" && git tag "v$(VERSION)"
	@echo "Bumped to v$(VERSION)"
