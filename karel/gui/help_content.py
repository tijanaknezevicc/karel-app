LEVEL_HELP = {
    "linijski": {
        "title": "Linijski program",
        "sections": [
            {
                "heading": "Komande za kretanje i loptice",
                "items": [
                    ("napred()", "Pomera robota jedno polje napred u pravcu u kom gleda."),
                    ("levo()", "Okreće robota za 90° ulevo, bez pomeranja."),
                    ("desno()", "Okreće robota za 90° udesno, bez pomeranja."),
                    ("uzmi()", "Skuplja jednu lopticu sa polja na kom robot stoji."),
                    ("ostavi()", "Ostavlja jednu lopticu iz robotove torbe na polje na kom stoji."),
                ],
            },
        ],
        "example": "napred()\nnapred()\nlevo()\nuzmi()",
    },
    "brojacka_petlja": {
        "title": "Brojačka petlja",
        "sections": [
            {
                "heading": "Iste komande kao i do sad",
                "items": [
                    ("napred(), levo(), desno(), uzmi(), ostavi()", "Rade isto kao na prethodnom nivou."),
                ],
            },
            {
                "heading": "Novo: for petlja",
                "items": [
                    ("for i in range(N):", "Ponavlja komande unutar petlje tačno N puta. Broj N moraš sama/sam da prebrojiš sa slike."),
                ],
            },
        ],
        "example": "for i in range(4):\n    napred()\n    uzmi()",
    },
    "uslovna_petlja": {
        "title": "Uslovna petlja",
        "sections": [
            {
                "heading": "Iste komande kao i do sad",
                "items": [
                    ("napred(), levo(), desno(), uzmi(), ostavi(), for", "Rade isto kao na prethodnim nivoima."),
                ],
            },
            {
                "heading": "Novo: senzori (samo čitaju stanje u lavirintu, ne menjaju ništa)",
                "items": [
                    ("moze_napred()", "Da li je polje ispred robota slobodno? Rezultat je 'tačno' ili 'netačno'."),
                    ("ima_loptica_na_polju()", "Da li na trenutnom polju ima loptica? Rezultat je 'tačno' ili 'netačno'."),
                    ("broj_loptica_na_polju()", "Vraća broj loptica na trenutnom polju."),
                    ("ima_loptica_kod_sebe()", "Da li robot ima kod sebe bar jednu lopticu? Rezultat je 'tačno' ili 'netačno'."),
                    ("broj_loptica_kod_sebe()", "Vraća broj loptica koje robot trenutno ima kod sebe."),
                ],
            },
            {
                "heading": "Novo: while petlja",
                "items": [
                    ("while uslov:", "Ponavlja komande unutar petlje sve dok je uslov tačan."),
                ],
            },
        ],
        "example": "while moze_napred():\n    napred()\n\nwhile ima_loptica_na_polju():\n    uzmi()",
    },
    "grananje": {
        "title": "Grananje",
        "sections": [
            {
                "heading": "Iste komande kao i do sad",
                "items": [
                    ("napred(), levo(), desno(), uzmi(), ostavi(), for, while, senzori", "Rade isto kao na prethodnim nivoima."),
                ],
            },
            {
                "heading": "Novo: if / else",
                "items": [
                    ("if uslov:", "Izvršava komande unutar bloka samo ako je uslov tačan."),
                    ("else:", "Izvršava komande unutar bloka samo ako je uslov iz if-a netačan."),
                ],
            },
        ],
        "example": "if ima_loptica_na_polju():\n    uzmi()\nelse:\n    napred()",
    },
    "napredni": {
        "title": "Napredni nivo",
        "sections": [
            {
                "heading": "Sve komande i konstrukcije",
                "items": [
                    ("napred(), levo(), desno(), uzmi(), ostavi()", "Osnovne komande."),
                    ("for, while, if / else", "Sve konstrukcije koje smo do sad naučili."),
                    ("moze_napred(), ima_loptica_na_polju(), broj_loptica_na_polju(), ima_loptica_kod_sebe(), broj_loptica_kod_sebe()", "Svi senzori."),
                ],
            },
        ],
        "example": "while moze_napred():\n    if ima_loptica_na_polju():\n        uzmi()\n    napred()",
    },
}