# Skime

Skime is a small Scheme implementation written in Python. It provides a bytecode compiler, a virtual machine, a REPL, hygienic `syntax-rules` macros, continuations, and a growing subset of R5RS syntax and procedures.

## Installation

Skime is published on [PyPI](https://pypi.org/project/skime/):

```sh
pip install skime
```

Start the REPL with:

```sh
skime
```

It can also be embedded in Python:

```python
from skime.vm import VM

vm = VM()
assert vm.eval_string("(+ 1 2 3)") == 6
```

## Project history

This repository is derived from [pluskid/skime](https://github.com/pluskid/skime), the original Skime project. The codebase was migrated to Python 3, existing bugs were fixed, and previously unsupported features were added, including more R5RS syntax, list procedures, characters, strings, vectors, numeric procedures, and output procedures.

Skime remains a compact educational implementation rather than a complete R5RS implementation.

## License and original public-domain dedication

The original author released the original project into the public domain with the following statement:

> I put this project into public domain. Anyone is free to make whatever use of the code in this repo.

That public-domain dedication continues to apply to the original work. This maintained version, including the Python 3 migration and subsequent changes, is redistributed under the [MIT License](LICENSE).
