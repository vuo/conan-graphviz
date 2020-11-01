from conans import ConanFile, CMake, tools
import os
import platform
import shutil

class GraphvizConan(ConanFile):
    name = 'graphviz'

    source_version = '2.44.1'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
        'vuoutils/1.2@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-graphviz'
    license = 'http://graphviz.org/License.php'
    description = 'A way of representing structural information as diagrams of abstract graphs and networks'
    source_dir = 'graphviz-%s' % source_version
    build_dir = '_build'
    install_dir = '_install'
    libs = {
        'cdt': 5,
        'cgraph': 6,
        'gvc': 6,
        'pathplan': 4,
        'xdot': 4,
    }
    libs_plugins = {
        'gvplugin_dot_layout': 6,
        'gvplugin_core': 6,
    }
    exports_sources = '*.patch'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://gitlab.com/graphviz/graphviz/-/archive/%s/graphviz-%s.tar.bz2' % (self.source_version, self.source_version),
                  sha256='0f8f3fbeaddd474e0a270dc9bb0e247a1ae4284ae35125af4adceffae5c7ae9b')

        # https://b33p.net/kosada/vuo/vuo/-/issues/11703#note_2056328
        tools.patch(patch_file='graphviz-skip-dot-layout.patch', base_path=self.source_dir)

        self.run('cp %s/COPYING %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        import VuoUtils

        cmake = CMake(self)

        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['CMAKE_C_COMPILER']   = '%s/bin/clang'   % self.deps_cpp_info['llvm'].rootpath
        cmake.definitions['CMAKE_C_FLAGS'] = '-Oz -fno-common'
        cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_dir)
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
        cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath
        cmake.definitions['BUILD_SHARED_LIBS'] = 'ON'
        cmake.definitions['BUILD_STATIC_LIBS'] = 'OFF'
        cmake.definitions['CAIRO_INCLUDE_DIR'] = ''
        cmake.definitions['CAIRO_LIBRARY'] = ''
        cmake.definitions['CAIRO_RUNTIME_LIBRARY'] = ''
        cmake.definitions['EXPAT_INCLUDE_DIR'] = ''
        cmake.definitions['EXPAT_LIBRARY'] = ''
        cmake.definitions['EXPAT_RUNTIME_LIBRARY'] = ''
        cmake.definitions['GD_INCLUDE_DIR'] = ''
        cmake.definitions['GD_LIBRARY'] = ''
        cmake.definitions['GD_RUNTIME_LIBRARY'] = ''
        cmake.definitions['GLIB_INCLUDE_DIR'] = ''
        cmake.definitions['GLIB_LIBRARY'] = ''
        cmake.definitions['GLIB_RUNTIME_LIBRARY'] = ''
        cmake.definitions['GOBJECT_LIBRARY'] = ''
        cmake.definitions['GOBJECT_RUNTIME_LIBRARY'] = ''
        cmake.definitions['LTDL_INCLUDE_DIR'] = ''
        cmake.definitions['LTDL_LIBRARY'] = ''
        cmake.definitions['PANGOCAIRO_INCLUDE_DIR'] = ''
        cmake.definitions['PANGOCAIRO_LIBRARY'] = ''
        cmake.definitions['PANGOCAIRO_RUNTIME_LIBRARY'] = ''
        cmake.definitions['PANGO_LIBRARY'] = ''
        cmake.definitions['PANGO_RUNTIME_LIBRARY'] = ''
        cmake.definitions['enable_ltdl'] = 'OFF'
        cmake.definitions['with_digcola'] = 'OFF'
        cmake.definitions['with_ipsepcola'] = 'OFF'
        cmake.definitions['with_ortho'] = 'OFF'
        cmake.definitions['with_sfdp'] = 'OFF'
        cmake.definitions['with_smyrna'] = 'OFF'

        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()
            cmake.install()

        with tools.chdir(self.install_dir):
            with tools.chdir('lib'):
                with tools.chdir('graphviz'):
                    for f in self.libs_plugins.keys():
                        shutil.copy('lib%s.dylib' % f, '..')
                l = self.libs_plugins.copy()
                l.update(self.libs)
                VuoUtils.fixLibs(l, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/include' % self.install_dir, dst='include')
        for f in list(self.libs.keys()) + list(self.libs_plugins.keys()):
            self.copy('lib%s.%s' % (f, libext), src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = list(self.libs.keys()) + list(self.libs_plugins.keys())
