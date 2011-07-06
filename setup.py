#!/usr/bin/env python

#############################################################################
##  this file is part of sate.
##  see "license.txt" for terms and conditions of usage.
#############################################################################


"""
Package setup and installation.
"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

from datetime import datetime
import os
import platform
import subprocess
import sys
import sate

script_name = 'run_sate.py'
gui_script_name = 'run_sate_gui.py'

def compose_build_distribution_name(build_type):
    return "sate%s-v%s-%s" % (build_type, sate.PROGRAM_VERSION, datetime.now().strftime("%Y%b%d"))

param = {
    'name': sate.PROGRAM_NAME,
    'version': sate.PROGRAM_VERSION,
    'description': sate.PROGRAM_DESCRIPTION,
    'author': sate.PROGRAM_AUTHOR,
    'author_email': ['sate-user@googlegroups.com'],
    'url': sate.PROGRAM_WEBSITE,
    'license': sate.PROGRAM_LICENSE,
    'packages': find_packages(),
    'package_dir': {'sate': 'sate'},
    'test_suite': "sate.test",
    'include_package_data': True,
    'install_requires': ['dendropy>=3.2.0'],
    'zip_safe': True,
    'keywords': 'Phylogenetics Evolution Biology',
    'long_description': """A Python implementation of the Simultaneous Alignment and Tree estimation algorithm of Liu, et al. 2009. The package requires configuration to refer to third-party tools such as ClustalW2, MAFFT, MUSCLE, OPAL, Prank, and RAxML""",
    'classifiers': ["Environment :: Console",
                    "Intended Audience :: Developers",
                    "Intended Audience :: Science/Research",
                    "License :: OSI Approved :: GNU General Public License (GPL)",
                    "Natural Language :: English",
                    "Operating System :: OS Independent",
                    "Programming Language :: Python",
                    "Topic :: Scientific/Engineering :: Bio-Informatics",
                    ],
    }

if sys.argv[1] == 'py2exe':
    PY2EXE_DIST_DIR = compose_build_distribution_name("win")
    if not platform.system() == 'Windows':
        raise ValueError('py2exe option only works on MS Windows.\n')
        from distutils.core import setup
    import glob
    import py2exe

    def find_data_files(source,target,patterns):
        if glob.has_magic(source) or glob.has_magic(target):
            raise ValueError("Magic not allowed in src, target")
        ret = {}
        for pattern in patterns:
            pattern = os.path.join(source,pattern)
            for filename in glob.glob(pattern):
                if os.path.isfile(filename):
                    targetpath = os.path.join(target,os.path.relpath(filename,source))
                    path = os.path.dirname(targetpath)
                    ret.setdefault(path,[]).append(filename)
        return sorted(ret.items())

    bin_win_src = sate.sate_tools_dev_dir()
    bin_win_dest = sate.sate_tools_deploy_subpath()
    my_files = []
    my_files.extend( find_data_files(
        bin_win_src,
        bin_win_dest,
        ['*'] ) )
    my_files.extend( find_data_files(
        os.path.join(bin_win_src, 'real_bin'),
        os.path.join(bin_win_dest, 'real_bin'),
        ['*'] ) )

    PY2EXE_OPTIONS = {
        "unbuffered": True,
        "optimize": 2,
        "compressed": True,
        "bundle_files": 1,
        "includes": ['satelib'],
        "dll_excludes": ['w9xpopen.exe'],
        "dist_dir" : PY2EXE_DIST_DIR,
    }

    param.update({
        'console': [script_name, os.path.join(sate.SATE_SCRIPT_RESOURCES, "mafft")],
        'windows': [
                    {   "script": gui_script_name,
                        "icon_resources": [(0, os.path.join(sate.SATE_GUI_RESOURCES, 'sate.ico'))],
                    } ],
        'data_files': my_files,
        'zipfile': None,
        'options': {'py2exe': PY2EXE_OPTIONS},
        }
    )

setup(**param)

### hack upon hack upon hack ...
if sys.argv[1] == 'py2exe':
    sys.stderr.write("\nMoving 'mafft.exe' into bundled binary directory ... \n")
    src_path = os.path.join(PY2EXE_DIST_DIR, "mafft.exe")
    dest_path = os.path.join(PY2EXE_DIST_DIR,
            bin_win_dest,
            "mafft.exe")
    os.rename(src_path, dest_path)
    sys.stderr.write("OK\n")

# On Linux and OS X systems, move mafft script to deployment directory
# so sate can be run from the command-line
#if sys.argv[1] == "develop" or platform.system() != "Windows":
if platform.system() != "Windows":

    src_path = os.path.abspath(os.path.join(sate.SATE_SCRIPT_RESOURCES, "mafft"))
    dest_dir = sate.sate_tools_deploy_dir()
    dest_path = os.path.join(dest_dir, "mafft")

    #if platform.system() == "Windows":
    #    pass
    #    #sys.stderr.write("\nCopying 'mafft' script: '%s' => '%s'\n" % (src_path, dest_path))
    #    #if os.path.exists(dest_path):
    #    #    os.remove(dest_path)
    #    #import shutil
    #    #shutil.copy(src_path, dest_path)
    #else:
    sys.stderr.write("\nCreating link to 'mafft' script: '%s' => '%s'\n" % (src_path, dest_path))
    if os.path.exists(dest_path) and os.path.islink(dest_path):
        real_dest = os.path.abspath(os.path.realpath(dest_path))
        if real_dest != os.path.abspath(os.path.realpath(src_path)):
            msg = "Symbolic link '%s' already exists, but points to different source: '%s'\n" % (dest_path, real_path)
            sys.exit(msg)
        else:
            sys.stderr.write("Path already exists and is linked correctly.\n")
    elif os.path.exists(dest_path):
        msg = "Path to deployed mafft already exists: '%s'\n" % dest_path
        sys.exit(msg)
    else:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        os.symlink(src_path, dest_path)



