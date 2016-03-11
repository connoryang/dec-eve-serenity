#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecrypto\settings.py
import blue

def get_boot():
    try:
        return boot
    except NameError:
        pass

    import eveprefs
    from eveprefs.inmemory import InMemoryIniFile
    return eveprefs.Handler(InMemoryIniFile(role=''))


boot = get_boot()
cryptoPack = boot.GetValue('cryptoPack', 'Placebo')
hashMethod = boot.GetValue('hashMethod', 'SHA')
symmetricKeyMethod = boot.GetValue('symmetricKeyMethod', '3DES')
symmetricKeyLength = boot.GetValue('symmetricKeyLength', 192)
symmetricKeyIVLength = boot.GetValue('symmetricKeyIVLength', None)
symmetricKeyMode = boot.GetValue('symmetricKeyMode', None)
asymmetricKeyLength = boot.GetValue('asymmetricKeyLength', 512)
cryptoAPI_cryptoProvider = boot.GetValue('CryptoAPISecurityProvider', blue.crypto.MS_ENHANCED_PROV)
cryptoAPI_cryptoProviderType = boot.GetValue('CryptoAPISecurityProviderType', 'RSA_FULL')
cryptoAPI_PROV_cryptoProviderType = getattr(blue.crypto, 'PROV_' + cryptoAPI_cryptoProviderType)
cryptoAPI_CALG_hashMethod = getattr(blue.crypto, 'CALG_' + hashMethod, None)
cryptoAPI_CALG_symmetricKeyMethod = getattr(blue.crypto, 'CALG_' + symmetricKeyMethod, None)
