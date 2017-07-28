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


window = Window()

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
        cls.defaultWins = window.getAllWindows()
        cls.rpadebs = RpaDebs()
        cls.pkgs = [Pkgs(pkg) for pkg in cls.rpadebs.debs]
        #cls.oldversion = getDebPkgsVersion()
        cls.oldversion = [pkg.version() for pkg in cls.pkgs]
        cls.not_installed_debs = [pkg.pkgname for pkg in cls.pkgs if not pkg.isExisted()]
        cls.installed_debs = [pkg.pkgname for pkg in cls.pkgs if pkg.isExisted()]
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
        result = [num, names, cls.oldversion, newversion, install_status, open_status, remove_status]
        title = ['number', 'name', 'oldversion', 'newversion', 'install_status', 'open_status', 'remove_status']
        with open('result.html', 'w') as f:
            f.write(convertToHtml(result, title))
        f.close()
        cls.wins = window.getAllWindows()
        if len(cls.wins) > len(cls.defaultWins):
            for win in cls.wins[len(cls.defaultWins):]:
                win.close(1)

        cls.newversion = getDebPkgsVersion()
        try:
            with open('pkgs.info', 'a') as f:
                for pkg in cls.pkgs:
                    f.write('\nAfter upgrade, %s  version: \t\t%s >> %s\n' % (
                    pkg.pkgname, pkg.oldversion, pkg.newversion))
                    print('\nAfter upgrade, %s  version: \t\t%s >> %s\n' % (
                    pkg.pkgname, pkg.oldversion, pkg.newversion))
        except Exception as e:
            print(e)
        finally:
            f.close()

    def setUp(self):
        self.defaultWins = window.getAllWindows()

    def tearDown(self):
        self.wins = window.getAllWindows()
        if len(self.wins) > len(self.defaultWins):
            for win in self.wins[len(self.defaultWins):]:
                win.close(1)

    @property
    def get_install_passed_pkgs(self):
        return self.install_passed_pkgs

    @property
    def get_newInstalledApps(self):
        return self.newInstalledApps

    @property
    def get_newInstalledServices(self):
        return self.newInstalledServices


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
        len_pkgs = len(self.not_installed_debs)
        with open('pkgs.info', 'a') as f:
            f.write('test_pkgs_install\n')
            if len_pkgs > 0:
                f.write('The following %d pkg%s are not installed, and will be installed now:\n' % (
                len_pkgs, len_pkgs > 1 and "s" or ""))
                print('The following %d pkg%s are not installed, and will be installed now:' % (
                len_pkgs, len_pkgs > 1 and "s" or ""))
                for pkg in self.not_installed_debs:
                    f.write(pkg + '\n')
                    print(pkg)
                    s, o = so(install + pkg)
                    if s != 0:
                        pkg.installed_status = 'successed'
                        f.write('install ' + pkg + ' failed\n' + o + '\n')
                        f.write('-' * 100 + '\n')
                        print('install ' + pkg + ' failed\n' + o + '\n')
                        print('-' * 100 + '\n')
                    else:
                        pkg.installed_status = 'failed'
                        self.install_passed_pkgs.append(pkg)
                        f.write('install ' + pkg + ' successfully\n')
                        f.write('-' * 100 + '\n')
                        print('install ' + pkg + ' successfully\n')
                        print('-' * 100 + '\n')
                    try:
                        self.assertEqual(s, 0, '%s was installed failed' % pkg)
                    except Exception as e:
                        print(e)
            else:
                f.write('All deb pkgs are installed\n')
                f.write('-' * 100 + '\n')
                print('All deb pkgs are installed')
                print('-' * 100 + '\n')

        f.close()

    # test upgrade pkgs version
    def test_pkgs_version(self):
        print('\033[1;31m%s\033[0m' % 'test_pkgs_version')
        with open('pkgs.info', 'a') as f:
            f.write('test_pkgs_version\n')

            self.local_pkgs = [Pkgs(pkg) for pkg in self.installed_debs + self.install_passed_pkgs]
            len_local_pkgs = len(self.local_pkgs)
            if len_local_pkgs > 0:
                f.write('The following %d pkg%s version will be checked:\n' % (
                len_local_pkgs, len_local_pkgs > 1 and "s" or ""))
                pkgs = list(set(self.local_pkgs).intersection(set(self.rpadebs.debs)))
                for pkg in pkgs:
                    local_version = Pkgs(pkg).version()
                    rpa_version = self.rpadebs.version(pkg)
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
        if app.exec_str is not None:
            run_app(app)
            if app.pkg_name in need_passwd_apps:
                sleep(2)
                pyautogui.typewrite(sys.argv[1], interval=1)
                pyautogui.press('enter')
                sleep(1)
            wait = 30
            while wait != 0:
                sleep(1)
                wait = wait - 1
                newWindows = getAllWindowsPid()
                if len(newWindows) > len(defaultWindows):
                    app.opened_status = 'passed'
                    print(defaultWindows)
                    print(newWindows)
                    self.opened_passed.append(app.pkg_name)
                    print('opened %s passed\n' % app.pkg_name)
                    WindowsPid = list(set(newWindows).symmetric_difference(set(defaultWindows)))
                    print(WindowsPid)
                    for winpid in WindowsPid:
                        Window(winpid).close()
                    break
            else:
                newtrayicons = getTrayIcons()
                if len(newtrayicons) > len(defaulttrayicons):
                    trayicons = list(set(newtrayicons).symmetric_difference(set(defaulttrayicons)))
                    print(trayicons)
                    self.trayicon.append(app.pkg_name)
                    print('opened %s passed\n' % app.pkg_name)
                    app.opened_status = 'passed'
                    self.opened_passed.append(app.pkg_name)
                else:
                    app.opened_status = 'failed'
                    print(defaultWindows)
                    print(getAllWindowsPid())
                    self.opened_failed.append(app.pkg_name)
                    f.write('[%s] run [%s] open failed ' % (app.pkg_name, get_desktop_exec(app.pkg_name)))
                    print('opened %s failed\n' % app.pkg_name)

    # test remove pkgs with cmd
    def test_pkgs_remove(self):
        print('\033[1;31m%s\033[0m' % 'test_pkgs_remove')
        len_pkgs = len(self.install_passed_pkgs)
        with open('pkgs.info', 'a') as f:
            f.write('test_pkgs_remove\n')
            if len_pkgs > 0:
                f.write('The following %d pkg%s will be removed now:\n' % (
                    len_pkgs, len_pkgs > 1 and "s" or ""))
                print('The following %d pkg%s will be removed now:' % (
                    len_pkgs, len_pkgs > 1 and "s" or ""))
                for pkg in self.install_passed_pkgs:
                    f.write(pkg + '\n')
                    print(pkg)
                    s, o = so(remove + pkg)
                    if s != 0:
                        pkg.removed_status = 'failed'
                        f.write('removed ' + pkg + ' failed\n' + o + '\n')
                        f.write('-' * 100 + '\n')
                        print('removed ' + pkg + ' failed\n' + o + '\n')
                        print('-' * 100 + '\n')
                    else:
                        pkg.removed_status = 'successed'
                        self.install_passed_pkgs.append(pkg)
                        f.write('removed ' + pkg + ' successfully\n')
                        f.write('-' * 100 + '\n')
                        print('removed ' + pkg + ' successfully\n')
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
    suite.addTest(PkgsTest('test_update'))
    suite.addTest(PkgsTest('test_pkgs_install'))
    suite.addTest(PkgsTest('test_pkgs_version'))
    suite.addTest(PkgsTest('test_pkgs_remove'))
    #suite.addTest(PkgsTest('test_app_open'))
    #suite.addTest(PkgsTest('test_app_uninstall'))
    return suite


alltests = unittest.TestSuite(suite())

if __name__ == '__main__':
    with open('test.result', 'w') as logf:
        unittest.TextTestRunner(stream=logf, verbosity=2).run(alltests)
    logf.close()
