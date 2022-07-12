from distutils.core import setup

setup(
    entry_points={"console_scripts": ["app-cli=app.cli:main"]},
)
