"""
P07 | Transform: groupby dan agregasi
Tingkat: SEDANG

SOAL
  1. monthly_revenue_by_segment(df) -> DataFrame
       Input punya kolom: order_id, order_date (datetime64), status, segment, line_amount.
       - hanya status 'COMPLETED'
       - kolom output (urut): month, segment, revenue, n_orders, avg_order_value
           month            string 'YYYY-MM'
           revenue          jumlah line_amount, dibulatkan 2 desimal
           n_orders         jumlah order_id UNIK (int)
           avg_order_value  revenue / n_orders, dibulatkan 2 desimal
       - urut month lalu segment, index di-reset

  2. top_n_per_group(df, group_col, value_col, n=3) -> DataFrame
       - untuk setiap grup, ambil n baris dengan value_col terbesar
       - kalau nilai seri, baris yang muncul lebih dulu di input menang
       - tambahkan kolom 'rank' (int, mulai 1) di akhir
       - urut group_col lalu rank, index di-reset

Uji     : task test-python -- -k p07
Petunjuk: task hint -- p07
"""

from __future__ import annotations

import pandas as pd


def monthly_revenue_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError


def top_n_per_group(df: pd.DataFrame, group_col: str, value_col: str, n: int = 3) -> pd.DataFrame:
    raise NotImplementedError
