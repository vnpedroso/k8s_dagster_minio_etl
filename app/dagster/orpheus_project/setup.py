from setuptools import find_packages, setup

setup(
    name="orpheus_project",
    packages=find_packages(exclude=["orpheus_project_tests"]),
    install_requires=[
        "dagster",
        "spotipy",
        "pandas"
    ],
    extras_require={"dev": ["dagit", "pytest"]},
)
