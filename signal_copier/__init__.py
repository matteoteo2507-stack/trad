"""Signal Copier — copia segnali da canali Telegram di mentori verso MT5.

Pipeline: reader Telegram (Telethon) → parser per-canale → planner (sizing +
risk gate) → executor (MT5 o dry-run). Fase 1 = demo personale, full-auto.

Vedi `signal_copier/README.md` per architettura e stato.
"""
