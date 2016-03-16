#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\urllib3\packages\ssl_match_hostname\__init__.py
try:
    from ssl import CertificateError, match_hostname
except ImportError:
    try:
        from backports.ssl_match_hostname import CertificateError, match_hostname
    except ImportError:
        from _implementation import CertificateError, match_hostname

__all__ = ('CertificateError', 'match_hostname')
