#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
from glob import glob
from utils import *


homePath = os.path.expanduser('~')
update = 'lastore-tools test -j upgrade'
install = 'lastore-tools test -j install '
remove = 'lastore-tools test -j remove '


class PkgsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''
        # delete all lock files
        updatefile = glob('/var/lib/dpkg/updates/*')
        lockfile = glob('/var/lib/dpkg/lock')
        cachefile = glob('/var/cache/apt/archives/lock')
        aptlock = glob('/var/lib/apt/lists/lock')
        if len(updatefile) > 0:
            subprocess.check_call('sudo rm /var/lib/dpkg/updates/*', shell=True)
        if len(lockfile) > 0:
            subprocess.check_call('sudo rm /var/lib/dpkg/lock', shell=True)
        if len(cachefile) > 0:
            subprocess.check_call('sudo rm /var/cache/apt/archives/lock', shell=True)
        if len(aptlock) > 0:
            subprocess.check_call('sudo rm /var/lib/apt/lists/lock', shell=True)
        
        # ready for close all opened windows
        

        infofiles = glob(homePath + '/rr/pkgs.info')
        for infofile in infofiles:
            os.remove(infofile)
        '''
        cls.defaultWins = getAllWindowsPid()
        cls.rpadebs = RpaDebs()
        cls.pkgs = [Pkgs(pkg) for pkg in cls.rpadebs.debs]
        cls.not_installed_debs = [pkg for pkg in cls.pkgs if not pkg.isExisted()]
        cls.installed_debs = [pkg for pkg in cls.pkgs if pkg.isExisted()]
        len_deb = len(cls.pkgs)
        try:
            with open('pkgs.info', 'w') as f:
                print('The following %d deb pkg%s will be checked:\n' % (len_deb, len_deb > 1 and "s" or ""))
                f.write('The following %d deb pkg%s will be checked:\n' % (len_deb, len_deb > 1 and "s" or ""))
                for deb in cls.pkgs:
                    print('%s\n' % deb.pkgname)
                    f.write('%s\n' % deb.pkgname)
                print('-' * 50 + '\n')
                f.write('-' * 50 + '\n')
        except Exception as e:
            print(e)
        finally:
            f.close()

        cls.install_passed_pkgs = []
        cls.newInstalledApps = []
        cls.newInstalledServices = []
        cls.local_pkgs = []
        cls.install_passed = []
        cls.install_failed = []
        cls.opened_passed = []
        cls.opened_failed = []
        cls.remove_passed = []
        cls.remove_failed = []
        cls.trayicon = []

    @classmethod
    def tearDownClass(cls):
        num = [i + 1 for i in range(len(cls.pkgs))]
        names = [pkg.pkgname for pkg in cls.pkgs]
        execstr = [pkg.exec_str for pkg in cls.pkgs]
        desktoppath = [pkg.desktop_path for pkg in cls.pkgs]
        install_status = [pkg.installed_status for pkg in cls.pkgs]
        open_status = [pkg.opened_status for pkg in cls.pkgs]
        remove_status = [pkg.removed_status for pkg in cls.pkgs]
        newversion = [pkg.version() for pkg in cls.pkgs]
        rrversion = [cls.rpadebs.version(pkg.pkgname) for pkg in cls.pkgs]
        result = [num, names,  newversion, rrversion, install_status, open_status, remove_status]
        title = ['number', 'name', 'newversion', 'rrversion', 'install_status', 'open_status', 'remove_status']
        with open('result.html', 'w') as f:
            f.write(convertToHtml(result, title))
        f.close()
        '''
        cls.wins = getAllWindowsPid()
        if len(cls.wins) > len(cls.defaultWins):
            for win in cls.wins[len(cls.defaultWins):]:
                Window(win).close()
        '''

        cls.newversion = getDebPkgsVersion()
    '''
    def setUp(self):
        self.defaultWins = window.getAllWindows()

    def tearDown(self):
        self.wins = window.getAllWindows()
        if len(self.wins) > len(self.defaultWins):
            for win in self.wins[len(self.defaultWins):]:
                win.close(1)
    '''

    @property
    def get_install_passed_pkgs(self):
        return self.install_passed_pkgs

    @property
    def get_newInstalledApps(self):
        return self.newInstalledApps

    @property
    def get_newInstalledServices(self):
        return self.newInstalledServices

    @property
    def get_local_pkgs(self):
        return self.local_pkgs


    # test 'sudo apt-get update'
    def test_update(self):
        print('\033[1;31m%s\033[0m' % 'test_update')
        with open('pkgs.info', 'a') as f:
            (s, o) = so(update)
            f.write('test_update\n')
            f.write(update + '\n' + o + '\n')
            f.write('-' * 100 + '\n')
            print(update + '\n' + o + '\n')
            print('-' * 100 + '\n')
            if s != 0:
                f.write(update + ' failed\n')
                f.write('-' * 100 + '\n')
                print(update + ' failed\n')
                print('-' * 100 + '\n')
            else:
                f.write(update + ' successfully\n')
                f.write('-' * 100 + '\n')
                print(update + ' successfully\n')
                print('-' * 100 + '\n')
            self.assertEqual(s, 0, 'sudo apt-get update failed')
        f.close()

    # test install
    def test_pkgs_install(self):
        print('\033[1;31m%s\033[0m' % 'test_pkgs_install')
        for pkg in self.installed_debs:
            pkg.installed_status = 'existed'
        len_pkgs = len(self.not_installed_debs)
        with open('pkgs.info', 'a') as f:
            f.write('test_pkgs_install\n')
            if len_pkgs > 0:
                f.write('The following %d pkg%s are not installed, and will be installed now:\n' % (
                len_pkgs, len_pkgs > 1 and "s" or ""))
                print('The following %d pkg%s are not installed, and will be installed now:' % (
                len_pkgs, len_pkgs > 1 and "s" or ""))
                for pkg in self.not_installed_debs:
                    f.write(pkg.pkgname + '\n')
                    print(pkg.pkgname)
                    s, o = pkg.install()
                    if s != 0:
                        pkg.installed_status = 'failed'
                        self.install_failed.append(pkg)
                        f.write('install ' + pkg.pkgname + ' failed\n' + o + '\n')
                        f.write('-' * 100 + '\n')
                        print('install ' + pkg.pkgname + ' failed\n' + o + '\n')
                        print('-' * 100 + '\n')
                    else:
                        pkg.installed_status = 'successed'
                        self.install_passed.append(pkg.pkgname)
                        f.write('install ' + pkg.pkgname + ' successfully\n')
                        f.write('-' * 100 + '\n')
                        print('install ' + pkg.pkgname + ' successfully\n')
                        print('-' * 100 + '\n')
                    try:
                        self.assertEqual(s, 0, '%s was installed failed' % pkg)
                    except Exception as e:
                        print(e)
            else:
                f.write('All pkgs are installed\n')
                f.write('-' * 100 + '\n')
                print('All deb pkgs are installed')
                print('-' * 100 + '\n')

        f.close()

    # test upgrade pkgs version
    def test_pkgs_version(self):
        print('\033[1;31m%s\033[0m' % 'test_pkgs_version')
        with open('pkgs.info', 'a') as f:
            f.write('test_pkgs_version\n')
            check_pkgs = [Pkgs(pkg) for pkg in self.installed_debs + self.install_passed]
            for pkg in check_pkgs:
                self.local_pkgs.append(pkg.pkgname)
            len_local_pkgs = len(self.local_pkgs)
            if len_local_pkgs > 0:
                f.write('The following %d pkg%s version will be checked:\n' % (
                len_local_pkgs, len_local_pkgs > 1 and "s" or ""))
                pkgs = list(set(self.local_pkgs).intersection(set(self.rpadebs.debs)))
                pkgs = [Pkgs(pkg) for pkg in pkgs]
                for pkg in pkgs:
                    local_version = pkg.version()
                    rpa_version = self.rpadebs.version(pkg.pkgname)
                    f.write('%s version: %s, and rr_verison is: %s\n' % (pkg, local_version, rpa_version))
                    try:
                        self.assertEqual(local_version, rpa_version,
                                         '%s is upgraded to %s now, not %s' % (pkg, local_version, rpa_version))
                    except Exception as e:
                        print(e)
            else:
                f.write('No pkg is installed\n')
                f.write('-' * 100 + '\n')
                print('\033[1;31m%s\033[0m' % 'No pkg is  installed')
                print('-' * 100 + '\n')
            f.write('-' * 100 + '\n')
            print('-' * 100 + '\n')
        f.close()

    def test_pkgs_open(self):
        print('\033[1;31m%s\033[0m' % 'test_pkgs_open')
        with open('pkgs.info', 'a') as f:
            f.write('test_pkgs_open\n')
            print([pkg.pkgname for pkg in self.local_pkgs])
            len_local_pkgs = len(self.local_pkgs)
            if len_local_pkgs > 0:
                f.write('The following %d pkg%s version will be checked:\n' % (
                    len_local_pkgs, len_local_pkgs > 1 and "s" or ""))
                local_pkgs = [pkg for pkg in self.local_pkgs if pkg.exec_name() is not None]
                for pkg in local_pkgs:
                    defaultWindows = getAllWindowsPid()
                    defaulttrayicons = getTrayIcons()

                    pkg.run()
                    wait = 30
                    while wait != 0:
                        sleep(1)
                        wait = wait - 1
                        newWindows = getAllWindowsPid()
                        try:
                            self.assertGreater(len(newWindows), len(defaultWindows),
                                           '%s was not opened successfully in tray' % pkg.pkgname)
                        except Exception as e:
                            print(e)
                        if len(newWindows) > len(defaultWindows):
                            pkg.opened_status = 'passed'
                            self.opened_passed.append(pkg)
                            print('opened %s passed\n' % pkg.pkgname)
                            externalWindows = list(set(newWindows).symmetric_difference(set(defaultWindows)))
                            for wins in externalWindows:
                                Window(wins).close()

                            break
                    else:
                        newtrayicons = getTrayIcons()
                        try:
                            self.assertGreater(len(newtrayicons), len(defaulttrayicons),
                                           '%s was not opened successfully in tray' % pkg.pkgname)
                        except Exception as e:
                            print(e)
                        if len(newtrayicons) > len(defaulttrayicons):
                            trayicons = list(set(newtrayicons).symmetric_difference(set(defaulttrayicons)))
                            print(trayicons)
                            self.trayicon.append(pkg.pkgname)
                            print('opened %s passed\n' % pkg.pkgname)
                            pkg.opened_status = 'passed'
                            self.opened_passed.append(pkg.pkgname)
                        else:
                            pkg.opened_status = 'failed'
                            print([default.get_name() for default in defaultWindows])
                            print(window.getAllWindowsName())
                            self.opened_failed.append(pkg.pkgname)
                            f.write('[%s] run [%s] open failed ' % (pkg.pkgname, pkg.exec_name()))
                            print('opened %s failed\n' % pkg.pkgname)

            else:
                f.write('No pkg is to be opened\n')
                f.write('-' * 100 + '\n')
                print('\033[1;31m%s\033[0m' % 'No pkg to be opened')
                print('-' * 100 + '\n')
            f.write('-' * 100 + '\n')
            print('-' * 100 + '\n')
        f.close()

    # test remove pkgs with cmd
    def test_pkgs_remove(self):
        print('\033[1;31m%s\033[0m' % 'test_pkgs_remove')
        for pkg in self.installed_debs:
            pkg.removed_status = 'default, do not remove'
        len_pkgs = len(self.install_passed)
        with open('pkgs.info', 'a') as f:
            f.write('test_pkgs_remove\n')
            if len_pkgs > 0:
                f.write('The following %d pkg%s will be removed now:\n' % (
                    len_pkgs, len_pkgs > 1 and "s" or ""))
                print('The following %d pkg%s will be removed now:' % (
                    len_pkgs, len_pkgs > 1 and "s" or ""))
                for pkg in self.install_passed:
                    f.write(pkg.pkgname + '\n')
                    print(pkg.pkgname)
                    s, o = pkg.remove()
                    if s != 0:
                        pkg.removed_status = 'failed'
                        self.remove_failed.append(pkg.pkgname)
                        f.write('removed ' + pkg.pkgname + ' failed\n' + o + '\n')
                        f.write('-' * 100 + '\n')
                        print('removed ' + pkg.pkgname + ' failed\n' + o + '\n')
                        print('-' * 100 + '\n')
                    else:
                        pkg.removed_status = 'successed'
                        self.remove_passed.append(pkg.pkgname)
                        f.write('removed ' + pkg.pkgname + ' successfully\n')
                        f.write('-' * 100 + '\n')
                        print('removed ' + pkg.pkgname + ' successfully\n')
                        print('-' * 100 + '\n')
                    try:
                        self.assertEqual(s, 0, '%s was removed failed' % pkg)
                    except Exception as e:
                        print(e)
            else:
                f.write('No pkg is removed\n')
                f.write('-' * 100 + '\n')
                print('\033[1;31m%s\033[0m' % 'No pkg is  removed')
                print('-' * 100 + '\n')
            f.write('-' * 100 + '\n')
            print('-' * 100 + '\n')
        f.close()


def suite():
    suite = unittest.TestSuite()
    #suite.addTest(PkgsTest('test_update'))
    suite.addTest(PkgsTest('test_pkgs_install'))
    suite.addTest(PkgsTest('test_pkgs_version'))
    suite.addTest(PkgsTest('test_pkgs_open'))
    suite.addTest(PkgsTest('test_pkgs_remove'))
    return suite


alltests = unittest.TestSuite(suite())

if __name__ == '__main__':
    with open('test.result', 'w') as logf:
        unittest.TextTestRunner(stream=logf, verbosity=2).run(alltests)
    logf.close()
