import qbs 1.0

Project {
	minimumQbsVersion: '1.6'
	references: [ buildDirectory + '/../conanbuildinfo.qbs' ]
	Product {
		type: 'application'
		consoleApplication: true

		Depends { name: 'ConanBasicSetup' }

		Depends { name: 'cpp' }
		cpp.cxxStandardLibrary: 'libstdc++'
		cpp.rpaths: [ buildDirectory + '/../../bin' ]

		Depends {
			condition: qbs.targetOS.contains('macos')
			name: 'xcode'
		}
		Properties {
			condition: qbs.targetOS.contains('macos')
			cpp.compilerPathByLanguage: ({
				c: '/usr/local/bin/clang',
				cpp: '/usr/local/bin/clang++',
			})
			cpp.linkerPath: '/usr/local/Cellar/llvm/3.2/bin/clang++'
			cpp.linkerWrapper: undefined
			cpp.minimumMacosVersion: '10.10'
			cpp.target: 'x86_64-apple-macosx10.10'
			cpp.stripPath: '/usr/bin/true'
			xcode.sdk: 'macosx10.10'
		}
		Properties {
			condition: qbs.targetOS.contains('linux')
			cpp.compilerPathByLanguage: ({
				c: '/opt/llvm-3.8.0/bin/clang',
				cpp: '/opt/llvm-3.8.0/bin/clang++',
			})
			cpp.cxxFlags: [ '-fblocks' ]
			cpp.linkerPath: '/opt/llvm-3.8.0/bin/clang++'
			cpp.target: 'x86_64-unknown-linux-gnu'
		}

		files: [ 'test_package.cc' ]
	}
}
