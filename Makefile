test:
	@.venv/bin/python -m pytest tests/ -v

.PHONY: dashboard open clean test

dashboard:
	@python3 generate-dashboard.py

open: dashboard
	@xdg-open Dashboard/index.html 2>/dev/null || open Dashboard/index.html 2>/dev/null || echo "Open Dashboard/index.html in your browser"

clean:
	@rm -rf Dashboard/
