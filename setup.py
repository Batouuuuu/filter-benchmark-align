from setuptools import setup, find_packages

setup(
    name="filter-benchmark-align",
    version="0.1",
    packages=find_packages(),  ## this will find my __init__.py
    install_requires=[
        "fastapi",
        "pandas",
        "scikit-learn",
        "pyyaml",
        "python-multipart",
        "opusfilter",
        "tabulate"
    ],
    entry_points={
        "console_scripts": [

        ]
    },
    python_requires='>=3.9',
)
