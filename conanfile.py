from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform
import shutil

class GraphvizConan(ConanFile):
    name = 'graphviz'

    source_version = '2.28.0'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-graphviz'
    license = 'http://graphviz.org/License.php'
    description = 'A way of representing structural information as diagrams of abstract graphs and networks'
    source_dir = 'graphviz-%s' % source_version
    build_dir = '_build'
    libs = ['cdt', 'gvc', 'pathplan', 'graph', 'xdot']
    libs_plugins = ['gvplugin_dot_layout', 'gvplugin_core']

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.9@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://pkgs.fedoraproject.org/repo/pkgs/graphviz/graphviz-2.28.0.tar.gz/8d26c1171f30ca3b1dc1b429f7937e58/graphviz-2.28.0.tar.gz',
                  sha256='d3aa7973c578cae4cc26d9d6498c57ed06680cab9a4e940d0357a3c6527afc76')

        tools.download('https://b33p.net/sites/default/files/graphviz-skip-dot-layout.patch', 'graphviz-skip-dot-layout.patch')
        tools.check_sha256('graphviz-skip-dot-layout.patch', 'c6a7022521c5559ba56f92845c2f1b4b87f541b87cd25949a6854e86d4215a76')
        tools.patch(patch_file='graphviz-skip-dot-layout.patch', base_path=self.source_dir)

    def fixId(self, library):
        if platform.system() == 'Darwin':
            self.run('install_name_tool -id @rpath/lib%s.dylib lib%s.dylib' % (library, library))
        elif platform.system() == 'Linux':
            patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
            self.run('%s --set-soname lib%s.so lib%s.so' % (patchelf, library, library))
            self.run('%s --remove-rpath lib%s.so' % (patchelf, library))
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

    def fixRefs(self, library):
        if platform.system() == 'Darwin':
            self.run('install_name_tool -change %s/libcdt.5.dylib @rpath/libcdt.dylib lib%s.dylib' % (os.getcwd(), library))
            self.run('install_name_tool -change %s/libgvc.6.dylib @rpath/libgvc.dylib lib%s.dylib' % (os.getcwd(), library))
            self.run('install_name_tool -change %s/libpathplan.4.dylib @rpath/libpathplan.dylib lib%s.dylib' % (os.getcwd(), library))
            self.run('install_name_tool -change %s/libgraph.5.dylib @rpath/libgraph.dylib lib%s.dylib' % (os.getcwd(), library))
            self.run('install_name_tool -change %s/libxdot.4.dylib @rpath/libxdot.dylib lib%s.dylib' % (os.getcwd(), library))
        elif platform.system() == 'Linux':
            patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
            self.run('%s --replace-needed libcdt.so.5 libcdt.so lib%s.so' % (patchelf, library))
            self.run('%s --replace-needed libgvc.so.6 libgvc.so lib%s.so' % (patchelf, library))
            self.run('%s --replace-needed libpathplan.so.4 libpathplan.so lib%s.so' % (patchelf, library))
            self.run('%s --replace-needed libgraph.so.5 libgraph.so lib%s.so' % (patchelf, library))
            self.run('%s --replace-needed libxdot.so.4 libxdot.so lib%s.so' % (patchelf, library))
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.cxx_flags.append('-Oz')
            if platform.system() == 'Darwin':
                autotools.flags.append('-mmacosx-version-min=10.10')
                autotools.flags.append('-mno-avx')
                autotools.flags.append('-mno-sse4')
                autotools.flags.append('-mno-sse4.1')
                autotools.flags.append('-mno-sse4.2')
                env_vars = {}
            elif platform.system() == 'Linux':
                env_vars = {
                    'CC' : '/opt/llvm-3.8.0/bin/clang',
                    'CXX': '/opt/llvm-3.8.0/bin/clang++',
                }
            else:
                raise Exception('Unknown platform "%s"' % platform.system())

            autotools.link_flags.append('-Wl,-headerpad_max_install_names')
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
                    for f in self.libs:
                        self.fixId(f)
                        self.fixRefs(f)

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
                    for f in self.libs_plugins:
                        self.fixId(f)
                        self.fixRefs(f)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        for f in self.libs + self.libs_plugins:
            self.copy('lib%s.%s' % (f, libext), src='%s/lib' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = self.libs + self.libs_plugins
