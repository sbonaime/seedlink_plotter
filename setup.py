from setuptools import setup

INSTALL_REQUIRES = [
    'numpy',
    'scipy',
    'matplotlib>=1.3.0',
    'obspy>=0.9.0']

setup(
    name="seedlink-plotter",
    version="0.1.0",
    description="Plot data acquired in realtime in from a seedlink server.",
    author="Sebastien Bonaime, Lion Krischer, Tobias Megies",
    author_email="bonaime@ipgp.fr",
    url="https://github.com/bonaime/seedlink_plotter",
    download_url="https://github.com/bonaime/seedlink_plotter.git",
    install_requires=INSTALL_REQUIRES,
    keywords=["Seedlink", "ObsPy", "Seismology", "Plotting", "Realtime"],
    packages=["seedlink_plotter"],
    package_data={'seedlink_plotter': ['favicon.gif']},
    entry_points={
        'console_scripts':
            ['seedlink-plotter = seedlink_plotter.seedlink_plotter:main'],
    },
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or " +
        "Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description="""\
Seedlink-plotter is a tool to plot seismological waveform data acquired from a
Seedlink server. The plots are continuously updated as recent data is acquired
in realtime.
"""
)
