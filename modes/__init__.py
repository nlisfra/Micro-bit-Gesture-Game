from .addition import ADDITION_QUESTIONS
from .subtraction import SUBTRACTION_QUESTIONS
from .multiplication import MULTIPLICATION_QUESTIONS
from .division import DIVISION_QUESTIONS

QUESTIONS_BY_OPERATION = {
    "addition": ADDITION_QUESTIONS,
    "subtraction": SUBTRACTION_QUESTIONS,
    "multiplication": MULTIPLICATION_QUESTIONS,
    "division": DIVISION_QUESTIONS
}

# Informasi setiap operasi
OPERATION_INFO = {
    "addition": {
        "name": "PENJUMLAHAN",
        "icon": "+",
        "color": (46, 204, 113),  # Hijau
        "theme": "animals",
        "desc": "Belajar penjumlahan dengan hewan-hewan lucu"
    },
    "subtraction": {
        "name": "PENGURANGAN",
        "icon": "-",
        "color": (231, 76, 60),  # Merah
        "theme": "animals",
        "desc": "Belajar pengurangan dengan hewan-hewan lucu"
    },
    "multiplication": {
        "name": "PERKALIAN",
        "icon": "×",
        "color": (241, 196, 15),  # Kuning
        "theme": "toys",
        "desc": "Belajar perkalian dengan mainan-mainan seru"
    },
    "division": {
        "name": "PEMBAGIAN",
        "icon": "÷",
        "color": (155, 89, 182),  # Ungu
        "theme": "foods",
        "desc": "Belajar pembagian dengan makanan-makanan lezat"
    }
}

__all__ = [
    'QUESTIONS_BY_OPERATION',
    'OPERATION_INFO',
    'ADDITION_QUESTIONS',
    'SUBTRACTION_QUESTIONS',
    'MULTIPLICATION_QUESTIONS',
    'DIVISION_QUESTIONS'
]