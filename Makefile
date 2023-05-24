VENV_DIR := venv

ifeq ($(PYTHON),)
	ifeq ($(OS), Windows_NT)
		PYTHON := python
	else
		PYTHON := python3
	endif
endif
ifeq ($(PYTHONV),)
	ifeq ($(OS), Windows_NT)
		PYTHONV := $(VENV_DIR)/Scripts/python.exe
	else
		PYTHONV := $(VENV_DIR)/bin/python
	endif
endif


setup:
	$(PYTHON) -m venv $(VENV_DIR)
	$(PYTHONV) -m pip install --upgrade pip
	$(PYTHONV) -m pip install '.[dev,test]'

clean:
	rm -rf build
	rm -rf dist
	rm -rf src/*.egg
	rm -rf src/*.egg-info

style:
	$(PYTHONV) -m black src

install: clean
	$(PYTHONV) -m pip install .

build: clean style
	$(PYTHONV) -m build .

upload: build
	$(PYTHONV) -m twine upload dist/*
