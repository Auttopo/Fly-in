FILE=config.txt
PROGRAM=main
TRACE=.install_trace
ENV=fly_in_env
PYHTON=python3

run : $(TRACE)
	. $(ENV)/bin/activate && \
	python3 -m $(PROGRAM) $(FILE)

install $(TRACE) : pyproject.toml
	python3 -m venv $(ENV) && \
	. $(ENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install uv && \
	uv pip install -r pyproject.toml && \
	touch .install_trace

run-trace : $(TRACE)
	. $(ENV)/bin/activate && \
	python3 -m $(PROGRAM) $(FILE) traceback

debug :
	. $(ENV)/bin/activate && \
	python3 -m pdb $(PROGRAM) $(FILE)

clean:
	. $(ENV)/bin/activate && \
	$(RM) -r __pycache__

fclean:
	. $(ENV)/bin/activate && \
	$(RM) -r __pycache__
	$(RM) .install_trace
	$(RM) -r fly_in_env

#	$(RM) -r .mypy_cache

lint :
	. $(ENV)/bin/activate && \
	python3 -m flake8 --exclude $(ENV),mlx_files; \
	python3 -m mypy . --explicit-package-bases --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict :
	. $(ENV)/bin/activate && \
	python3 -m flake8 --exclude $(ENV),mlx_files; \
	python3 -m mypy . --explicit-package-bases --strict

.PHONY : install run debug clean fclean lint lint-strict
