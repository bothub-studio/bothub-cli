.PHONY: dist

clean:
	rm -rf dist

build: dist
	python setup.py bdist_wheel

register:
	twine register dist/*.whl

upload:
	twine upload dist/*
