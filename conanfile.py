from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from sys import platform
import re
import os


class DarknetConan(ConanFile):
    name = "darknet"
    version = "git61c9d02"
    license = "MIT"
    url = "https://github.com/pjreddie/darknet"
    description = "Darknet is an open source neural network framework written in C and CUDA. It is fast, easy to install, and supports CPU and GPU computation."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "gpu": [True, False],
               "opencv": [True, False],
               "cudnn": [True, False],
               "openmp": [True, False]}
    default_options = {"shared": False,
                       "gpu": False,
                       "opencv": False,
                       "cudnn": False,
                       "openmp": False}
    generators = "make"

    def requirements(self):
        if self.options.opencv:
            self.requires("opencv/4.1.1@conan/stable")

    def source(self):
        git = tools.Git()
        git.clone("https://github.com/pjreddie/darknet.git")
        version = git.run('rev-parse --short HEAD')
        self.version = "git%s" % version

    def system_requirements(self):
        if self.settings.os == 'Linux' and tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                arch_suffix = ''
                if self.settings.arch == 'x86':
                    arch_suffix = ':i386'
                elif self.settings.arch == 'x86_64':
                    arch_suffix = ':amd64'
                packages = []
                if self.options.openmp:
                    packages.append('libomp-dev%s' % arch_suffix)
                for package in packages:
                    installer.install(package)
            elif tools.os_info.with_yum:
                installer = tools.SystemPackageTool()
                arch_suffix = ''
                if self.settings.arch == 'x86':
                    arch_suffix = '.i686'
                elif self.settings.arch == 'x86_64':
                    arch_suffix = '.x86_64'
                packages = []
                if self.options.openmp:
                    packages.append('libomp-devel%s' % arch_suffix)
                for package in packages:
                    installer.install(package)

    def build(self):
        tools.replace_in_file('Makefile', "GPU=0",
                              "GPU=%d" % int(self.options.gpu == 'True'))
        tools.replace_in_file('Makefile', "OPENCV=0",
                              "OPENCV=%d" % int(self.options.opencv == 'True'))
        tools.replace_in_file('Makefile', "CUDNN=0",
                              "CUDNN=%d" % int(self.options.cudnn == 'True'))
        tools.replace_in_file('Makefile', "OPENMP=0",
                              "OPENMP=%d" % int(self.options.openmp == 'True'))
        env_build = AutoToolsBuildEnvironment(self)
        env_build.make()

    def package(self):
        self.copy("darknet", dst=".", keep_path=False)
        self.copy("*.h", dst="include", src="include")
        self.copy("*.h", dst="include", src="src")
        self.copy("*.so", keep_path=True)
        self.copy("*.o", dst="obj", src="obj")
        self.copy("*.a", keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["darknet"]
