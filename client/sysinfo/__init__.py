#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sysinfo\__init__.py
import blue
PLATFORM_WINDOWS = 2
PLATFORM_MAC_CIDER = -1
PLATFORM_LINUX_CIDER = -2
PLATFORM_MAC_WINE = -3
PLATFORM_LINUX_WINE = -4

def get_os_platform_major_minor_patch():
    if blue.sysinfo.isTransgaming:
        osPlatform = PLATFORM_MAC_CIDER
        versionEx = blue.win32.TGGetSystemInfo()
        osMajor = int(versionEx.get('platform_major_version', 0))
        osMinor = int(versionEx.get('platform_minor_version', 0))
        osPatch = 'Service Pack ' + versionEx.get('platform_extra', '0')
    elif blue.sysinfo.isWine:
        host = blue.sysinfo.wineHostOs
        if host.startswith('Darwin'):
            osPlatform = PLATFORM_MAC_WINE
            version = host.replace('Darwin', '').strip()
            DARWIN_TO_OSX = {'11.4.2': (10, 7, 5),
             '12.0.0': (10, 8, 0),
             '12.6.0': (10, 8, 5),
             '13.0.0': (10, 9, 0),
             '14.0.0': (10, 10, 0),
             '14.5.0': (10, 10, 5),
             '15.0.0': (10, 11, 0),
             '15.3.0': (10, 11, 3)}
            try:
                osMajor, osMinor, osPatch = DARWIN_TO_OSX[version]
            except KeyError:
                components = version.split('.')
                osMajor = int(components[0])
                osMinor = int(components[1])
                osPatch = components[2]

        elif host.startswith('Linux'):
            osPlatform = PLATFORM_LINUX_WINE
            components = host.replace('Linux', '').strip().split('.')
            osMajor = int(components[0])
            osMinor = int(components[1])
            osPatch = components[2]
    else:
        osPlatform = PLATFORM_WINDOWS
        osMajor = blue.sysinfo.os.majorVersion
        osMinor = blue.sysinfo.os.minorVersion
        osPatch = blue.sysinfo.os.patch
    return {'osPlatform': osPlatform,
     'osMajor': osMajor,
     'osMinor': osMinor,
     'osPatch': osPatch}
