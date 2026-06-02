"""Stock Selector V6.0 — versione headless del notebook originale.

Espone `StockSelector` come orchestratore e `run_selection(...)` come funzione
pura per uso programmatico. La CLI è in `__main__.py`.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import yaml

from . import data_sources, scoring
from .scoring import (
    MacroScenario,
    RRGStatus,
    SelectionResult,
    StockPick,
    compute_fundamental_score,
    compute_rrg_status,
    derive_scenario,
    check_scenario_match,
    normalize_debt_to_equity,
)

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.yaml"


# ---------------------------------------------------------------------------
# StockSelector
# ---------------------------------------------------------------------------


class StockSelector:
    """Orchestratore della selezione SP500 V6.0.

    Pure function-style: input → output. L'unico side effect è il salvataggio
    degli Excel (opzionale via flag).
    """

    def __init__(self, config_path: Path | str = DEFAULT_CONFIG_PATH):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config: dict[str, Any] = yaml.safe_load(f)

    # ---- API principale -----------------------------------------------------

    def run(
        self,
        risk_free_rate: float,
        is_liquidity_increasing: bool,
        benchmark: Optional[str] = None,
        save_excel: bool = True,
        output_dir: Path | str = ".",
        tickers_override: Optional[list[str]] = None,
    ) -> SelectionResult:
        """Esegue la selezione completa e restituisce un `SelectionResult`."""
        benchmark = benchmark or self.config["default_benchmark"]
        risk_free_decimal = risk_free_rate / 100

        scenario = derive_scenario(
            risk_free_rate=risk_free_rate,
            is_liquidity_increasing=is_liquidity_increasing,
            high_rate_threshold=self.config["high_rate_threshold"],
        )
        logger.info("Scenario rilevato: %s", scenario.value)

        tickers = self._resolve_tickers(tickers_override)
        history = data_sources.download_history(
            tickers=tickers,
            benchmark=benchmark,
            period=self.config["data"]["history_period"],
            interval=self.config["data"]["history_interval"],
        )

        picks = self._analyze_all(
            tickers=tickers,
            benchmark=benchmark,
            history=history,
            scenario=scenario,
            risk_free_decimal=risk_free_decimal,
        )

        full_sorted = sorted(picks, key=lambda p: p.score, reverse=True)
        min_score = self.config["top_picks_min_score"]
        require_match = self.config.get("top_picks_require_macro_match", False)
        top = [
            p for p in full_sorted
            if p.score >= min_score
            and (not require_match or p.target_match.startswith("SI"))
        ]

        out = Path(output_dir)
        prev_tickers = self._load_previous_top_tickers(out) if save_excel else []
        current_tickers = {p.ticker for p in top}
        sell_signals = self._compute_sell_signals(prev_tickers, current_tickers, full_sorted)

        result = SelectionResult(
            scenario=scenario,
            benchmark=benchmark,
            risk_free_rate=risk_free_rate,
            is_liquidity_increasing=is_liquidity_increasing,
            generated_at=datetime.utcnow(),
            top_picks=top,
            full_analysis=full_sorted,
        )

        if save_excel and full_sorted:
            out.mkdir(parents=True, exist_ok=True)
            top_path = out / self.config["output"]["top_picks_filename"]
            full_path = out / self.config["output"]["full_analysis_filename"]
            self._save_excel(top, top_path)
            self._save_excel(full_sorted, full_path)
            result.excel_top_picks_path = str(top_path)
            result.excel_full_analysis_path = str(full_path)

            if sell_signals:
                sell_path = out / self.config["output"]["sell_signals_filename"]
                self._save_sell_signals_excel(sell_signals, sell_path)
                logger.info("Sell signals: %d ticker da vendere (%s)",
                            len(sell_signals), sell_path)
            else:
                logger.info("Nessun sell signal (prima run o nessuna uscita).")

            self._save_current_top_tickers(out, sorted(current_tickers))

        return result

    # ---- Sell signals -------------------------------------------------------

    def _load_previous_top_tickers(self, output_dir: Path) -> list[str]:
        state_path = output_dir / self.config["output"]["previous_picks_state_filename"]
        if not state_path.exists():
            return []
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
            return list(data.get("tickers", []))
        except Exception as exc:
            logger.warning("Stato precedente illeggibile (%s): %s", state_path, exc)
            return []

    def _save_current_top_tickers(self, output_dir: Path, tickers: list[str]) -> None:
        state_path = output_dir / self.config["output"]["previous_picks_state_filename"]
        payload = {
            "saved_at": datetime.utcnow().isoformat(),
            "tickers": tickers,
        }
        state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _compute_sell_signals(
        self,
        prev_tickers: list[str],
        current_tickers: set[str],
        full_sorted: list[StockPick],
    ) -> list[dict[str, Any]]:
        """Calcola ticker che erano top picks ma non lo sono più.

        Assunzione operativa: l'utente compra TUTTE le top picks della run, quindi
        il "portafoglio" implicito coincide con la lista precedente. Vendere = uscire
        dalla lista corrente.
        """
        if not prev_tickers:
            return []
        exited = [t for t in prev_tickers if t not in current_tickers]
        if not exited:
            return []
        by_ticker = {p.ticker: p for p in full_sorted}
        signals: list[dict[str, Any]] = []
        min_score = self.config["top_picks_min_score"]
        require_match = self.config.get("top_picks_require_macro_match", False)
        for t in exited:
            p = by_ticker.get(t)
            if p is None:
                reason = "Ticker non più presente nell'universo analizzato"
            else:
                reasons = []
                if p.score < min_score:
                    reasons.append(f"score sceso a {p.score} (< {min_score})")
                if require_match and not p.target_match.startswith("SI"):
                    reasons.append(f"target_match={p.target_match} (scenario cambiato)")
                reason = "; ".join(reasons) or "Uscita dalle top picks"
            signals.append({
                "Ticker": t,
                "Settore": p.sector if p else "N/A",
                "Score attuale": p.score if p else None,
                "RRG attuale": p.rrg.value if p else "N/A",
                "Target Match": p.target_match if p else "N/A",
                "Motivo Sell": reason,
            })
        return signals

    def _save_sell_signals_excel(self, signals: list[dict[str, Any]], path: Path) -> None:
        df = pd.DataFrame(signals)
        try:
            with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Sell", index=False)
                wb = writer.book
                ws = writer.sheets["Sell"]
                red = wb.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
                ws.set_column("A:F", 22)
                ws.conditional_format(
                    "A2:A500",
                    {"type": "no_blanks", "format": red},
                )
            logger.info("Salvato: %s", path)
        except Exception as exc:
            logger.error("Errore salvataggio %s: %s", path, exc)

    # ---- Helpers interni ----------------------------------------------------

    def _resolve_tickers(self, override: Optional[list[str]]) -> list[str]:
        if override:
            return data_sources.normalize_tickers_for_yfinance(override)
        raw = data_sources.fetch_sp500_tickers(
            csv_url=self.config["data"]["sp500_csv_url"],
            fallback_tickers=self.config["data"]["fallback_tickers"],
        )
        return data_sources.normalize_tickers_for_yfinance(raw)

    def _analyze_all(
        self,
        tickers: list[str],
        benchmark: str,
        history: pd.DataFrame,
        scenario: MacroScenario,
        risk_free_decimal: float,
    ) -> list[StockPick]:
        results: list[StockPick] = []
        rate_every = self.config["data"]["rate_limit_every"]
        rate_sleep = self.config["data"]["rate_limit_seconds"]
        bench_close = self._extract_close(history, benchmark, multi=len(tickers) > 1)
        if bench_close is None:
            logger.error("Storico benchmark %s mancante. Abort.", benchmark)
            return results

        for i, ticker in enumerate(tickers):
            try:
                if i and i % rate_every == 0:
                    time.sleep(rate_sleep)
                if i % 50 == 0:
                    logger.info("Processing %d/%d", i, len(tickers))

                stk_close = self._extract_close(history, ticker, multi=len(tickers) > 1)
                if stk_close is None:
                    continue

                rrg = compute_rrg_status(stk_close, bench_close, self.config["rrg"])
                pick = self._analyze_one(ticker, rrg, scenario, risk_free_decimal)
                if pick is not None:
                    results.append(pick)
            except Exception as exc:
                logger.debug("Errore su %s: %s", ticker, exc)
                continue
        return results

    @staticmethod
    def _extract_close(history: pd.DataFrame, symbol: str, multi: bool) -> Optional[pd.Series]:
        """Estrae la serie Close dal DataFrame multi-indice di yfinance."""
        try:
            if multi:
                if symbol not in history.columns.get_level_values(0):
                    return None
                return history[symbol]["Close"].dropna()
            return history["Close"].dropna()
        except Exception:
            return None

    def _analyze_one(
        self,
        ticker: str,
        rrg: RRGStatus,
        scenario: MacroScenario,
        risk_free_decimal: float,
    ) -> Optional[StockPick]:
        info = data_sources.fetch_ticker_info(ticker)
        if not info:
            return None

        de = normalize_debt_to_equity(info.get("debtToEquity"))
        pe = info.get("trailingPE")
        eps = info.get("trailingEps")
        ebitda_m = info.get("ebitdaMargins")
        profit_m = info.get("profitMargins")
        roe = info.get("returnOnEquity")
        beta = info.get("beta")

        score, note = compute_fundamental_score(
            de=de,
            pe=pe,
            eps=eps,
            ebitda_margin=ebitda_m,
            profit_margin=profit_m,
            roe=roe,
            risk_free_decimal=risk_free_decimal,
            scoring_cfg=self.config["scoring"],
        )

        macro_match = check_scenario_match(
            de=de,
            beta=beta,
            roe=roe,
            scenario=scenario,
            filters=self.config["scenario_filters"],
        )

        return StockPick(
            ticker=ticker,
            sector=info.get("sector") or "N/A",
            target_match=macro_match,
            score=score,
            rrg=rrg,
            price=info.get("currentPrice"),
            pe=pe,
            de_ratio=de,
            ebitda_margin=ebitda_m,
            profit_margin=profit_m,
            roe=roe,
            beta=beta,
            note=note,
        )

    # ---- Export Excel -------------------------------------------------------

    @staticmethod
    def _picks_to_dataframe(picks: list[StockPick]) -> pd.DataFrame:
        """Stesse colonne e nomi del notebook V6.0 (per parità di output)."""
        rows = [
            {
                "Ticker": p.ticker,
                "Settore": p.sector,
                "TARGET MATCH": p.target_match,
                "SCORE (Max 6)": p.score,
                "RRG Trend": p.rrg.value,
                "Prezzo": p.price,
                "P/E": p.pe,
                "D/E Ratio": p.de_ratio,
                "MOL %": p.ebitda_margin,
                "ROE %": p.roe,
                "Beta": p.beta,
                "Note": p.note,
            }
            for p in picks
        ]
        return pd.DataFrame(rows)

    def _save_excel(self, picks: list[StockPick], path: Path) -> None:
        """Salva l'Excel con la stessa formattazione condizionale del notebook."""
        df = self._picks_to_dataframe(picks)
        try:
            with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Dati", index=False)
                wb = writer.book
                ws = writer.sheets["Dati"]

                green = wb.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})
                red = wb.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
                perc = wb.add_format({"num_format": "0.00%"})

                ws.set_column("I:J", 10, perc)
                ws.conditional_format(
                    "E2:E500",
                    {"type": "text", "criteria": "containing", "value": "LEADING", "format": green},
                )
                ws.conditional_format(
                    "E2:E500",
                    {"type": "text", "criteria": "containing", "value": "LAGGING", "format": red},
                )
                ws.conditional_format(
                    "C2:C500",
                    {"type": "text", "criteria": "begins with", "value": "SI", "format": green},
                )
            logger.info("Salvato: %s", path)
        except Exception as exc:
            logger.error("Errore salvataggio %s: %s", path, exc)


# ---------------------------------------------------------------------------
# API funzionale (firma richiesta dalla skill)
# ---------------------------------------------------------------------------


def run_selection(
    risk_free_rate: float,
    is_liquidity_increasing: bool,
    benchmark: str = "^GSPC",
    save_excel: bool = True,
    output_dir: Path | str = ".",
    tickers_override: Optional[list[str]] = None,
    config_path: Path | str = DEFAULT_CONFIG_PATH,
) -> SelectionResult:
    """Funzione pura: input → `SelectionResult`. Firma definita nella skill."""
    selector = StockSelector(config_path=config_path)
    return selector.run(
        risk_free_rate=risk_free_rate,
        is_liquidity_increasing=is_liquidity_increasing,
        benchmark=benchmark,
        save_excel=save_excel,
        output_dir=output_dir,
        tickers_override=tickers_override,
    )
