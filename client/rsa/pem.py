#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\rsa\pem.py
import base64
from rsa._compat import b, is_bytes

def _markers(pem_marker):
    if is_bytes(pem_marker):
        pem_marker = pem_marker.decode('utf-8')
    return (b('-----BEGIN %s-----' % pem_marker), b('-----END %s-----' % pem_marker))


def load_pem(contents, pem_marker):
    pem_start, pem_end = _markers(pem_marker)
    pem_lines = []
    in_pem_part = False
    for line in contents.splitlines():
        line = line.strip()
        if not line:
            continue
        if line == pem_start:
            if in_pem_part:
                raise ValueError('Seen start marker "%s" twice' % pem_start)
            in_pem_part = True
            continue
        if not in_pem_part:
            continue
        if in_pem_part and line == pem_end:
            in_pem_part = False
            break
        if b(':') in line:
            continue
        pem_lines.append(line)

    if not pem_lines:
        raise ValueError('No PEM start marker "%s" found' % pem_start)
    if in_pem_part:
        raise ValueError('No PEM end marker "%s" found' % pem_end)
    pem = b('').join(pem_lines)
    return base64.decodestring(pem)


def save_pem(contents, pem_marker):
    pem_start, pem_end = _markers(pem_marker)
    b64 = base64.encodestring(contents).replace(b('\n'), b(''))
    pem_lines = [pem_start]
    for block_start in range(0, len(b64), 64):
        block = b64[block_start:block_start + 64]
        pem_lines.append(block)

    pem_lines.append(pem_end)
    pem_lines.append(b(''))
    return b('\n').join(pem_lines)
