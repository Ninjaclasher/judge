import os
import subprocess

from dmoj.executors.java_executor import JavaExecutor

with open(os.path.join(os.path.dirname(__file__), 'groovy-security.policy')) as policy_file:
    policy = policy_file.read()


class Executor(JavaExecutor):
    name = 'GROOVY'
    ext = '.groovy'

    compiler = 'groovyc'
    vm = 'groovy_vm'
    security_policy = policy

    test_program = '''\
println System.in.newReader().readLine()
'''

    def create_files(self, problem_id, source_code, *args, **kwargs):
        super(Executor, self).create_files(problem_id, source_code, *args, **kwargs)
        self._class_name = problem_id

    def get_cmdline(self):
        res = super(Executor, self).get_cmdline()

        res[-2:-1] = self.runtime_dict.get('groovy_args') + ['-Dsubmission.file=%s' % self._class_name]
        return res

    def get_compile_args(self):
        return [self.get_compiler(), self._code]

    @classmethod
    def autoconfig(cls):
        result = {}

        for key, files in {'groovyc': ['groovyc'], 'groovy': ['groovy']}.iteritems():
            file = cls.find_command_from_list(files)
            if file is None:
                return result, False, 'Failed to find "%s"' % key
            result[key] = file

        groovy = result.pop('groovy')
        with open(os.devnull, 'w') as devnull:
            process = subprocess.Popen(['bash', '-x', groovy, '-version'], stdout=devnull, stderr=subprocess.PIPE)
        log = [i for i in process.communicate()[1].split('\n') if 'org.codehaus.groovy.tools.GroovyStarter' in i]

        if not log:
            return result, False, 'Failed to parse: %s' % groovy

        cmdline = log[-1].lstrip('+ ').split()
        print cmdline
        result['groovy_vm'] = cls.find_command_from_list([cmdline[1]])
        result['groovy_args'] = [i for i in cmdline[2:-1]]

        data = cls.autoconfig_run_test(result)
        if data[1]:
            data = data[:2] + ('Using %s' % groovy,) + data[3:]
        return data
