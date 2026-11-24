// PortafoglioIntradayNT - Motore Profitto (10/11/2026). Versione NinjaTrader (futures) dell'EA MT5 PortafoglioIntraday,
// set INTRADAY_BIL (stessa logica, cambiano solo i mercati: CFD -> futures micro).
//  Regole intraday (1 trade al giorno per regola, stop iniziale, uscita a fine sessione, nessun target):
//    1 GER40  fade Londra 30m (FDXS, Eurex: lascia vuoto se la prop non ha Eurex)   5 ETH NR-ORB30 NY (spenta)
//    2 BTC    fade NY 15m (spenta)                                                  6 SP500  NR-ORB30 NY  (MES)
//    3 NAS100 prima ora NY 60m (MNQ)                                                7 NAS100 NR-ORB30 NY  (MNQ)
//    4 oro    fade NY 5m (MGC)                                                      8 petrolio NR-ORB30 Londra (MCL)
//    Gruppi di rischio come il preset: A (6,7) 0,50%  B (3,8) 0,44%  C (1,4) 0,30% dell'equity a trade.
//  News oro NFP / CPI / FOMC: stop-and-reverse nel minuto dopo l'uscita (ordini stop a ~5 $ che seguono il prezzo).
//    11/11: ordini aggiornati ogni 1 s e inversione piazzata 2 s dopo l'esecuzione (come MT5). Sui tick veri del future
//    la versione veloce (250 ms, inversione subito) perdeva: troppe inversioni e slittamento.
//  18/11 (soci): regola 4 spenta sui futures (gruppo C = "1"), news oro solo NFP (tipi = "1").
//  Guardiano: perdita del giorno oltre il limite (% e/o $, dal saldo a mezzanotte di Atene) -> chiude tutto, fermo fino a domani.
//  Tetto contratti: non supera MaxMicro (micro = 1, mini = 10).
//  PREDEFINITI = FundedNext Futures Rapid Daily 25k: rischio 0,25/0,22/0,15%, news 30 once (3 MGC), stop giorno 400 $, max 20 micro.
// USO: un grafico qualsiasi (es. MGC 5 minuti), almeno 60 giorni caricati, Strategia > PortafoglioIntradayNT.
//  Le regole leggono da sole i loro mercati (serie 5 minuti). Calendario news: Documenti\NinjaTrader 8\news_eventi.csv
//  A OGNI SCADENZA (rollover) aggiornare i nomi dei contratti nelle impostazioni (es. MNQ 12-26 -> MNQ 03-27).
//  "Backtest" = true SOLO nello Strategy Analyzer; sul grafico lasciarlo false (lo storico serve solo a ricostruire lo stato).
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
	public class PortafoglioIntradayNT : Strategy
	{
		private static readonly int[] TIPO = { 1, 2, 3, 4, 5, 5, 5, 5 };     // 1 fade 30 Londra, 2 fade 15 NY, 3 prima ora, 4 fade 5 NY, 5 NR-ORB30
		private static readonly bool[] LON = { true, false, false, false, false, false, false, true };

		private class Regola
		{
			public int n, serie = -1; public string strum = ""; public bool on; public double rischio;
			public DateTime giorno = DateTime.MinValue; public bool fatto, stretta; public double rh, rl, est, hs, ls; public int rott;
			public List<double> rng = new List<double>();
		}
		private class Gamba
		{
			public string nome; public int idx, lato, qty; public double stop; public bool chiudi, finita, sr;
			public Order entrata, ordStop, uscita;
		}

		private readonly Regola[] regole = new Regola[8];
		private readonly List<string> serieNomi = new List<string>();      // strumento della serie 5 min (indice = posizione + 1)
		private readonly List<Gamba> gambe = new List<Gamba>();
		private TimeZoneInfo tzNt, tzNy, tzLon, tzAte;
		private int serieOro = -1;
		private readonly List<DateTime> newsUtc = new List<DateTime>();

		// news (stop-and-reverse)
		private Order srBuy, srSell, srRev, srEsci;
		private int srPos, srQ, srConta;
		private DateTime srUltimo = DateTime.MinValue, srUltimaEsec = DateTime.MinValue;

		// guardiano
		private DateTime gsGiorno = DateTime.MinValue; private bool gsFermo, gsFinito; private double gsRif, gsPart;
		private DateTime gsUltimo = DateTime.MinValue;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "PortafoglioIntradayNT";
				Description = "Portafoglio intraday bilanciato (versione futures dell'EA MT5): 6 regole intraday + news oro + guardiano -4% al giorno.";
				Calculate = Calculate.OnBarClose;
				IsUnmanaged = true;
				IsExitOnSessionCloseStrategy = false;
				BarsRequiredToTrade = 0;
				EntriesPerDirection = 10;
				StartBehavior = StartBehavior.ImmediatelySubmit;
				TraceOrders = false;
				// valori predefiniti = FundedNext Futures Rapid Daily 25k (11/11/2026): rischio x0,5, news 3 MGC, stop giorno 400 $, max 20 micro
				Insieme = "RAPID_DAILY_25K";
				RischioA = 0.25; RischioB = 0.22; RischioC = 0.15;
				AttiveA = "67"; AttiveB = "38"; AttiveC = "1";
				MinimoSempre = false; UsaCuscinetto = true;
				Strumenti = ",,MNQ 12-26,MGC 12-26,,MES 12-26,MNQ 12-26,MCL 01-27";
				UsaNews = true; OroNews = "MGC 12-26"; NewsOnce = 30; NewsTipi = "1";
				NewsAggiornaMs = 1000; NewsAttesaInversione = 2;
				StopGiorno = 0; StopGiornoDollari = 490; MaxMicro = 20; Obiettivo = 0; SaldoPartenza = 0;
				Backtest = false; CapitaleTest = 25000; ContoVirtuale = 0;
			}
			else if (State == State.Configure)
			{
				string[] p = (Strumenti ?? "").Split(',');
				for (int i = 0; i < 8; i++)
				{
					Regola r = new Regola(); r.n = i + 1; r.strum = i < p.Length ? p[i].Trim() : "";
					r.on = r.strum != "" && (AttiveA + AttiveB + AttiveC).Contains((i + 1).ToString());
					r.rischio = AttiveA.Contains((i + 1).ToString()) ? RischioA : AttiveB.Contains((i + 1).ToString()) ? RischioB : RischioC;
					if (r.on)
					{
						int k = serieNomi.IndexOf(r.strum);
						if (k < 0) { serieNomi.Add(r.strum); AddDataSeries(r.strum, BarsPeriodType.Minute, 5); k = serieNomi.Count - 1; }
						r.serie = k + 1;
					}
					regole[i] = r;
				}
				if (UsaNews && OroNews.Trim() != "")
				{
					if (Backtest) AddDataSeries(OroNews.Trim(), BarsPeriodType.Second, 1);     // nel test serve il secondo per gli ordini stop
					else AddDataSeries(OroNews.Trim(), BarsPeriodType.Minute, 1);             // dal vivo lavora sui tick (OnMarketData)
					serieOro = serieNomi.Count + 1;
				}
			}
			else if (State == State.DataLoaded)
			{
				tzNt = NinjaTrader.Core.Globals.GeneralOptions.TimeZoneInfo;
				tzNy = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
				tzLon = TimeZoneInfo.FindSystemTimeZoneById("GMT Standard Time");
				tzAte = TimeZoneInfo.FindSystemTimeZoneById("GTB Standard Time");
				if (UsaNews) CaricaNews();
				gsPart = SaldoPartenza > 0 ? SaldoPartenza : (Backtest ? CapitaleTest : 0);
				for (int i = 0; i < 8; i++)
					if (regole[i].on) Print(string.Format("PortafoglioIntradayNT: regola {0} su {1} (serie {2}), rischio {3:0.00}%", i + 1, regole[i].strum, regole[i].serie, regole[i].rischio));
			}
			else if (State == State.Realtime)
			{
				if (Backtest) { gambe.Clear(); srPos = 0; }
				if (ContoVirtuale > 0) { virtBase = SaldoReale(); gsRif = 0; gsGiorno = DateTime.MinValue; }
				if (gsPart <= 0 || ContoVirtuale > 0) gsPart = SaldoPartenza > 0 ? SaldoPartenza : Saldo();
				if (ContoVirtuale > 0) Print(string.Format("PortafoglioIntradayNT: conto virtuale {0:0} $ (conto vero {1:0.00} $): contratti e stop calcolati sul virtuale", ContoVirtuale, virtBase));
				Print(string.Format("PortafoglioIntradayNT avviato: set {0}, saldo di partenza {1:0.00}, stop giorno {2}%, obiettivo {3}%, news {4}",
					Insieme, gsPart, StopGiorno, Obiettivo, UsaNews ? "si" : "no"));
				if (UsaCuscinetto) { string ic; NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Moltiplicatore(Account, out ic); Print("PortafoglioIntradayNT CUSCINETTO acceso: " + ic); } else Print("PortafoglioIntradayNT cuscinetto: spento");
			}
		}

		// ------------------------------------------------------------------ tempo
		private DateTime Utc(DateTime t)
		{
			try { return TimeZoneInfo.ConvertTimeToUtc(DateTime.SpecifyKind(t, DateTimeKind.Unspecified), tzNt); }
			catch { return TimeZoneInfo.ConvertTimeToUtc(DateTime.SpecifyKind(t.AddHours(1), DateTimeKind.Unspecified), tzNt).AddHours(-1); }
		}
		private DateTime Ora(DateTime t, bool ny) { return TimeZoneInfo.ConvertTimeFromUtc(Utc(t), ny ? tzNy : tzLon); }
		private bool Operativo() { return State == State.Realtime || Backtest; }

		private void CaricaNews()
		{
			string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "news_eventi.csv");
			if (!File.Exists(f)) { Print("PortafoglioIntradayNT: news_eventi.csv NON trovato in " + f + " - news spente"); return; }
			foreach (string riga in File.ReadAllLines(f))
			{
				string[] p = riga.Split(';');
				if (p.Length < 2 || !NewsTipi.Contains(p[0].Trim())) continue;
				DateTime t;
				if (!DateTime.TryParseExact(p[1].Trim(), "yyyy.MM.dd HH:mm", CultureInfo.InvariantCulture, DateTimeStyles.None, out t)) continue;
				newsUtc.Add(TimeZoneInfo.ConvertTimeToUtc(t, tzAte));          // il calendario e' in ora del server MT5 (Atene)
			}
			Print("PortafoglioIntradayNT: news caricate " + newsUtc.Count);
		}

		// ------------------------------------------------------------------ conto
		private double Profitto()
		{
			double u = 0; HashSet<string> visti = new HashSet<string>();
			for (int i = 0; i < BarsArray.Length; i++)
			{
				string nome = BarsArray[i].Instrument.FullName;
				if (!visti.Add(nome) || CurrentBars[i] < 0) continue;
				if (Positions[i].MarketPosition != MarketPosition.Flat) u += Positions[i].GetUnrealizedProfitLoss(PerformanceUnit.Currency, Closes[i][0]);
			}
			return u;
		}
		// Conto virtuale: su un demo piu' grande (es. 50.000) l'EA lavora come se il conto fosse ContoVirtuale (es. 25.000)
		private double virtBase = -1;
		// 12/11: registro eventi per gli avvisi Telegram (solo scrittura su file, nessun effetto sul trading)
		private void Evento(string s)
		{
			if (State != State.Realtime) return;
			for (int t = 0; t < 3; t++)
				try { File.AppendAllText(Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "eventi_bot.txt"), DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "|" + Name + "|" + s.Replace(Environment.NewLine, " ") + Environment.NewLine); return; }
				catch { System.Threading.Thread.Sleep(20); }
		}
		private void Pr(string s) { Print(s); Evento(s); }

		private double Virtuale(double reale)
		{
			if (ContoVirtuale <= 0 || State != State.Realtime || virtBase <= 0) return reale;
			return ContoVirtuale + (reale - virtBase);
		}
		private double SaldoReale()
		{
			if (State == State.Realtime && Account != null)
			{
				double c = Account.Get(AccountItem.CashValue, Currency.UsDollar);
				if (c > 0) return c;
			}
			return CapitaleTest + SystemPerformance.AllTrades.TradesPerformance.Currency.CumProfit;
		}
		private double Saldo() { return Virtuale(SaldoReale()); }
		private double Equity()
		{
			if (State == State.Realtime && Account != null)
			{
				double nl = Account.Get(AccountItem.NetLiquidation, Currency.UsDollar);
				if (nl > 0) return Virtuale(nl);
				double c = Account.Get(AccountItem.CashValue, Currency.UsDollar);
				if (c > 0) return Virtuale(c + Profitto());
			}
			return CapitaleTest + SystemPerformance.AllTrades.TradesPerformance.Currency.CumProfit + Profitto();
		}

		// ------------------------------------------------------------------ guardiano (true = si puo' lavorare)
		private bool Guardiano(DateTime adessoUtc)
		{
			if (!Operativo()) return true;
			if (UsaCuscinetto && State == State.Realtime) NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Aggiorna(Account);   // 19/11: registra il saldo per il massimo di fine giornata
			DateTime g = TimeZoneInfo.ConvertTimeFromUtc(adessoUtc, tzAte).Date;
			double eq = Equity();
			if (g != gsGiorno)
			{
				gsGiorno = g; gsRif = Saldo();
				if (gsFermo) { gsFermo = false; Print("GUARDIANO: nuovo giorno, si riparte"); }
			}
			if (gsFinito) return false;
			if (Obiettivo > 0 && gsPart > 0 && eq >= gsPart * (1 + Obiettivo / 100))
			{
				gsFinito = true; ChiudiTutto();
				Pr(string.Format("GUARDIANO: obiettivo +{0:0.0}% raggiunto (equity {1:0.00}): chiuso tutto, strategia ferma", Obiettivo, eq));
				return false;
			}
			if (gsFermo) return false;
			if ((StopGiorno > 0 && gsRif > 0 && eq <= gsRif * (1 - StopGiorno / 100)) || (StopGiornoDollari > 0 && gsRif > 0 && eq <= gsRif - StopGiornoDollari))
			{
				gsFermo = true; ChiudiTutto();
				Pr(string.Format("GUARDIANO: perdita del giorno oltre il limite ({0:0.0}% / {1:0} $) (equity {2:0.00}, inizio {3:0.00}): chiuso tutto, fermo fino a domani", StopGiorno, StopGiornoDollari, eq, gsRif));
				return false;
			}
			return true;
		}
		private void ChiudiTutto()
		{
			foreach (Gamba x in gambe) if (!x.finita) Chiudi(x);
			SrChiudi();
		}

		// ------------------------------------------------------------------ eventi
		protected override void OnBarUpdate()
		{
			int b = BarsInProgress;
			if (CurrentBars[b] < 1) return;
			DateTime adesso = Utc(Times[b][0]);
			bool ok = true;
			if (adesso > gsUltimo || State == State.Realtime) { gsUltimo = adesso; ok = Guardiano(adesso); }
			else ok = !gsFermo && !gsFinito;
			if (b == serieOro && Backtest && State != State.Realtime) { if (ok) SrGestisci(adesso); return; }
			if (b == 0 || b == serieOro) return;
			for (int i = 0; i < 8; i++)
				if (regole[i].serie == b) Processa(regole[i], b, ok);
		}

		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (State != State.Realtime || serieOro < 0 || e.MarketDataType != MarketDataType.Last) return;
			if (e.Instrument.FullName != BarsArray[serieOro].Instrument.FullName) return;
			DateTime adesso = DateTime.UtcNow;
			if ((adesso - srUltimo).TotalMilliseconds < Math.Max(100, NewsAggiornaMs)) return;
			srUltimo = adesso;
			if (Guardiano(adesso)) SrGestisci(adesso);
		}

		// ------------------------------------------------------------------ regole intraday (stessa logica di IP_Processa MT5)
		private void Processa(Regola r, int idx, bool ok)
		{
			bool ny = !LON[r.n - 1]; int tipo = TIPO[r.n - 1];
			int inizio = ny ? 9 * 60 + 30 : 8 * 60, fine = ny ? 16 * 60 : 16 * 60 + 30;
			int N = tipo == 1 ? 30 : tipo == 2 ? 15 : tipo == 3 ? 60 : tipo == 5 ? 30 : 5;
			DateTime t = Ora(Times[idx][0], ny);                    // fine della candela chiusa = inizio della candela dopo (come MT5)
			if (t.DayOfWeek == DayOfWeek.Saturday || t.DayOfWeek == DayOfWeek.Sunday) return;
			int m = t.Hour * 60 + t.Minute;
			if (t.Date != r.giorno)
			{
				if (r.hs > 0) { r.rng.Add(r.hs - r.ls); if (r.rng.Count > 40) r.rng.RemoveAt(0); }
				int n = r.rng.Count; double media = 0; int k0 = Math.Max(0, n - 11);
				for (int k = k0; k < n - 1; k++) media += r.rng[k];
				r.stretta = n >= 11 && r.rng[n - 1] < 0.7 * media / (n - 1 - k0);
				r.giorno = t.Date; r.fatto = false; r.rott = 0; r.rh = 0; r.rl = 0; r.hs = 0; r.ls = 0;
			}
			if (m >= fine) { foreach (Gamba x in gambe) if (!x.finita && !x.sr && x.nome.StartsWith("IP" + r.n + "_")) Chiudi(x); return; }
			if (m > inizio)
			{
				double hh = Highs[idx][0], ll = Lows[idx][0];
				r.hs = r.hs == 0 ? hh : Math.Max(r.hs, hh); r.ls = r.ls == 0 ? ll : Math.Min(r.ls, ll);
			}
			if (m < inizio + N || !r.on) return;
			int nb = (m - inizio) / 5;
			if (CurrentBars[idx] < nb) return;
			double[] o = new double[nb], h = new double[nb], l = new double[nb], c = new double[nb];
			for (int j = 0; j < nb; j++) { int a = nb - 1 - j; o[j] = Opens[idx][a]; h[j] = Highs[idx][a]; l[j] = Lows[idx][a]; c[j] = Closes[idx][a]; }
			int kk = N / 5;
			if (r.rh == 0)
			{
				r.rh = h[0]; r.rl = l[0];
				for (int j = 1; j < kk; j++) { r.rh = Math.Max(r.rh, h[j]); r.rl = Math.Min(r.rl, l[j]); }
			}
			if (r.fatto) return;
			double ultima = c[nb - 1];
			if (tipo == 5)
			{
				if (!r.stretta) { r.fatto = true; return; }
				if (ultima > r.rh) Entra(r, idx, 1, r.rl, ok); else if (ultima < r.rl) Entra(r, idx, -1, r.rh, ok);
				return;
			}
			if (tipo == 3)
			{
				if (nb == kk) { int lato = c[kk - 1] > o[0] ? 1 : -1; Entra(r, idx, lato, lato > 0 ? r.rl : r.rh, ok); }
				return;
			}
			if (r.rott == 0)
			{
				if (ultima > r.rh) { r.rott = 1; r.est = h[nb - 1]; }
				else if (ultima < r.rl) { r.rott = -1; r.est = l[nb - 1]; }
				return;
			}
			r.est = r.rott > 0 ? Math.Max(r.est, h[nb - 1]) : Math.Min(r.est, l[nb - 1]);
			if ((r.rott > 0 && ultima < r.rh) || (r.rott < 0 && ultima > r.rl))
			{
				double tk = Instruments[idx].MasterInstrument.TickSize;
				Entra(r, idx, -r.rott, r.rott > 0 ? r.est + tk : r.est, ok);
			}
		}

		private double Ask(int idx) { double a = State == State.Realtime ? GetCurrentAsk(idx) : 0; return a > 0 ? a : Closes[idx][0]; }
		private double Bid(int idx) { double a = State == State.Realtime ? GetCurrentBid(idx) : 0; return a > 0 ? a : Closes[idx][0]; }

		private void Entra(Regola r, int idx, int lato, double stop, bool ok)
		{
			r.fatto = true;
			if (!Operativo() || !ok) return;
			MasterInstrument mi = Instruments[idx].MasterInstrument;
			double px = lato > 0 ? Ask(idx) : Bid(idx);
			stop = mi.RoundToTickSize(stop);
			if ((lato > 0 && stop >= px) || (lato < 0 && stop <= px)) return;
			double mcR = 1.0;
			if (UsaCuscinetto && State == State.Realtime) { string ic; mcR = NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Moltiplicatore(Account, out ic); Print(string.Format("Regola {0} {1}: {2}", r.n, r.strum, ic)); }   // 19/11 cuscinetto
			double grezzo = r.rischio * mcR / 100.0 * Equity() / (Math.Abs(px - stop) * mi.PointValue);
			int q = (int)Math.Floor(grezzo + 1e-9);
			if (q < 1) q = (MinimoSempre || grezzo >= 0.5) ? 1 : 0;
			if (q < 1) { Print(string.Format("Regola {0} {1}: rischio troppo piccolo per 1 contratto, salto", r.n, r.strum)); return; }
			q = Tetto(idx, q);
			if (q < 1) { Print(string.Format("Regola {0} {1}: tetto di {2} micro raggiunto, salto", r.n, r.strum, MaxMicro)); return; }
			Gamba x = new Gamba();
			x.nome = "IP" + r.n + "_" + Times[idx][0].ToString("yyyyMMddHHmm"); x.idx = idx; x.lato = lato; x.stop = stop;
			gambe.Add(x);
			x.entrata = SubmitOrderUnmanaged(idx, lato > 0 ? OrderAction.Buy : OrderAction.SellShort, OrderType.Market, q, 0, 0, "", x.nome);
			Pr(string.Format("{0} Regola {1} {2}: {3} {4} contratti, stop {5}", Times[idx][0], r.n, r.strum, lato > 0 ? "BUY" : "SELL", q, stop));
		}

		// tetto contratti della prop (micro = 1, mini = 10): conta posizioni aperte e ingressi in attesa
		private int Peso(int idx) { string n = Instruments[idx].MasterInstrument.Name; return n.StartsWith("M") ? 1 : 10; }
		private int Aperti()
		{
			int tot = 0; HashSet<string> visti = new HashSet<string>();
			for (int i = 0; i < BarsArray.Length; i++)
			{
				if (!visti.Add(BarsArray[i].Instrument.FullName) || CurrentBars[i] < 0) continue;
				if (Positions[i].MarketPosition != MarketPosition.Flat) tot += Positions[i].Quantity * Peso(i);
			}
			foreach (Gamba x in gambe) if (!x.finita && Attivo(x.entrata) && x.entrata.OrderState != OrderState.Filled) tot += (x.entrata.Quantity - x.qty) * Peso(x.idx);
			if (srPos == 0 && serieOro >= 0 && (Attivo(srBuy) || Attivo(srSell))) tot += srQ * Peso(serieOro);
			return tot;
		}
		private int Tetto(int idx, int q)
		{
			if (MaxMicro <= 0) return q;
			int libero = (MaxMicro - Aperti()) / Peso(idx);
			return Math.Min(q, Math.Max(0, libero));
		}

		private void Chiudi(Gamba x)
		{
			if (x.finita || x.chiudi) return;
			x.chiudi = true;
			if (Attivo(x.entrata) && x.entrata.OrderState != OrderState.Filled) CancelOrder(x.entrata);
			if (Attivo(x.ordStop)) { CancelOrder(x.ordStop); return; }    // esce a mercato quando lo stop e' cancellato
			Esci(x);
		}
		private void Esci(Gamba x)
		{
			if (x.qty <= 0) { if (!Attivo(x.entrata)) x.finita = true; return; }
			if (Attivo(x.uscita)) return;
			x.uscita = SubmitOrderUnmanaged(x.idx, x.lato > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.Market, x.qty, 0, 0, "", x.nome + "_X");
		}
		private static bool Attivo(Order o)
		{
			return o != null && o.OrderState != OrderState.Filled && o.OrderState != OrderState.Cancelled && o.OrderState != OrderState.Rejected && o.OrderState != OrderState.Unknown;
		}
		private Gamba Trova(string nome)
		{
			foreach (Gamba x in gambe) if (nome == x.nome || nome == x.nome + "_S" || nome == x.nome + "_X") return x;
			return null;
		}

		protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity, int filled, double averageFillPrice,
			OrderState orderState, DateTime time, ErrorCode error, string comment)
		{
			if (order.Name.StartsWith("SR")) { SrOrdine(order); return; }
			Gamba x = Trova(order.Name);
			if (x == null) return;
			if (order.Name == x.nome) x.entrata = order; else if (order.Name == x.nome + "_S") x.ordStop = order; else x.uscita = order;
			if (orderState == OrderState.Rejected)
				Pr(string.Format("{0}: ordine {1} RIFIUTATO ({2} {3})", time, order.Name, error, comment));
			if (order == x.ordStop && (orderState == OrderState.Cancelled || orderState == OrderState.Rejected) && x.qty > 0)
			{
				if (orderState == OrderState.Rejected) x.chiudi = true;         // stop rifiutato (prezzo gia' oltre): esce subito
				if (x.chiudi) Esci(x);
			}
			if (order == x.entrata && (orderState == OrderState.Cancelled || orderState == OrderState.Rejected) && x.qty == 0) x.finita = true;
		}

		protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time)
		{
			Order o = execution.Order;
			if (o == null) return;
			Evento(string.Format("ESEGUITO {0} {1} {2} a {3} | equity {4:0}", o.Name, o.OrderAction, quantity, price, Equity()));
			if (o.Name.StartsWith("SR")) { SrEseguito(o, quantity); return; }
			Gamba x = Trova(o.Name);
			if (x == null) return;
			if (o.Name == x.nome)
			{
				x.qty += quantity;
				if (x.chiudi) { Esci(x); return; }
				if ((x.lato > 0 && price <= x.stop) || (x.lato < 0 && price >= x.stop)) { x.chiudi = true; Esci(x); return; }
				if (x.ordStop == null)
					x.ordStop = SubmitOrderUnmanaged(x.idx, x.lato > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.StopMarket, x.qty, 0, x.stop, "", x.nome + "_S");
				else if (Attivo(x.ordStop)) ChangeOrder(x.ordStop, x.qty, 0, x.stop);
			}
			else
			{
				x.qty -= quantity;
				if (x.qty <= 0)
				{
					x.qty = 0; x.finita = true;
					if (Attivo(x.ordStop)) CancelOrder(x.ordStop);
					if (Attivo(x.uscita)) CancelOrder(x.uscita);
				}
			}
		}

		// ------------------------------------------------------------------ news oro: stop-and-reverse (come StopReverse MT5)
		private bool InFinestra(DateTime u)
		{
			foreach (DateTime n in newsUtc) if (u >= n && u < n.AddMinutes(1)) return true;
			return false;
		}
		private void SrGestisci(DateTime adessoUtc)
		{
			if (!UsaNews || serieOro < 0 || !Operativo()) return;
			if (!InFinestra(adessoUtc)) { if (srPos != 0 || Attivo(srBuy) || Attivo(srSell) || Attivo(srRev)) SrChiudi(); return; }
			int g = serieOro; MasterInstrument mi = Instruments[g].MasterInstrument;
			double ask = Ask(g), bid = Bid(g);
			if (ask <= 0 || bid <= 0) return;
			double dist = mi.RoundToTickSize(5.0 * bid / 4100.0), passo = Math.Max(mi.TickSize, 1.0 * bid / 4100.0);
			if (srPos == 0 && !Attivo(srBuy) && !Attivo(srSell) && !Attivo(srRev))
			{
				double eq = Equity(), scala = (gsPart > 0) ? eq / gsPart : 1.0;
				if (UsaCuscinetto && State == State.Realtime) { string ic; scala *= NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Moltiplicatore(Account, out ic); Print("News: " + ic); }   // 19/11 cuscinetto
				srQ = Math.Max(1, (int)Math.Floor(NewsOnce * 4100.0 / bid / mi.PointValue * scala + 1e-9));
				if (MaxMicro > 0) srQ = Math.Min(srQ, Math.Max(1, MaxMicro / (2 * Peso(g))));      // l'inversione usa il doppio
				if (srUltimaEsec > DateTime.MinValue && (adessoUtc - srUltimaEsec).TotalSeconds < 1) return;
				srConta++;
				string oco = "SROCO" + srConta + "_" + adessoUtc.Ticks;
				srBuy = SubmitOrderUnmanaged(g, OrderAction.Buy, OrderType.StopMarket, srQ, 0, mi.RoundToTickSize(ask + dist), oco, "SRB" + srConta);
				srSell = SubmitOrderUnmanaged(g, OrderAction.SellShort, OrderType.StopMarket, srQ, 0, mi.RoundToTickSize(bid - dist), oco, "SRS" + srConta);
				Pr(string.Format("{0} News oro: coppia stop {1} contratti a +/-{2}", adessoUtc, srQ, dist));
				return;
			}
			if (srPos == 0)
			{
				if (Attivo(srBuy) && srBuy.OrderState == OrderState.Working)
				{ double np = mi.RoundToTickSize(ask + dist); if (np <= srBuy.StopPrice - passo) ChangeOrder(srBuy, srBuy.Quantity, 0, np); }
				if (Attivo(srSell) && srSell.OrderState == OrderState.Working)
				{ double np = mi.RoundToTickSize(bid - dist); if (np >= srSell.StopPrice + passo) ChangeOrder(srSell, srSell.Quantity, 0, np); }
				return;
			}
			// posizione aperta: un solo stop opposto per Q + posizione (inversione), che segue il prezzo
			bool vendi = srPos > 0;
			int qRev = Math.Abs(srPos) + srQ;
			if (Attivo(srRev))
			{
				bool giusto = (srRev.OrderAction == OrderAction.SellShort) == vendi;
				if (!giusto) { CancelOrder(srRev); return; }
				if (srRev.OrderState != OrderState.Working) return;
				double np = vendi ? mi.RoundToTickSize(bid - dist) : mi.RoundToTickSize(ask + dist);
				if (vendi ? np >= srRev.StopPrice + passo : np <= srRev.StopPrice - passo) ChangeOrder(srRev, qRev, 0, np);
				return;
			}
			if ((adessoUtc - srUltimaEsec).TotalSeconds < NewsAttesaInversione) return;     // come MT5: l'inversione si piazza dopo qualche secondo
			srConta++;
			srRev = SubmitOrderUnmanaged(g, vendi ? OrderAction.SellShort : OrderAction.Buy, OrderType.StopMarket, qRev, 0,
				vendi ? mi.RoundToTickSize(bid - dist) : mi.RoundToTickSize(ask + dist), "", "SRR" + srConta);
		}
		private void SrChiudi()
		{
			if (Attivo(srBuy)) CancelOrder(srBuy);
			if (Attivo(srSell)) CancelOrder(srSell);
			if (Attivo(srRev)) CancelOrder(srRev);
			if (srPos != 0 && !Attivo(srEsci) && serieOro >= 0)
			{
				srConta++;
				srEsci = SubmitOrderUnmanaged(serieOro, srPos > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.Market, Math.Abs(srPos), 0, 0, "", "SRX" + srConta);
			}
		}
		private void SrOrdine(Order o)
		{
			if (o.Name.StartsWith("SRB")) srBuy = o; else if (o.Name.StartsWith("SRS")) srSell = o; else if (o.Name.StartsWith("SRR")) srRev = o; else if (o.Name.StartsWith("SRX")) srEsci = o;
			if (o.OrderState == OrderState.Rejected) Pr("News oro: ordine " + o.Name + " RIFIUTATO");
		}
		private void SrEseguito(Order o, int q)
		{
			bool compra = o.OrderAction == OrderAction.Buy || o.OrderAction == OrderAction.BuyToCover;
			srPos += compra ? q : -q;
			srUltimaEsec = State == State.Realtime ? DateTime.UtcNow : Utc(Times[serieOro][0]);
		}

		#region Properties
		[NinjaScriptProperty][Display(Name = "Usa cuscinetto (rischio x cuscinetto/1000, min 35%)", Description = "19/11 soci: rischio proporzionale ai soldi che mancano al limite di perdita FundedNext (saldo max fine giornata - 1000). Stato in cuscinetto_stato.txt", Order = 20, GroupName = "1 Generale")]
		public bool UsaCuscinetto { get; set; }
		[NinjaScriptProperty][Display(Name = "Nome del set", Order = 0, GroupName = "1 Generale")]
		public string Insieme { get; set; }
		[NinjaScriptProperty][Display(Name = "Backtest (SOLO Strategy Analyzer)", Order = 1, GroupName = "1 Generale")]
		public bool Backtest { get; set; }
		[NinjaScriptProperty][Range(100, 10000000)][Display(Name = "Capitale del backtest", Order = 2, GroupName = "1 Generale")]
		public double CapitaleTest { get; set; }
		[NinjaScriptProperty][Range(0, 10000000)][Display(Name = "Conto virtuale $ (0 = usa il conto vero)", Description = "Su un demo da 50.000 metti 25000 per lavorare come sul Rapid Daily 25k. Sul conto FundedNext vero: 0", Order = 3, GroupName = "1 Generale")]
		public double ContoVirtuale { get; set; }

		[NinjaScriptProperty][Range(0, 10)][Display(Name = "Rischio % gruppo A", Order = 0, GroupName = "2 Intraday")]
		public double RischioA { get; set; }
		[NinjaScriptProperty][Range(0, 10)][Display(Name = "Rischio % gruppo B", Order = 1, GroupName = "2 Intraday")]
		public double RischioB { get; set; }
		[NinjaScriptProperty][Range(0, 10)][Display(Name = "Rischio % gruppo C", Order = 2, GroupName = "2 Intraday")]
		public double RischioC { get; set; }
		[NinjaScriptProperty][Display(Name = "Regole gruppo A", Order = 3, GroupName = "2 Intraday")]
		public string AttiveA { get; set; }
		[NinjaScriptProperty][Display(Name = "Regole gruppo B", Order = 4, GroupName = "2 Intraday")]
		public string AttiveB { get; set; }
		[NinjaScriptProperty][Display(Name = "Regole gruppo C", Order = 5, GroupName = "2 Intraday")]
		public string AttiveC { get; set; }
		[NinjaScriptProperty][Display(Name = "Contratti regole 1..8 (vuoto = spenta)", Description = "1 GER40, 2 BTC, 3 NAS100 prima ora, 4 oro fade, 5 ETH, 6 SP500, 7 NAS100, 8 petrolio", Order = 6, GroupName = "2 Intraday")]
		public string Strumenti { get; set; }
		[NinjaScriptProperty][Display(Name = "Sotto 1 contratto apri comunque 1", Order = 7, GroupName = "2 Intraday")]
		public bool MinimoSempre { get; set; }

		[NinjaScriptProperty][Display(Name = "News oro attive", Order = 0, GroupName = "3 News oro")]
		public bool UsaNews { get; set; }
		[NinjaScriptProperty][Display(Name = "Contratto oro news", Order = 1, GroupName = "3 News oro")]
		public string OroNews { get; set; }
		[NinjaScriptProperty][Range(1, 100000)][Display(Name = "Once d'oro (a 4100 $, al saldo di partenza)", Description = "MT5 SR_Lotti 0,60 = 60 once = 6 MGC", Order = 2, GroupName = "3 News oro")]
		public double NewsOnce { get; set; }
		[NinjaScriptProperty][Display(Name = "Tipi news (1 NFP, 2 CPI, 4 FOMC)", Order = 3, GroupName = "3 News oro")]
		public string NewsTipi { get; set; }

		[NinjaScriptProperty][Range(100, 10000)][Display(Name = "News: aggiorna ordini ogni (ms)", Description = "1000 = come MT5; piu' veloce perde sui tick veri del future", Order = 4, GroupName = "3 News oro")]
		public int NewsAggiornaMs { get; set; }
		[NinjaScriptProperty][Range(0, 30)][Display(Name = "News: secondi prima di piazzare l'inversione", Order = 5, GroupName = "3 News oro")]
		public int NewsAttesaInversione { get; set; }

		[NinjaScriptProperty][Range(0, 100)][Display(Name = "Stop giorno % (0 = spento)", Order = 0, GroupName = "4 Guardiano")]
		public double StopGiorno { get; set; }
		[NinjaScriptProperty][Range(0, 1000000)][Display(Name = "Stop giorno in $ (0 = spento)", Description = "Rapid Daily 25k: limite prop 500 $, qui 400 per margine", Order = 3, GroupName = "4 Guardiano")]
		public double StopGiornoDollari { get; set; }
		[NinjaScriptProperty][Range(0, 1000)][Display(Name = "Massimo contratti micro aperti (0 = nessun tetto)", Description = "Rapid Daily 25k: 20 micro (1 mini = 10 micro)", Order = 4, GroupName = "4 Guardiano")]
		public int MaxMicro { get; set; }
		[NinjaScriptProperty][Range(0, 1000)][Display(Name = "Obiettivo % (0 = spento)", Order = 1, GroupName = "4 Guardiano")]
		public double Obiettivo { get; set; }
		[NinjaScriptProperty][Range(0, 100000000)][Display(Name = "Saldo di partenza (0 = all'avvio)", Order = 2, GroupName = "4 Guardiano")]
		public double SaldoPartenza { get; set; }
		#endregion
	}
}
