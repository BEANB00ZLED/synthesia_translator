from enum import Enum
from dataclasses import dataclass


@dataclass
class AdvancedOptions:
    keyOffset: int = 20


class PianoKey(Enum):
    A0 = 0
    A0sBb0 = 1
    B0 = 2
    C1 = 3
    C1sDb1 = 4
    D1 = 5
    D1sEb1 = 6
    E1 = 7
    F1 = 8
    F1sGb1 = 9
    G1 = 10
    G1sAb1 = 11
    A1 = 12
    A1sBb1 = 13
    B1 = 14
    C2 = 15
    C2sDb2 = 16
    D2 = 17
    D2sEb2 = 18
    E2 = 19
    F2 = 20
    F2sGb2 = 21
    G2 = 22
    G2sAb2 = 23
    A2 = 24
    A2sBb2 = 25
    B2 = 26
    C3 = 27
    C3sDb3 = 28
    D3 = 29
    D3sEb3 = 30
    E3 = 31
    F3 = 32
    F3sGb3 = 33
    G3 = 34
    G3sAb3 = 35
    A3 = 36
    A3sBb3 = 37
    B3 = 38
    C4 = 39  # Middle C
    C4sDb4 = 40
    D4 = 41
    D4sEb4 = 42
    E4 = 43
    F4 = 44
    F4sGb4 = 45
    G4 = 46
    G4sAb4 = 47
    A4 = 48  # A440
    A4sBb4 = 49
    B4 = 50
    C5 = 51
    C5sDb5 = 52
    D5 = 53
    D5sEb5 = 54
    E5 = 55
    F5 = 56
    F5sGb5 = 57
    G5 = 58
    G5sAb5 = 59
    A5 = 60
    A5sBb5 = 61
    B5 = 62
    C6 = 63
    C6sDb6 = 64
    D6 = 65
    D6sEb6 = 66
    E6 = 67
    F6 = 68
    F6sGb6 = 69
    G6 = 70
    G6sAb6 = 71
    A6 = 72
    A6sBb6 = 73
    B6 = 74
    C7 = 75
    C7sDb7 = 76
    D7 = 77
    D7sEb7 = 78
    E7 = 79
    F7 = 80
    F7sGb7 = 81
    G7 = 82
    G7sAb7 = 83
    A7 = 84
    A7sBb7 = 85
    B7 = 86
    C8 = 87
