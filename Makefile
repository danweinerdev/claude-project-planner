.PHONY: bump-patch bump-minor bump-major

bump-patch:
	$(eval VERSION := $(shell python3 bump-version.py patch))
	@git add . && git commit -m "v$(VERSION)" && git tag -a "v$(VERSION)" -m "v$(VERSION)"
	@echo "Bumped to v$(VERSION)"

bump-minor:
	$(eval VERSION := $(shell python3 bump-version.py minor))
	@git add . && git commit -m "v$(VERSION)" && git tag -a "v$(VERSION)" -m "v$(VERSION)"
	@echo "Bumped to v$(VERSION)"

bump-major:
	$(eval VERSION := $(shell python3 bump-version.py major))
	@git add . && git commit -m "v$(VERSION)" && git tag -a "v$(VERSION)" -m "v$(VERSION)"
	@echo "Bumped to v$(VERSION)"
