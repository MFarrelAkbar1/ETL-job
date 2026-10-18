"""Daftar semua latihan yang dinilai otomatis, per modul."""

from sql_questions import QUESTIONS

MODULES = {
    "m1_sql": {
        "title": "Modul 1: SQL",
        "ids": [q["id"] for q in QUESTIONS],
        "priority": [q["id"] for q in QUESTIONS if q["priority"]],
    },
    "m2_python": {
        "title": "Modul 2: Python dan pandas",
        "ids": [f"p{i:02d}" for i in range(1, 13)],
        "priority": [],
    },
    "m3_modeling": {
        "title": "Modul 3: Data modeling (grain, fact, dimension)",
        "ids": [f"g{i:02d}" for i in range(1, 9)],
        "priority": [],
    },
    "m4_quality": {
        "title": "Modul 4: Data quality",
        "ids": [f"dq{i:02d}" for i in range(1, 9)],
        "priority": [],
    },
    "m6_iceberg": {
        "title": "Modul 6: Lakehouse dan Iceberg",
        "ids": [f"ice{i:02d}" for i in range(1, 8)],
        "priority": [],
    },
    "m8_airflow": {
        "title": "Modul 8: Airflow (struktur DAG)",
        "ids": [f"dag{i:02d}" for i in range(1, 4)],
        "priority": [],
    },
}
