#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evePathfinder\pathfinderconst.py
import math
import sys
ROUTE_TYPE_SAFE = 'safe'
ROUTE_TYPE_UNSAFE = 'unsafe'
ROUTE_TYPE_UNSAFE_AND_NULL = 'unsafe + zerosec'
ROUTE_TYPE_SHORTEST = 'shortest'
SECURITY_PENALTY_FACTOR = 0.15
DEFAULT_SECURITY_PENALTY = 50.0
DEFAULT_SECURITY_PENALTY_VALUE = math.exp(SECURITY_PENALTY_FACTOR * DEFAULT_SECURITY_PENALTY)
UNREACHABLE_JUMP_COUNT = sys.maxint
