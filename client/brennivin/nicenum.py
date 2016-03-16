#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\nicenum.py
import math as _math

def format(num, precision):
    accpow = _math.floor(_math.log10(precision))
    if num < 0:
        digits = int(_math.fabs(num / pow(10, accpow) - 0.5))
    else:
        digits = int(_math.fabs(num / pow(10, accpow) + 0.5))
    result = ''
    if digits > 0:
        for i in range(0, int(accpow)):
            if i % 3 == 0 and i > 0:
                result = '0,' + result
            else:
                result = '0' + result

        curpow = int(accpow)
        while digits > 0:
            adigit = chr(digits % 10 + ord('0'))
            if curpow % 3 == 0 and curpow != 0 and len(result) > 0:
                if curpow < 0:
                    result = adigit + ' ' + result
                else:
                    result = adigit + ',' + result
            elif curpow == 0 and len(result) > 0:
                result = adigit + '.' + result
            else:
                result = adigit + result
            digits //= 10
            curpow += 1

        for i in range(curpow, 0):
            if i % 3 == 0 and i != 0:
                result = '0 ' + result
            else:
                result = '0' + result

        if curpow <= 0:
            result = '0.' + result
        if num < 0:
            result = '-' + result
    else:
        result = '0'
    return result


KB = 1024

def format_memory(val):
    val = float(val)
    if val < KB:
        label = 'B'
    elif KB < val < KB ** 2:
        label = 'KB'
        val /= KB
    elif KB ** 2 < val < KB ** 3:
        label = 'MB'
        val /= KB ** 2
    else:
        label = 'GB'
        val /= KB ** 3
    return str(round(val, 2)) + label
