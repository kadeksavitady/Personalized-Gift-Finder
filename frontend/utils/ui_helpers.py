def score_bar(pct: float) -> str:
    """Merender progress bar kemiripan berbasis persentase secara dinamis"""
    return f"""
    <div class="score-wrap">
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{pct:.0f}%"></div>
        </div>
        <div class="score-text">Kemiripan {pct:.0f}%</div>
    </div>"""

def badge_kategori(label: str) -> str:
    """Merender badge pembungkus kategori produk"""
    return f'<span class="badge-kategori">{label}</span>'

def badge_rank(rank: int) -> str:
    """Merender badge peringkat rekomendasi (Top 1, 2, 3)"""
    cls = "badge-rank-1" if rank == 1 else "badge-rank-other"
    icon = "⭐ " if rank == 1 else ""
    return f'<span class="{cls}">{icon}#{rank}</span>'