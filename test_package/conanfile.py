from conans import ConanFile
import platform

class GraphvizTestConan(ConanFile):
    generators = 'qbs'

    def build(self):
        self.run('qbs -f "%s"' % self.conanfile_directory);

    def imports(self):
        self.copy('*.dylib', dst='bin', src='lib')
        self.copy('*.so', dst='bin', src='lib')

    def test(self):
        self.run('qbs run -f "%s"' % self.conanfile_directory)

        # Ensure we only link to system libraries and our own libraries.
        if platform.system() == 'Darwin':
            self.run('! (otool -L bin/*.dylib | grep -v "^bin/" | egrep -v "^\s*(/usr/lib/|/System/|@rpath/)")')
        elif platform.system() == 'Linux':
            self.run('! (ldd bin/*.so | grep -v "^bin/" | grep "/" | egrep -v "\s/lib64/")')
        else:
            raise Exception('Unknown platform "%s"' % platform.system())
