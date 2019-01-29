

import os
import sys
import platform

from pkg_resources import get_distribution

SCRIPT_NAME = 'pysamloader'
SCRIPT_VERSION = get_distribution(SCRIPT_NAME).version

if platform.system() == 'Linux':
    import tarfile
    package_ext = '.tar.gz'
    executable_ext = ''
elif platform.system() == 'Windows':
    import zipfile
    package_ext = '.zip'
    executable_ext = '.exe'
else:
    raise NotImplementedError("Platform not supported : {0}"
                              "".format(platform.system()))


def _get_python_shared_lib():
    real_exec = sys.executable
    while os.path.islink(real_exec):
        real_exec = os.readlink(real_exec)
    return os.path.normpath(
        os.path.join(os.path.split(real_exec)[0], os.pardir, 'lib')
    )


def _base_folder():
    return os.path.join(os.path.split(__file__)[0])


def _dist_folder():
    target = 'binary-{0}'.format(platform.system().lower())
    return os.path.join(_base_folder(), 'dist', target)


def _executable_name():
    return SCRIPT_NAME + executable_ext


def _executable_path():
    return os.path.join(_dist_folder(), _executable_name())


def task_build():
    if platform.system() == 'Linux':
        prefix = "LD_LIBRARY_PATH={0} ".format(_get_python_shared_lib())
    else:
        prefix = ""
    return {
        'actions': [prefix + 'pyinstaller pysamloader.spec'],
        'targets': [_executable_path()]
    }


def _package_name():
    return "{0}-{1}-{2}-{3}{4}".format(
        SCRIPT_NAME, SCRIPT_VERSION,
        platform.system().lower(), platform.machine(), package_ext
    )


def _package_path():
    return os.path.join(_dist_folder(), _package_name())


def _create_package():
    package_content = [
        (os.path.join(_dist_folder(), _executable_name()), _executable_name()),
        (os.path.join(_base_folder(), 'LICENSE'), 'LICENSE'),
        (os.path.join(_base_folder(), 'README.rst'), 'README.rst'),
        (os.path.join(_base_folder(), 'pysamloader', 'devices'), 'devices'),
    ]

    def _filter_py(tarinfo):
        if os.path.splitext(tarinfo.name)[1] == '.pyc':
            return None
        if tarinfo.isdir() and tarinfo.name.endswith('__pycache__'):
            return None
        return tarinfo

    if platform.system() == 'Linux':
        with tarfile.open(_package_path(), "w:gz") as tar:
            for item, arc in package_content:
                tar.add(item, arcname=arc, filter=_filter_py)
    elif platform.system() == 'Windows':
        pass


def task_package():
    return {
        'task_dep': ['build'],
        'actions': [_create_package],
        'targets': [_package_path()]
    }