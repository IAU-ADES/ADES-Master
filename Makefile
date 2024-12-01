.PHONY: env
env:
	test -f "env/bin/activate" || python3 -m venv env && env/bin/python -m pip install --upgrade pip && env/bin/python -m pip install -r Python/test-requirements.txt
	echo "Activate with 'source env/bin/activate'"

.PHONY: dist
dist:
	python -m build

.PHONY: install
install: 
	python3 -m pip install .

.PHONY: install-dev
install-dev:
	python3 -m pip install -e .

.PHONY: install-tar
install-tar: dist
	python3 -m pip install dist/*.tar.gz

.PHONY: install-wheel
install-wheel: dist
	python3 -m pip install dist/*.whl

.PHONY: clean
clean:
	rm -rf env dist build *.egg-info 

.PHONY: test
test: 
	pushd new_tests && pytest
