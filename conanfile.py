from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import shutil

class GraphvizConan(ConanFile):
    name = 'graphviz'
    version = '2.28.0'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-graphviz'
    license = 'http://graphviz.org/License.php'
    description = 'A way of representing structural information as diagrams of abstract graphs and networks'
    source_dir = 'graphviz-%s' % version
    build_dir = '_build'
    libs = ['cdt', 'gvc', 'pathplan', 'graph', 'xdot']
    libs_plugins = ['gvplugin_dot_layout', 'gvplugin_core']

    def source(self):
        tools.get('http://www.graphviz.org/pub/graphviz/stable/SOURCES/graphviz-%s.tar.gz' % self.version,
                  sha256='d3aa7973c578cae4cc26d9d6498c57ed06680cab9a4e940d0357a3c6527afc76')

        tools.download('https://b33p.net/sites/default/files/graphviz-skip-dot-layout.patch', 'graphviz-skip-dot-layout.patch')
        tools.check_sha256('graphviz-skip-dot-layout.patch', 'c6a7022521c5559ba56f92845c2f1b4b87f541b87cd25949a6854e86d4215a76')
        tools.patch(patch_file='graphviz-skip-dot-layout.patch', base_path=self.source_dir)

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.cxx_flags.append('-Oz')
            autotools.cxx_flags.append('-mmacosx-version-min=10.8')
            autotools.cxx_flags.append('-mno-avx')
            autotools.cxx_flags.append('-mno-sse4')
            autotools.cxx_flags.append('-mno-sse4.1')
            autotools.cxx_flags.append('-mno-sse4.2')
            autotools.link_flags.append('-Wl,-headerpad_max_install_names')
            autotools.configure(configure_dir='../%s' % self.source_dir,
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
            autotools.make()
            with tools.chdir('lib'):
                autotools.make(args=['install'])
                shutil.move('libcdt.5.dylib', 'libcdt.dylib')
                shutil.move('libgvc.6.dylib', 'libgvc.dylib')
                shutil.move('libpathplan.4.dylib', 'libpathplan.dylib')
                shutil.move('libgraph.5.dylib', 'libgraph.dylib')
                shutil.move('libxdot.4.dylib', 'libxdot.dylib')
                for f in self.libs:
                    self.run('install_name_tool -id @rpath/lib%s.dylib lib%s.dylib' % (f, f))
                    self.run('install_name_tool -change %s/libcdt.5.dylib @rpath/libcdt.dylib lib%s.dylib' % (os.getcwd(), f))
                    self.run('install_name_tool -change %s/libgvc.6.dylib @rpath/libgvc.dylib lib%s.dylib' % (os.getcwd(), f))
                    self.run('install_name_tool -change %s/libpathplan.4.dylib @rpath/libpathplan.dylib lib%s.dylib' % (os.getcwd(), f))
                    self.run('install_name_tool -change %s/libgraph.5.dylib @rpath/libgraph.dylib lib%s.dylib' % (os.getcwd(), f))
                    self.run('install_name_tool -change %s/libxdot.4.dylib @rpath/libxdot.dylib lib%s.dylib' % (os.getcwd(), f))
            with tools.chdir('plugin'):
                autotools.make(args=['install'])
            with tools.chdir('lib/graphviz'):
                shutil.move('libgvplugin_dot_layout.6.dylib', '../libgvplugin_dot_layout.dylib')
                shutil.move('libgvplugin_core.6.dylib', '../libgvplugin_core.dylib')
            with tools.chdir('lib'):
                for f in self.libs_plugins:
                    self.run('install_name_tool -id @rpath/lib%s.dylib lib%s.dylib' % (f, f))
                    self.run('install_name_tool -change %s/libcdt.5.dylib @rpath/libcdt.dylib lib%s.dylib' % (os.getcwd(), f))
                    self.run('install_name_tool -change %s/libgvc.6.dylib @rpath/libgvc.dylib lib%s.dylib' % (os.getcwd(), f))
                    self.run('install_name_tool -change %s/libpathplan.4.dylib @rpath/libpathplan.dylib lib%s.dylib' % (os.getcwd(), f))
                    self.run('install_name_tool -change %s/libgraph.5.dylib @rpath/libgraph.dylib lib%s.dylib' % (os.getcwd(), f))
                    self.run('install_name_tool -change %s/libxdot.4.dylib @rpath/libxdot.dylib lib%s.dylib' % (os.getcwd(), f))

    def package(self):
        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        for f in self.libs + self.libs_plugins:
            self.copy('lib%s.dylib' % f, src='%s/lib' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = self.libs
