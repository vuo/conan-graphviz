from conans import ConanFile

class GraphvizTestConan(ConanFile):
    generators = 'qbs'

    def build(self):
        self.run('qbs -f "%s"' % self.conanfile_directory);

    def imports(self):
        self.copy('*.dylib', dst='bin', src='lib')

    def test(self):
        self.run('qbs run')

        # Ensure we only link to system libraries and our own libraries.
        self.run('! (otool -L bin/*.dylib | grep -v "^bin/" | egrep -v "^\s*(/usr/lib/|/System/|@rpath/)")')
