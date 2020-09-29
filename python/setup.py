from setuptools import setup, find_namespace_packages

settings = {
    'name': 'CSV-Backend',
    'version_config': {
        'version_style': {
            'metadata': True,
            'dirty': True,
        }
    },
    'setup_requires': ['setuptools-vcs-version'],
    'packages': find_namespace_packages(),
    'install_requires': [
        'aiohttp==3.6.2',
        'configargparse'
    ]
}

setup(**settings)
