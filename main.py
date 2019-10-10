import os
import subprocess


class StringToCombinations:
    def __init__(self):
        self.combinations = []
        self._raw_str = '''
aix	ppc64
android	386
android	amd64
android	arm
android	arm64
darwin	386
darwin	amd64
darwin	arm
darwin	arm64
dragonfly	amd64
freebsd	386
freebsd	amd64
freebsd	arm
illumos	amd64
js	wasm
linux	386
linux	amd64
linux	arm
linux	arm64
linux	ppc64
linux	ppc64le
linux	mips
linux	mipsle
linux	mips64
linux	mips64le
linux	s390x
netbsd	386
netbsd	amd64
netbsd	arm
openbsd	386
openbsd	amd64
openbsd	arm
openbsd	arm64
plan9	386
plan9	amd64
plan9	arm
solaris	amd64
windows	386
windows	amd64
'''

    def _str_to_list(self):
        lines = self._raw_str.splitlines(keepends=False)
        for line in lines:
            if len(line) > 0:
                line_list = line.split('\t')
                combination = {'GOOS': line_list[0].strip(), 'GOARCH': line_list[1].strip()}
                self.combinations.append(combination)


class BuildProcess(StringToCombinations):
    def __init__(self, go_root, go_path):
        super().__init__()
        self.go_root = go_root
        self.go_path = go_path
        self.work_dir = ''
        self._str_to_list()

    def _process(self, cmd, *args, env):
        arg = ['go', cmd]
        arg.extend(args)
        print('CGO_ENABLED={} GOOS={} GOARCH={} '.format(
            env['CGO_ENABLED'], env['GOOS'], env['GOARCH']) + ' '.join(arg))
        done = subprocess.run(arg, env=env, cwd=str(self.work_dir), capture_output=True)
        print(done)

    def _select(self, cmd, out_name, version, *args):
        for env in self.combinations:
            env['PATH'] = ':{}{}:{}{}'.format(self.go_root, '/bin', self.go_path, '/bin')\
                          + os.environ["PATH"]
            env['GOCACHE'] = '/tmp/gocache'
            env['GO111MODULE'] = 'auto'
            env['GOPATH'] = self.go_path
            env['GOROOT'] = self.go_root
            env['GOBIN'] = self.go_path + '/bin'
            env['CGO_ENABLED'] = '0'
            name = '{}_{}_{}_{}'.format(out_name, version, env['GOOS'],  env['GOARCH'])
            self._process(cmd, '-o', name, env=env, *args)

    def _build(self, go_file, version):
        out_name = str(go_file).split('/')[-1].split('.')[0]
        # print(out_name)
        self._select('build', out_name, version, go_file)

    def start(self, version, work_dir, go_file):
        version = version.replace('.', '-')
        go_file = go_file.replace('\\', '/')
        if str(go_file).startswith('/'):
            go_file = str(go_file).lstrip(work_dir)
        self.work_dir = work_dir.replace('\\', '/')
        self._build(go_file, version)


if __name__ == '__main__':
    go_root_data = '/home/ffdfgdfg/go/go1.13'
    go_path_data = '/home/ffdfgdfg/go'
    work_dir_data = '/home/ffdfgdfg/go/src/github.com/cnlh/nps'
    go_file_data = 'cmd/npc/npc.go'
    go_file_data1 = 'cmd/nps/nps.go'
    version_data = '0.0.1'
    build = BuildProcess(go_root=go_root_data, go_path=go_path_data)
    print(build.combinations)
    build.start(version_data, work_dir_data, go_file_data)
    build.start(version_data, work_dir_data, go_file_data1)
