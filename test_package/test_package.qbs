import qbs

Project {
	minimumQbsVersion: 1.6
	references: [ buildDirectory + '/../conanbuildinfo.qbs' ]
	Product {
		type: 'application'
		consoleApplication: true

		Depends { name: 'ConanBasicSetup' }

		Depends { name: 'cpp' }
		cpp.compilerPathByLanguage: {}
		cpp.cxxStandardLibrary: 'libstdc++'
		cpp.rpaths: [ buildDirectory + '/../../bin' ]

		Depends {
			condition: qbs.targetOS.contains("mac")
			name: 'xcode'
		}
		Properties {
			condition: qbs.targetOS.contains("mac")
			cpp.compilerPath: '/usr/local/bin/clang++'
			cpp.linkerPath: '/usr/local/bin/clang++'
			cpp.linkerWrapper: undefined
			cpp.minimumMacosVersion: '10.8'
			cpp.target: 'x86_64-apple-macosx10.8'
			xcode.sdk: 'macosx10.10'
			xcode.buildEnv.env.SDKROOT: undefined
		}
		Properties {
			condition: qbs.targetOS.contains("linux")
			cpp.compilerPath: '/opt/llvm-3.8.0/bin/clang++'
			cpp.cxxFlags: [ '-fblocks' ]
			cpp.linkerPath: '/opt/llvm-3.8.0/bin/clang++'
			cpp.target: 'x86_64-unknown-linux-gnu'
		}

		files: [ 'test_package.cc' ]
	}
}
