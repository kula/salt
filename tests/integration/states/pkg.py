'''
tests for pkg state
'''

# Import Salt Testing libs
from salttesting import skipIf
from salttesting.helpers import (
    destructiveTest,
    ensure_in_syspath,
    requires_system_grains,
    requires_salt_modules
)
ensure_in_syspath('../../')

# Import salt libs
import integration
import salt.utils

_PKG_TARGETS = {
    'Arch': ['bzr', 'finch'],
    'Debian': ['python-plist', 'finch'],
    'RedHat': ['bzr', 'finch'],
    'FreeBSD': ['aalib', 'pth'],
    'Suse': ['aalib', 'finch']
}


@requires_salt_modules('pkg.latest_version')
@requires_salt_modules('pkg.version')
class PkgTest(integration.ModuleCase,
              integration.SaltReturnAssertsMixIn):
    '''
    pkg.installed state tests
    '''
    @destructiveTest
    @skipIf(salt.utils.is_windows(), 'minion is windows')
    @requires_system_grains
    def test_pkg_installed(self, grains=None):
        '''
        This is a destructive test as it installs and then removes a package
        '''
        os_family = grains.get('os_family', '')
        pkg_targets = _PKG_TARGETS.get(os_family, [])

        # Make sure that we have targets that match the os_family. If this
        # fails then the _PKG_TARGETS dict above needs to have an entry added,
        # with two packages that are not installed before these tests are run
        self.assertTrue(pkg_targets)

        target = pkg_targets[0]
        version = self.run_function('pkg.version', [target])

        # If this assert fails, we need to find new targets, this test needs to
        # be able to test successful installation of packages, so this package
        # needs to not be installed before we run the states below
        self.assertFalse(version)

        ret = self.run_state('pkg.installed', name=pkg_targets[0])
        self.assertSaltTrueReturn(ret)
        ret = self.run_state('pkg.removed', name=pkg_targets[0])
        self.assertSaltTrueReturn(ret)

    @destructiveTest
    @skipIf(salt.utils.is_windows(), 'minion is windows')
    @requires_system_grains
    def test_pkg_installed_multipkg(self, grains=None):
        '''
        This is a destructive test as it installs and then removes two packages
        '''
        os_family = grains.get('os_family', '')
        pkg_targets = _PKG_TARGETS.get(os_family, [])

        # Make sure that we have targets that match the os_family. If this
        # fails then the _PKG_TARGETS dict above needs to have an entry added,
        # with two packages that are not installed before these tests are run
        self.assertTrue(pkg_targets)

        version = self.run_function('pkg.version', pkg_targets)

        # If this assert fails, we need to find new targets, this test needs to
        # be able to test successful installation of packages, so these
        # packages need to not be installed before we run the states below
        self.assertFalse(any(version.values()))

        ret = self.run_state('pkg.installed', name=None, pkgs=pkg_targets)
        self.assertSaltTrueReturn(ret)
        ret = self.run_state('pkg.removed', name=None, pkgs=pkg_targets)
        self.assertSaltTrueReturn(ret)


if __name__ == '__main__':
    from integration import run_tests
    run_tests(PkgTest)
