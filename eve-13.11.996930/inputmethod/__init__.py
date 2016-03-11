#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\inputmethod\__init__.py
try:
    import blue
    import _ime
except ImportError:
    import binbootstrapper
    binbootstrapper.update_binaries(__file__, binbootstrapper.DLL_BLUE, binbootstrapper.DLL_IME)
    import blue
    import _ime

Ime = _ime.Ime
__all__ = ['Ime']
