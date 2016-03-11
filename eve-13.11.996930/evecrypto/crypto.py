#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecrypto\crypto.py
import blue
import evecrypto.cryptoapi as cryptoapi
import evecrypto.placebo as placebo
import evecrypto.settings as settings
if '/generatekeys' in blue.pyos.GetArg():
    from evecrypto.restricted.gen_pykeys import generate_keys
    generate_keys(cryptoapi.get_crypto_context())
if settings.cryptoPack == 'CryptoAPI':
    impl = cryptoapi
else:
    impl = placebo
GetCryptoContext = cryptoapi.get_crypto_context
CryptoHash = impl.crypto_hash
CryptoCreateContext = impl.create_context
GetRandomBytes = impl.get_random_bytes
Sign = impl.sign
Verify = impl.verify
publicKey = impl.publicKey
publicKeyVersion = impl.publicKeyVersion
privateKey = impl.privateKey
privateKeyVersion = impl.privateKeyVersion
