import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pipettewrapper",
    version="0.1",
    author="Liam Hawkins",
    author_email="liam.hawkins@carleton.ca",
    description="Wrapper to allow Opentrons multichannel pipettes to use any number of tips",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liamhawkins/PipetteWrapper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
)