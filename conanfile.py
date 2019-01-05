from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform
import shutil

class GraphvizConan(ConanFile):
    name = 'graphviz'

    source_version = '2.28.0'
    package_version = '5'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable', \
        'vuoutils/1.0@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-graphviz'
    license = 'http://graphviz.org/License.php'
    description = 'A way of representing structural information as diagrams of abstract graphs and networks'
    source_dir = 'graphviz-%s' % source_version
    build_dir = '_build'
    libs = {
        'cdt': 5,
        'gvc': 6,
        'pathplan': 4,
        'graph': 5,
        'xdot': 4,
    }
    libs_plugins = {
        'gvplugin_dot_layout': 1,
        'gvplugin_core': 1,
    }
    exports_sources = '*.patch'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://pkgs.fedoraproject.org/repo/pkgs/graphviz/graphviz-2.28.0.tar.gz/8d26c1171f30ca3b1dc1b429f7937e58/graphviz-2.28.0.tar.gz',
                  sha256='d3aa7973c578cae4cc26d9d6498c57ed06680cab9a4e940d0357a3c6527afc76')

        tools.patch(patch_file='graphviz-skip-dot-layout.patch', base_path=self.source_dir)

        self.run('cp %s/COPYING %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        import VuoUtils
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = ['c++abi']

            autotools.flags.append('-Oz')
            if platform.system() == 'Darwin':
                autotools.flags.append('-mmacosx-version-min=10.10')
                autotools.flags.append('-mno-avx')
                autotools.flags.append('-mno-sse4')
                autotools.flags.append('-mno-sse4.1')
                autotools.flags.append('-mno-sse4.2')

            autotools.link_flags.append('-Wl,-headerpad_max_install_names')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=['--quiet',
                                          '--disable-debug',
                                          '--disable-dependency-tracking',
                                          '--disable-guile',
                                          '--disable-java',
                                          '--disable-ltdl',
                                          '--disable-lua',
                                          '--disable-ocaml',
                                          '--disable-perl',
                                          '--disable-php',
                                          '--disable-python',
                                          '--disable-r',
                                          '--disable-ruby',
                                          '--disable-sharp',
                                          '--disable-static',
                                          '--disable-swig',
                                          '--disable-swig',
                                          '--disable-tcl',
                                          '--enable-shared',
                                          '--with-qt=no',
                                          '--with-quartz',
                                          '--without-digcola',
                                          '--without-expat',
                                          '--without-fontconfig',
                                          '--without-freetype2',
                                          '--without-gdk-pixbuf',
                                          '--without-jpeg',
                                          '--without-ortho',
                                          '--without-pangocairo',
                                          '--without-png',
                                          '--without-quartz',
                                          '--without-sfdp',
                                          '--without-x',
                                          '--prefix=%s' % os.getcwd()])
                autotools.make(args=['--quiet'])

                with tools.chdir('lib'):
                    autotools.make(args=['--quiet', 'install'])
                    if platform.system() == 'Darwin':
                        shutil.move('libcdt.5.dylib', 'libcdt.dylib')
                        shutil.move('libgvc.6.dylib', 'libgvc.dylib')
                        shutil.move('libpathplan.4.dylib', 'libpathplan.dylib')
                        shutil.move('libgraph.5.dylib', 'libgraph.dylib')
                        shutil.move('libxdot.4.dylib', 'libxdot.dylib')
                    VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

                with tools.chdir('plugin'):
                    autotools.make(args=['--quiet', 'install'])

                with tools.chdir('lib'):
                    if platform.system() == 'Darwin':
                        shutil.move('graphviz/libgvplugin_dot_layout.6.dylib', 'libgvplugin_dot_layout.dylib')
                        shutil.move('graphviz/libgvplugin_core.6.dylib', 'libgvplugin_core.dylib')
                    elif platform.system() == 'Linux':
                        shutil.move('graphviz/libgvplugin_dot_layout.so.6.0.0', 'libgvplugin_dot_layout.so')
                        shutil.move('graphviz/libgvplugin_core.so.6.0.0', 'libgvplugin_core.so')
                    else:
                        raise Exception('Unknown platform "%s"' % platform.system())

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

        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        for f in list(self.libs.keys()) + list(self.libs_plugins.keys()):
            self.copy('lib%s.%s' % (f, libext), src='%s/lib' % self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = list(self.libs.keys()) + list(self.libs_plugins.keys())
