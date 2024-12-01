.PHONY: env
env:
	test -f "env/bin/activate" || python3 -m venv env
	echo "Activate with 'source env/bin/activate'"

.PHONY: install
install:
	python3 -m pip install --upgrade pip
	python3 -m pip install pytest
	python3 -m pip install .

.PHONY: clean
clean:
	rm -rf env dist build *.egg-info ./Python/bin/data

.PHONY: test
test:
	pushd new_tests && pytest
