.PHONY: clean
clean:
	@find * -name "*.egg-info"      | xargs rm -rf
	@find * -name "__pycache__"     | xargs rm -rf
	@find * -name ".tox"            | xargs rm -rf
	@find * -name ".bash_history"   | xargs rm -rf
	@find * -name ".cache"          | xargs rm -rf
	@find * -name ".coverage"       | xargs rm -rf
	@find * -name ".python_history" | xargs rm -rf
	@find * -name "build"           | xargs rm -rf
	@find * -name "dist"            | xargs rm -rf
	@find * -name "*.retry"         | xargs rm -rf
