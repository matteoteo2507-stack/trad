// OroOrderFlowNT - Motore Profitto (11/11/2026). Versione che APRE ORDINI dell'indicatore SegnaliOroOF (stesse regole).
// Da mettere su GC (oro grande) 5 minuti, Tick Replay ACCESO, almeno 15 giorni caricati. Gli ordini vanno su MGC (oro micro).
//  GROSSI: tra 08:20 e 13:30 di New York, candela 5m in cui gli scambi grossi (>= SogliaContratti) netti sono oltre SogliaZ
//          deviazioni e nello stesso verso della candela (pausa PausaMinuti tra due segnali). Entrata a mercato all'apertura della
//          candela dopo, stop oltre l'estremo opposto della candela, target 2R; se non tocca nulla esce alle 13:30 NY.
//  FADE:   range della candela 09:30-09:35 NY; una candela chiude fuori, poi una chiude di nuovo dentro -> entrata contro la
//          rottura SOLO se il delta cumulato dalle 09:30 e' nel verso del trade. Stop oltre l'estremo, uscita alle 16:00 NY.
// Rischio: Rischio% dell'equity (o del ContoVirtuale) per trade, contratti MGC interi (sotto 1: 1 se almeno 0,5, altrimenti salta).
// Guardiano: perdita del giorno oltre StopGiornoDollari (equity del conto, dalla mezzanotte di Atene) -> chiude e si ferma fino a domani.
// 18/11 (decisione soci): filtro POC 'almeno uno' = GROSSI entra se va verso il POC di ieri OPPURE verso il POC di oggi
//        (profilo 08:20 NY fino al segnale, tick veri); salta solo se va via da entrambi. FADE: stop minimo 5 punti.
// 20/11 (test: FADE dopo un giorno molto agitato -0,53R in entrambe le meta', 16/16 varianti): FILTRO VOLATILITA' = salta la FADE se il range
//        di ieri (08:20-13:30 NY, in % del prezzo) e' nel terzo piu' alto degli ultimi 120 giorni di borsa. Range calcolati dallo storico 5m.
// Tetto: MaxMicro contratti aperti da questa strategia. Lo storico serve solo a calcolare le statistiche: ordini SOLO in tempo reale.
// Ogni trade viene scritto anche in Documenti\NinjaTrader 8\segnali_oro_of.csv (come l'indicatore).
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
	public class OroOrderFlowNT : Strategy
	{
		private class Trade
		{
			public string nome; public int lato, qty, chiesti, entrati; public double stop, target, sommaEnt, pnl; public DateTime fineNy;
			public bool eAggiunta, aggiuntaFatta;     // 12/11: aggiunta a +1R (seconda posizione con stop all'entrata del trade iniziale)
			public Order ent, st, tg, ex; public bool chiudi, finito, contato;
			public DateTime segnale = DateTime.MinValue;   // 13/11: fine della candela del segnale (per misurare il ritardo)
		}
		// 12/11: protezione perdite (prova Rapid Daily): dopo DimezzaDopo perdite di fila rischia Rischio x FattoreRidotto finche' non vince;
		// al massimo MaxPerditeGiorno perdite al giorno (giorno di New York). Stato salvato in Documenti\NinjaTrader 8\of_stato.txt
		private int perseFila, perseOggi; private DateTime giornoPerse = DateTime.MinValue;
		// 12/11: filtro POC. Profilo volume della sessione 08:20-13:30 NY (come i test); GROSSI solo se va VERSO il POC di ieri.
		private readonly SortedDictionary<long, double> profilo = new SortedDictionary<long, double>();
		private DateTime giornoProf = DateTime.MinValue, barIniNy = DateTime.MinValue; private double pocIeri;

		private double ultimoAsk, ultimoBid, ultimoPrezzo, volPrecedente;
		private int ultimoLato = 1;
		private double buy, sell, gbuy, gsell;
		private readonly List<double> storiaG = new List<double>();
		private DateTime ultimoGrossi = DateTime.MinValue, giornoFade = DateTime.MinValue;
		private double fHi, fLo, fEst, cumDelta;
		private int fRott, conta;
		private bool fRange, fFatto;
		private TimeZoneInfo ny, ate;
		// 20/11 filtro volatilita' FADE
		private volatile bool volAgitato = false, volPronto = false; private volatile string volInfo = "non ancora calcolata"; private DateTime volGiorno = DateTime.MinValue; private BarsRequest volReq;
		private readonly List<Trade> trades = new List<Trade>();
		private const int IDX = 1;                     // serie degli ordini (MGC)
		private double virtBase = -1;
		private DateTime gsGiorno = DateTime.MinValue; private double gsRif; private bool gsFermo;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "OroOrderFlowNT";
				Description = "Order flow oro (scambi grossi + fade 09:30 con delta): calcola su GC con Tick Replay, opera su MGC.";
				Calculate = Calculate.OnEachTick;
				IsUnmanaged = true;
				IsExitOnSessionCloseStrategy = false;
				BarsRequiredToTrade = 0;
				StartBehavior = StartBehavior.ImmediatelySubmit;
				SogliaContratti = 15; PausaMinuti = 30; SogliaZ = 2.5; Finestra = 600;
				ContrattoOrdini = "MGC 12-26";
				Rischio = 1.5; MaxMicro = 15; StopGiornoDollari = 400; ContoVirtuale = 0; FiltroPOC = true; PocAncheOggi = true; FadeStopMinimo = 5.0;
				UsaAggiunta = true; AggiuntaR = 1.0; AggiuntaFrazione = 0.5; MaxIniziale = 10;
				FiltroVolatilita = true; VolSoglia = 0.667; VolGiorni = 120;
				UsaGrossi = true; UsaFade = true; MaxRitardoSecondi = 0; UsaCuscinetto = true;   // 13/11: blocco spento (anche in ritardo i trade restano positivi), resta solo la misura del ritardo
				DimezzaDopo = 2; FattoreRidotto = 0.5; MaxPerditeGiorno = 2;
			}
			else if (State == State.Configure)
			{
				AddDataSeries(ContrattoOrdini.Trim(), BarsPeriodType.Minute, 1);
			}
			else if (State == State.DataLoaded)
			{
				ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
				ate = TimeZoneInfo.FindSystemTimeZoneById("GTB Standard Time");
			}
			else if (State == State.Realtime)
			{
				virtBase = Reale();
				LeggiStato();
				Print(string.Format("OroOrderFlowNT avviato: rischio {0}% a trade, max {1} micro, stop giorno {2} $, conto virtuale {3} (vero {4:0.00}), storia {5} candele",
					Rischio, MaxMicro, StopGiornoDollari, ContoVirtuale, virtBase, storiaG.Count));
				Print(string.Format(CultureInfo.InvariantCulture, "OroOrderFlowNT filtro POC: {0} | POC di ieri {1}", FiltroPOC ? "ACCESO (GROSSI solo verso il POC di ieri)" : "spento", pocIeri > 0 ? pocIeri.ToString(CultureInfo.InvariantCulture) : "non ancora calcolato"));
				Print(string.Format(CultureInfo.InvariantCulture, "OroOrderFlowNT aggiunta: {0} | trade iniziale max {1} MGC, totale max {2} MGC",
					UsaAggiunta ? string.Format(CultureInfo.InvariantCulture, "ACCESA (a +{0}R aggiunge {1} dei contratti, stop all'entrata)", AggiuntaR, AggiuntaFrazione) : "spenta", MaxIniziale, MaxMicro));
				Print(string.Format("OroOrderFlowNT protezione: dopo {0} perdite di fila rischio x{1} ({2}%), max {3} perdite al giorno (0 = spento). Ora: {4} perdite di fila, {5} oggi",
					DimezzaDopo, FattoreRidotto, Rischio * FattoreRidotto, MaxPerditeGiorno, perseFila, perseOggi));
				Print("OroOrderFlowNT protezione: conta anche le perdite di fila di SPINTA (ora " + FilaSpinta() + ")");
				if (UsaCuscinetto) { string ic; NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Moltiplicatore(Account, out ic); Print("OroOrderFlowNT CUSCINETTO acceso: " + ic); } else Print("OroOrderFlowNT cuscinetto: spento");
				if (FiltroVolatilita) CalcolaVolatilita(); else Print("OroOrderFlowNT filtro volatilita' FADE: spento");
			}
			else if (State == State.Terminated) { if (volReq != null) { try { volReq.Dispose(); } catch { } volReq = null; } }
		}


		// 12/11: registro eventi per gli avvisi Telegram (solo scrittura su file, nessun effetto sul trading)
		private void Evento(string s)
		{
			if (State != State.Realtime) return;
			for (int t = 0; t < 3; t++)
				try { File.AppendAllText(Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "eventi_bot.txt"), DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "|" + Name + "|" + s.Replace(Environment.NewLine, " ") + Environment.NewLine); return; }
				catch { System.Threading.Thread.Sleep(20); }
		}
		private void Pr(string s) { Print(s); Evento(s); }

		// ------------------------------------------------------------------ conto
		private double Reale()
		{
			if (Account == null) return 0;
			double nl = Account.Get(AccountItem.NetLiquidation, Currency.UsDollar);
			if (nl > 0) return nl;
			return Account.Get(AccountItem.CashValue, Currency.UsDollar);
		}
		private double Equity()
		{
			double r = Reale();
			if (ContoVirtuale > 0 && virtBase > 0) return ContoVirtuale + (r - virtBase);
			return r;
		}
		private bool Guardiano()
		{
			if (State != State.Realtime) return false;
			DateTime g = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, ate).Date;
			double eq = Equity();
			if (g != gsGiorno) { gsGiorno = g; gsRif = eq; if (gsFermo) Print("OroOrderFlowNT: nuovo giorno, si riparte"); gsFermo = false; }
			if (gsFermo) return false;
			if (StopGiornoDollari > 0 && eq <= gsRif - StopGiornoDollari)
			{
				gsFermo = true;
				foreach (Trade t in trades) if (!t.finito) Chiudi(t);
				Pr(string.Format("OroOrderFlowNT GUARDIANO: perdita del giorno oltre {0} $ (equity {1:0.00}, inizio {2:0.00}): chiuso, fermo fino a domani", StopGiornoDollari, eq, gsRif));
				return false;
			}
			return true;
		}
		private int Aperti()
		{
			int n = 0;
			foreach (Trade t in trades) if (!t.finito) n += Math.Max(t.qty, t.chiesti - 0);
			return n;
		}

		// ------------------------------------------------------------------ dati
		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.Instrument.FullName != Instrument.FullName) return;
			if (e.MarketDataType == MarketDataType.Last)
			{
				if (e.Ask > e.Bid && e.Bid > 0) { ultimoAsk = e.Ask; ultimoBid = e.Bid; }
			}
			else if (e.MarketDataType == MarketDataType.Ask) ultimoAsk = e.Price;
			else if (e.MarketDataType == MarketDataType.Bid) ultimoBid = e.Price;
		}

		protected override void OnBarUpdate()
		{
			if (BarsInProgress == IDX)
			{
				if (State == State.Realtime) { UsciteATempo(); ControllaAggiunte(); if (UsaCuscinetto) NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Aggiorna(Account); }
				return;
			}
			if (CurrentBars[0] == 0 && !Bars.IsTickReplay)
				Draw.TextFixed(this, "ofAvviso", "OroOrderFlowNT: accendi Tick Replay sul grafico GC (serve il lato di ogni scambio)", TextPosition.TopLeft);
			if (State == State.Historical && !Bars.IsTickReplay) return;

			if (IsFirstTickOfBar)
			{
				if (CurrentBar > 0) BarraChiusa();
				buy = sell = gbuy = gsell = 0; volPrecedente = 0;
				barIniNy = TimeZoneInfo.ConvertTime(Time[0], TimeZoneInfo.Local, ny).AddMinutes(-BarsPeriod.Value);
			}
			double v = Volume[0] - volPrecedente; volPrecedente = Volume[0];
			if (v <= 0) return;
			double p = Close[0]; int lato;
			TimeSpan mp = barIniNy.TimeOfDay;
			if (mp >= new TimeSpan(8, 20, 0) && mp < new TimeSpan(13, 30, 0))
			{
				if (barIniNy.Date != giornoProf)
				{
					if (profilo.Count > 0)
					{
						long best = 0; double bv = -1;
						foreach (KeyValuePair<long, double> kv in profilo) if (kv.Value > bv) { bv = kv.Value; best = kv.Key; }
						pocIeri = best * TickSize;
						if (State == State.Realtime) Print(string.Format(CultureInfo.InvariantCulture, "OroOrderFlowNT: POC di ieri (08:20-13:30 NY) = {0}", pocIeri));
					}
					profilo.Clear(); giornoProf = barIniNy.Date;
				}
				long lv = (long)Math.Round(p / TickSize);
				double cur; profilo.TryGetValue(lv, out cur); profilo[lv] = cur + v;
			}
			if (ultimoAsk > 0 && p >= ultimoAsk) lato = 1;
			else if (ultimoBid > 0 && p <= ultimoBid) lato = -1;
			else lato = p > ultimoPrezzo ? 1 : p < ultimoPrezzo ? -1 : ultimoLato;
			ultimoPrezzo = p; ultimoLato = lato;
			if (lato > 0) { buy += v; if (v >= SogliaContratti) gbuy += v; }
			else { sell += v; if (v >= SogliaContratti) gsell += v; }
		}

		private void BarraChiusa()
		{
			DateTime fineNy = TimeZoneInfo.ConvertTime(Time[1], TimeZoneInfo.Local, ny);
			DateTime inizioNy = fineNy.AddMinutes(-BarsPeriod.Value);
			TimeSpan m = inizioNy.TimeOfDay; DateTime g = inizioNy.Date;
			double delta = buy - sell, gnet = gbuy - gsell;

			if (m >= new TimeSpan(8, 20, 0) && m < new TimeSpan(13, 30, 0))
			{
				if (storiaG.Count >= 200 && (inizioNy - ultimoGrossi).TotalMinutes >= PausaMinuti)
				{
					double media = 0; foreach (double x in storiaG) media += x; media /= storiaG.Count;
					double var = 0; foreach (double x in storiaG) var += (x - media) * (x - media);
					double sd = Math.Sqrt(var / (storiaG.Count - 1));
					int dir = Math.Sign(Close[1] - Open[1]);
					if (sd > 0 && dir != 0)
					{
						double z = gnet / sd;
						if (Math.Abs(z) > SogliaZ && Math.Sign(z) == dir)
						{
							ultimoGrossi = inizioNy;
							double stop = dir > 0 ? Low[1] - TickSize : High[1] + TickSize;
							if (UsaGrossi) Apri("GROSSI", dir, stop, 2.0, g.Add(new TimeSpan(13, 30, 0)), string.Format(CultureInfo.InvariantCulture, "z {0:0.0}", z));
						}
					}
				}
				storiaG.Add(gnet);
				if (storiaG.Count > Finestra) storiaG.RemoveAt(0);
			}

			if (g != giornoFade) { giornoFade = g; fRange = false; fFatto = false; fRott = 0; cumDelta = 0; if (State == State.Realtime && FiltroVolatilita) CalcolaVolatilita(); }
			if (m >= new TimeSpan(9, 30, 0) && m < new TimeSpan(16, 0, 0))
			{
				cumDelta += delta;
				if (m == new TimeSpan(9, 30, 0)) { fHi = High[1]; fLo = Low[1]; fRange = true; }
				else if (fRange && !fFatto)
				{
					if (fRott == 0)
					{
						if (Close[1] > fHi) { fRott = 1; fEst = High[1]; }
						else if (Close[1] < fLo) { fRott = -1; fEst = Low[1]; }
					}
					else
					{
						fEst = fRott > 0 ? Math.Max(fEst, High[1]) : Math.Min(fEst, Low[1]);
						if ((fRott > 0 && Close[1] < fHi) || (fRott < 0 && Close[1] > fLo))
						{
							fFatto = true; int dir = -fRott;
							if (Math.Sign(cumDelta) == dir && UsaFade && FiltroVolatilita && State == State.Realtime && volAgitato)
								Pr("OroOrderFlowNT FADE: salto per il filtro volatilita' (" + volInfo + ")");
							else if (Math.Sign(cumDelta) == dir && UsaFade)
								Apri("FADE", dir, fRott > 0 ? fEst + TickSize : fEst - TickSize, 0, g.Add(new TimeSpan(16, 0, 0)),
									"delta " + cumDelta.ToString("0", CultureInfo.InvariantCulture));
						}
					}
				}
			}
		}

		// ------------------------------------------------------------------ 20/11 filtro volatilita' FADE
		// Scarica dallo storico le candele 5m dell'oro (stesso strumento del grafico) degli ultimi ~200 giorni, calcola per ogni giorno di New York
		// il range 08:20-13:30 in % della chiusura, e confronta il range dell'ULTIMO giorno finito (ieri) con i VolGiorni giorni prima (ieri compreso).
		private void CalcolaVolatilita()
		{
			DateTime oggiNy = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, ny).Date;
			if (volGiorno == oggiNy && volPronto) return;
			volGiorno = oggiNy; volPronto = false;
			try
			{
				if (volReq != null) { try { volReq.Dispose(); } catch { } }
				volReq = new BarsRequest(Instrument, DateTime.Now.AddDays(-(VolGiorni * 1.6 + 20)), DateTime.Now);
				volReq.BarsPeriod = new BarsPeriod { BarsPeriodType = BarsPeriodType.Minute, Value = 5 };
				volReq.TradingHours = Bars.TradingHours;
				volReq.Request(new Action<BarsRequest, ErrorCode, string>((br, err, msg) =>
				{
					if (err != ErrorCode.NoError) { volInfo = "errore storico: " + msg; Print("OroOrderFlowNT filtro volatilita': " + volInfo + " -> FADE NON filtrata oggi"); return; }
					try { ElaboraVolatilita(br.Bars, oggiNy); } catch (Exception ex) { volInfo = "errore: " + ex.Message; Print("OroOrderFlowNT filtro volatilita': " + volInfo); }
				}));
			}
			catch (Exception ex) { volInfo = "errore: " + ex.Message; Print("OroOrderFlowNT filtro volatilita': " + volInfo); }
		}
		private void ElaboraVolatilita(Bars b, DateTime oggiNy)
		{
			SortedDictionary<DateTime, double[]> gg = new SortedDictionary<DateTime, double[]>();   // giorno NY -> alto, basso, chiusura
			for (int i = 0; i < b.Count; i++)
			{
				DateTime fine = TimeZoneInfo.ConvertTime(b.GetTime(i), TimeZoneInfo.Local, ny);   // ora di CHIUSURA della candela
				TimeSpan m = fine.TimeOfDay;
				if (m <= new TimeSpan(8, 20, 0) || m > new TimeSpan(13, 30, 0)) continue;
				DateTime d = fine.Date; if (d >= oggiNy) continue;
				double[] x;
				if (!gg.TryGetValue(d, out x)) { x = new double[] { b.GetHigh(i), b.GetLow(i), b.GetClose(i), 0 }; gg[d] = x; }
				x[0] = Math.Max(x[0], b.GetHigh(i)); x[1] = Math.Min(x[1], b.GetLow(i)); x[2] = b.GetClose(i); x[3] += 1;
			}
			List<double> r = new List<double>(); DateTime ultimo = DateTime.MinValue;
			foreach (KeyValuePair<DateTime, double[]> kv in gg) if (kv.Value[3] >= 30 && kv.Value[2] > 0) { r.Add((kv.Value[0] - kv.Value[1]) / kv.Value[2] * 100.0); ultimo = kv.Key; }
			if (r.Count > VolGiorni) r.RemoveRange(0, r.Count - VolGiorni);
			if (r.Count < 40) { volAgitato = false; volPronto = true; volInfo = string.Format("solo {0} giorni di storico (servono 40): FADE non filtrata", r.Count); Print("OroOrderFlowNT filtro volatilita': " + volInfo); return; }
			double ieri = r[r.Count - 1]; int sotto = 0;
			for (int k = 0; k < r.Count - 1; k++) if (r[k] < ieri) sotto++;
			double perc = (double)sotto / (r.Count - 1);
			volAgitato = perc >= VolSoglia; volPronto = true;
			volInfo = string.Format(CultureInfo.InvariantCulture, "range di {0:dd/MM} {1:0.00}% = piu' agitato del {2:0}% dei {3} giorni prima (soglia {4:0}%) -> FADE {5}",
				ultimo, ieri, perc * 100, r.Count - 1, VolSoglia * 100, volAgitato ? "SALTA oggi" : "attiva oggi");
			Print("OroOrderFlowNT filtro volatilita': " + volInfo);
		}

		// ------------------------------------------------------------------ ordini
		// 18/11: POC di oggi = livello con piu' volume nel profilo in costruzione (08:20 NY fino ad ora); 0 se non disponibile
		private double PocDiOggi()
		{
			DateTime oggiNy = TimeZoneInfo.ConvertTime(Time[1], TimeZoneInfo.Local, ny).Date;
			if (profilo.Count == 0 || giornoProf != oggiNy) return 0;
			long best = 0; double bv = -1;
			foreach (KeyValuePair<long, double> kv in profilo) if (kv.Value > bv) { bv = kv.Value; best = kv.Key; }
			return best * TickSize;
		}

		private void Apri(string tipo, int dir, double stop, double multR, DateTime fineNy, string nota)
		{
			Brush col = dir > 0 ? Brushes.LimeGreen : Brushes.OrangeRed;
			string tag = "of" + tipo + CurrentBar;
			if (dir > 0) Draw.ArrowUp(this, tag, false, 0, Low[0] - 4 * TickSize, col);
			else Draw.ArrowDown(this, tag, false, 0, High[0] + 4 * TickSize, col);
			if (State != State.Realtime || !Guardiano()) return;
			// 13/11: niente entrate in ritardo (dopo un blocco o una riconnessione il prezzo e' peggiore e il vantaggio si dimezza)
			double ritardo = (DateTime.Now - Time[1]).TotalSeconds;
			if (MaxRitardoSecondi > 0 && ritardo > MaxRitardoSecondi)
			{ Pr(string.Format(CultureInfo.InvariantCulture, "OroOrderFlowNT {0}: segnale in RITARDO di {1:0} s (massimo {2}), salto", tipo, ritardo, MaxRitardoSecondi)); return; }
			nota += string.Format(CultureInfo.InvariantCulture, ", ritardo {0:0.0} s", ritardo);

			MasterInstrument mi = Instruments[IDX].MasterInstrument;
			double px = dir > 0 ? GetCurrentAsk(IDX) : GetCurrentBid(IDX);
			if (px <= 0) px = Closes[IDX][0];
			stop = mi.RoundToTickSize(stop);
			double rischio = (px - stop) * dir;
			if (rischio <= 2 * mi.TickSize) { Print("OroOrderFlowNT " + tipo + ": prezzo gia' oltre lo stop, salto"); return; }
			// 18/11: FADE con stop minimo FadeStopMinimo punti (se lo stop naturale e' piu' vicino lo allarga)
			if (tipo == "FADE" && FadeStopMinimo > 0 && rischio < FadeStopMinimo)
			{
				nota += string.Format(CultureInfo.InvariantCulture, ", stop allargato da {0:0.0} a {1:0.0} punti", rischio, FadeStopMinimo);
				stop = mi.RoundToTickSize(px - dir * FadeStopMinimo); rischio = (px - stop) * dir;
			}
			if (tipo == "GROSSI" && pocIeri > 0)
			{
				bool verso = Math.Sign(pocIeri - px) == dir;
				double pocOggi = PocDiOggi();
				bool versoOggi = PocAncheOggi && pocOggi > 0 && Math.Sign(pocOggi - px) == dir;
				nota += verso ? ", verso il POC di ieri " : ", VIA dal POC di ieri ";
				nota += pocIeri.ToString(CultureInfo.InvariantCulture);
				if (PocAncheOggi) nota += (versoOggi ? ", verso il POC di oggi " : ", via dal POC di oggi ") + pocOggi.ToString(CultureInfo.InvariantCulture);
				if (FiltroPOC && !verso && !versoOggi)
				{
					Pr(string.Format(CultureInfo.InvariantCulture, "OroOrderFlowNT GROSSI: va via dal POC di ieri ({0}){1}, salto (filtro POC)", pocIeri,
						PocAncheOggi ? string.Format(CultureInfo.InvariantCulture, " e da quello di oggi ({0})", pocOggi) : ""));
					return;
				}
				if (FiltroPOC && !verso && versoOggi) Pr(string.Format(CultureInfo.InvariantCulture, "OroOrderFlowNT GROSSI: via dal POC di ieri ({0}) ma verso quello di oggi ({1}): entro", pocIeri, pocOggi));
			}
			AggiornaGiorno();
			if (MaxPerditeGiorno > 0 && perseOggi >= MaxPerditeGiorno) { Pr(string.Format("OroOrderFlowNT {0}: gia' {1} perdite oggi, salto fino a domani", tipo, perseOggi)); return; }
			int spFila = DimezzaDopo > 0 ? FilaSpinta() : 0;   // 20/11 soci: conta anche le perdite di fila di SPINTA (prudente 80->86%, 5 prelievi 80->90%)
			int fila = Math.Max(perseFila, spFila);
			double rischioPct = Rischio * ((DimezzaDopo > 0 && fila >= DimezzaDopo) ? FattoreRidotto : 1.0);
			if (rischioPct < Rischio) Pr(string.Format("OroOrderFlowNT {0}: perdite di fila bot {1}, SPINTA {2} -> rischio ridotto a {3}%", tipo, perseFila, spFila, rischioPct));
			if (UsaCuscinetto) { string ic; double mc = NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Moltiplicatore(Account, out ic); rischioPct *= mc; nota += ", " + ic; }   // 19/11 cuscinetto
			double grezzo = rischioPct / 100.0 * Equity() / (rischio * mi.PointValue);
			int q = (int)Math.Floor(grezzo + 1e-9);
			if (q < 1) q = grezzo >= 0.5 ? 1 : 0;
			q = Math.Min(Math.Min(q, MaxIniziale), MaxMicro - Aperti());
			if (q < 1) { Print(string.Format("OroOrderFlowNT {0}: contratti 0 (rischio {1:0.0} punti, tetto {2}), salto", tipo, rischio, MaxMicro)); return; }

			Trade t = new Trade();
			conta++;
			t.nome = "OF" + tipo.Substring(0, 1) + conta; t.lato = dir; t.chiesti = q; t.stop = stop; t.fineNy = fineNy; t.segnale = Time[1];
			t.target = multR > 0 ? mi.RoundToTickSize(px + multR * rischio * dir) : double.NaN;
			trades.Add(t);
			t.ent = SubmitOrderUnmanaged(IDX, dir > 0 ? OrderAction.Buy : OrderAction.SellShort, OrderType.Market, q, 0, 0, "", t.nome);
			string riga = string.Format(CultureInfo.InvariantCulture, "{0:yyyy-MM-dd HH:mm:ss};{1};{2};{3};{4};{5};{6};ORDINE {7} contratti, {8}",
				Time[0], Instruments[IDX].FullName, tipo, dir > 0 ? "LONG" : "SHORT", px, stop, double.IsNaN(t.target) ? "" : t.target.ToString(CultureInfo.InvariantCulture), q, nota);
			Pr("OroOrderFlowNT " + riga);
			try
			{
				string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "segnali_oro_of.csv");
				if (!File.Exists(f)) File.WriteAllText(f, "ora;strumento;tipo;lato;entrata;stop;target;nota" + Environment.NewLine);
				File.AppendAllText(f, riga + Environment.NewLine);
			}
			catch (Exception ex) { Print("OroOrderFlowNT: errore scrittura " + ex.Message); }
		}

		// 12/11: quando un trade iniziale arriva a +AggiuntaR volte il suo rischio, apre una seconda posizione
		// di AggiuntaFrazione x contratti, stop = prezzo d'entrata del trade iniziale, stesso target e stessa uscita a orario.
		// Il trade iniziale non cambia. Le aggiunte non contano nella protezione perdite (conta solo il trade iniziale).
		private void ControllaAggiunte()
		{
			if (!UsaAggiunta) return;
			double px = Closes[IDX][0];
			if (px <= 0) return;
			List<Trade> nuove = new List<Trade>();
			foreach (Trade p in trades)
			{
				if (p.eAggiunta || p.aggiuntaFatta || p.finito || p.chiudi || p.entrati <= 0 || p.qty <= 0) continue;
				double ent = p.sommaEnt / p.entrati, rk = Math.Abs(ent - p.stop);
				if (rk <= 0 || (px - ent) * p.lato < AggiuntaR * rk) continue;
				p.aggiuntaFatta = true;
				if (!Guardiano()) continue;
				MasterInstrument mi = Instruments[IDX].MasterInstrument;
				int q = (int)Math.Floor(p.entrati * AggiuntaFrazione + 0.5);
				q = Math.Min(q, MaxMicro - Aperti());
				if (q < 1) { Print(string.Format("OroOrderFlowNT {0}: +{1}R raggiunto ma niente spazio per l'aggiunta (tetto {2} micro)", p.nome, AggiuntaR, MaxMicro)); continue; }
				Trade a = new Trade();
				conta++;
				a.nome = "OFP" + conta; a.lato = p.lato; a.chiesti = q; a.stop = mi.RoundToTickSize(ent); a.target = p.target; a.fineNy = p.fineNy;
				a.eAggiunta = true; a.contato = true;
				nuove.Add(a);
				Pr(string.Format(CultureInfo.InvariantCulture, "OroOrderFlowNT {0}: +{1}R raggiunto ({2}), AGGIUNTA {3} contratti, stop all'entrata {4}{5}",
					p.nome, AggiuntaR, px, q, a.stop, double.IsNaN(a.target) ? "" : ", target " + a.target));
			}
			foreach (Trade a in nuove)
			{
				trades.Add(a);
				a.ent = SubmitOrderUnmanaged(IDX, a.lato > 0 ? OrderAction.Buy : OrderAction.SellShort, OrderType.Market, a.chiesti, 0, 0, "", a.nome);
				try
				{
					string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "segnali_oro_of.csv");
					File.AppendAllText(f, string.Format(CultureInfo.InvariantCulture, "{0:yyyy-MM-dd HH:mm:ss};{1};AGGIUNTA;{2};{3};{4};{5};ORDINE {6} contratti", DateTime.Now,
						Instruments[IDX].FullName, a.lato > 0 ? "LONG" : "SHORT", Closes[IDX][0], a.stop, double.IsNaN(a.target) ? "" : a.target.ToString(CultureInfo.InvariantCulture), a.chiesti) + Environment.NewLine);
				}
				catch (Exception ex) { Print("OroOrderFlowNT: errore scrittura " + ex.Message); }
			}
		}

		private void UsciteATempo()
		{
			DateTime adessoNy = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, ny);
			bool ok = Guardiano();
			foreach (Trade t in trades)
				if (!t.finito && !t.chiudi && adessoNy >= t.fineNy) { Pr("OroOrderFlowNT " + t.nome + ": fine tempo, esco"); Chiudi(t); }
		}

		private static bool Attivo(Order o)
		{
			return o != null && o.OrderState != OrderState.Filled && o.OrderState != OrderState.Cancelled && o.OrderState != OrderState.Rejected && o.OrderState != OrderState.Unknown;
		}
		private void Chiudi(Trade t)
		{
			if (t.finito || t.chiudi) return;
			t.chiudi = true;
			if (Attivo(t.ent) && t.ent.OrderState != OrderState.Filled) CancelOrder(t.ent);
			if (Attivo(t.st)) { CancelOrder(t.st); if (Attivo(t.tg)) CancelOrder(t.tg); return; }     // esce a mercato quando lo stop e' cancellato
			Esci(t);
		}
		private void Esci(Trade t)
		{
			if (t.qty <= 0) { if (!Attivo(t.ent)) t.finito = true; return; }
			if (Attivo(t.ex)) return;
			t.ex = SubmitOrderUnmanaged(IDX, t.lato > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.Market, t.qty, 0, 0, "", t.nome + "_X");
		}
		private void AggiornaGiorno()
		{
			DateTime g = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, ny).Date;
			if (g != giornoPerse) { giornoPerse = g; perseOggi = 0; SalvaStato(); }
		}
		private string FileStato() { return Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "of_stato.txt"); }
		// 20/11: perdite di fila di OroSpintaNT (solo lettura di spinta_stato.txt, primo campo); 0 se manca o illeggibile
		private int FilaSpinta()
		{
			try
			{
				string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "spinta_stato.txt");
				if (!File.Exists(f)) return 0;
				return Math.Max(0, int.Parse(File.ReadAllText(f).Trim().Split(';')[0], CultureInfo.InvariantCulture));
			}
			catch { return 0; }
		}
		private void SalvaStato()
		{
			try { File.WriteAllText(FileStato(), string.Format(CultureInfo.InvariantCulture, "{0};{1};{2:yyyy-MM-dd}", perseFila, perseOggi, giornoPerse)); }
			catch (Exception ex) { Print("OroOrderFlowNT: errore salvataggio stato " + ex.Message); }
		}
		private void LeggiStato()
		{
			try
			{
				if (!File.Exists(FileStato())) return;
				string[] p = File.ReadAllText(FileStato()).Trim().Split(';');
				perseFila = int.Parse(p[0]); perseOggi = int.Parse(p[1]);
				giornoPerse = DateTime.ParseExact(p[2], "yyyy-MM-dd", CultureInfo.InvariantCulture);
			}
			catch (Exception ex) { Print("OroOrderFlowNT: errore lettura stato " + ex.Message); }
		}
		private Trade Trova(string nome)
		{
			foreach (Trade t in trades) if (nome == t.nome || nome == t.nome + "_S" || nome == t.nome + "_T" || nome == t.nome + "_X") return t;
			return null;
		}

		protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity, int filled, double averageFillPrice,
			OrderState orderState, DateTime time, ErrorCode error, string comment)
		{
			Trade t = Trova(order.Name);
			if (t == null) return;
			if (order.Name == t.nome) t.ent = order; else if (order.Name == t.nome + "_S") t.st = order; else if (order.Name == t.nome + "_T") t.tg = order; else t.ex = order;
			if (orderState == OrderState.Rejected) Pr(string.Format("OroOrderFlowNT: ordine {0} RIFIUTATO ({1} {2})", order.Name, error, comment));
			if (order == t.st && (orderState == OrderState.Cancelled || orderState == OrderState.Rejected) && t.qty > 0)
			{
				if (orderState == OrderState.Rejected) t.chiudi = true;
				if (t.chiudi) { if (Attivo(t.tg)) CancelOrder(t.tg); Esci(t); }
			}
			if (order == t.ent && (orderState == OrderState.Cancelled || orderState == OrderState.Rejected) && t.qty == 0) t.finito = true;
		}

		protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time)
		{
			Order o = execution.Order;
			if (o == null) return;
			Trade t = Trova(o.Name);
			if (t == null) return;
			if (o.Name == t.nome)
			{
				t.qty += quantity; t.entrati += quantity; t.sommaEnt += price * quantity;
				if (t.chiudi) { Esci(t); return; }
				if ((t.lato > 0 && price <= t.stop) || (t.lato < 0 && price >= t.stop)) { t.chiudi = true; Esci(t); return; }
				string oco = "OCO_" + t.nome + "_" + t.qty;
				if (Attivo(t.st)) { ChangeOrder(t.st, t.qty, 0, t.stop); if (Attivo(t.tg)) ChangeOrder(t.tg, t.qty, t.target, 0); return; }
				t.st = SubmitOrderUnmanaged(IDX, t.lato > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.StopMarket, t.qty, 0, t.stop, double.IsNaN(t.target) ? "" : oco, t.nome + "_S");
				if (!double.IsNaN(t.target))
					t.tg = SubmitOrderUnmanaged(IDX, t.lato > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.Limit, t.qty, t.target, 0, oco, t.nome + "_T");
				Pr(string.Format("OroOrderFlowNT {0}: entrato {1} contratti a {2}, stop {3}{4}{5}", t.nome, t.qty, price, t.stop, double.IsNaN(t.target) ? "" : ", target " + t.target,
					t.segnale > DateTime.MinValue ? string.Format(CultureInfo.InvariantCulture, " (eseguito {0:0.0} s dopo la chiusura della candela)", (DateTime.Now - t.segnale).TotalSeconds) : ""));
			}
			else
			{
				t.qty -= quantity;
				if (t.entrati > 0) t.pnl += (price - t.sommaEnt / t.entrati) * t.lato * quantity;
				if (t.qty <= 0)
				{
					t.qty = 0; t.finito = true;
					if (!t.contato && t.entrati > 0)
					{
						t.contato = true; AggiornaGiorno();
						if (t.pnl < 0) { perseFila++; perseOggi++; }
						else if (t.pnl > 0) perseFila = 0;
						SalvaStato();
						Pr(string.Format("OroOrderFlowNT {0}: risultato {1:0.00} punti x contratti -> perdite di fila {2}, perdite oggi {3}", t.nome, t.pnl, perseFila, perseOggi));
					}
					if (Attivo(t.st)) CancelOrder(t.st);
					if (Attivo(t.tg)) CancelOrder(t.tg);
					if (Attivo(t.ex)) CancelOrder(t.ex);
					Pr(string.Format("OroOrderFlowNT {0}: chiuso a {1} ({2})", t.nome, price, o.Name.EndsWith("_T") ? "target" : o.Name.EndsWith("_S") ? "stop" : "uscita"));
				}
			}
		}

		#region Properties
		[NinjaScriptProperty][Display(Name = "Contratto per gli ordini", Description = "MGC della stessa scadenza del grafico GC", Order = 0, GroupName = "1 Ordini")]
		public string ContrattoOrdini { get; set; }
		[NinjaScriptProperty][Range(0.01, 5)][Display(Name = "Rischio % a trade", Description = "Prova Rapid Daily: 1,5 con filtro POC + protezione. Conto finanziato: 0,5", Order = 1, GroupName = "1 Ordini")]
		public double Rischio { get; set; }
		[NinjaScriptProperty][Range(1, 100)][Display(Name = "Massimo contratti MGC aperti", Order = 2, GroupName = "1 Ordini")]
		public int MaxMicro { get; set; }
		[NinjaScriptProperty][Range(0, 1000000)][Display(Name = "Stop giorno in $ (0 = spento)", Order = 3, GroupName = "1 Ordini")]
		public double StopGiornoDollari { get; set; }
		[NinjaScriptProperty][Range(0, 10000000)][Display(Name = "Conto virtuale $ (0 = usa il conto vero)", Description = "Demo da 50.000: 25000. Conto FundedNext vero: 0", Order = 4, GroupName = "1 Ordini")]
		public double ContoVirtuale { get; set; }
		[NinjaScriptProperty][Display(Name = "Usa segnali GROSSI", Order = 5, GroupName = "1 Ordini")]
		public bool UsaGrossi { get; set; }
		[NinjaScriptProperty][Display(Name = "Usa segnali FADE", Order = 6, GroupName = "1 Ordini")]
		public bool UsaFade { get; set; }
		[NinjaScriptProperty][Range(0, 600)][Display(Name = "Salta se il segnale arriva oltre N secondi (0 = spento)", Description = "Dopo blocchi o riconnessioni il prezzo e' peggiore: 0 = spento (consigliato: anche in ritardo i trade restano positivi)", Order = 7, GroupName = "1 Ordini")]
		public int MaxRitardoSecondi { get; set; }

		[NinjaScriptProperty][Display(Name = "Filtro POC: GROSSI solo verso il POC di ieri", Description = "Profilo 08:20-13:30 NY del giorno prima. Test: passa la prova piu' spesso con meno cali", Order = 3, GroupName = "3 Protezione perdite")]
		public bool FiltroPOC { get; set; }
		[NinjaScriptProperty][Display(Name = "Filtro POC: vale anche il POC di oggi (almeno uno)", Description = "18/11: entra se va verso il POC di ieri OPPURE verso quello di oggi (08:20 NY fino al segnale). Test: 121 trade/anno invece di 89, stessa qualita'", Order = 4, GroupName = "3 Protezione perdite")]
		public bool PocAncheOggi { get; set; }
		[NinjaScriptProperty][Range(0, 50)][Display(Name = "FADE: stop minimo in punti (0 = spento)", Description = "18/11: se lo stop della FADE e' piu' vicino di N punti lo allarga a N (soci: 5)", Order = 8, GroupName = "1 Ordini")]
		public double FadeStopMinimo { get; set; }
		[NinjaScriptProperty][Display(Name = "FADE: filtro volatilita' (salta dopo un giorno molto agitato)", Description = "20/11: salta la FADE se il range 08:20-13:30 NY di ieri e' nel terzo piu' alto dei giorni prima. Test prop prudente: passa 77% -> 83%, 5 prelievi 66% -> 75%", Order = 10, GroupName = "3 Protezione perdite")]
		public bool FiltroVolatilita { get; set; }
		[NinjaScriptProperty][Range(0.5, 0.95)][Display(Name = "FADE: soglia volatilita' (0,667 = terzo piu' agitato)", Order = 11, GroupName = "3 Protezione perdite")]
		public double VolSoglia { get; set; }
		[NinjaScriptProperty][Range(40, 400)][Display(Name = "FADE: giorni di confronto volatilita'", Order = 12, GroupName = "3 Protezione perdite")]
		public int VolGiorni { get; set; }
		[NinjaScriptProperty][Display(Name = "Aggiunta sui trade vincenti", Description = "A +N R apre una seconda posizione con stop all'entrata del trade iniziale (test: +28% guadagno, stesso calo)", Order = 0, GroupName = "4 Aggiunta")]
		public bool UsaAggiunta { get; set; }
		[NinjaScriptProperty][Range(0.25, 5.0)][Display(Name = "Aggiungi a +R", Description = "1 = quando il trade guadagna quanto rischia", Order = 1, GroupName = "4 Aggiunta")]
		public double AggiuntaR { get; set; }
		[NinjaScriptProperty][Range(0.1, 2.0)][Display(Name = "Dimensione aggiunta (frazione dei contratti iniziali)", Description = "0,5 = meta'", Order = 2, GroupName = "4 Aggiunta")]
		public double AggiuntaFrazione { get; set; }
		[NinjaScriptProperty][Range(1, 100)][Display(Name = "Massimo contratti del trade iniziale", Description = "10 come nei test; il tetto totale (con l'aggiunta) e' 'Massimo contratti MGC aperti' = 15", Order = 3, GroupName = "4 Aggiunta")]
		public int MaxIniziale { get; set; }
		[NinjaScriptProperty][Display(Name = "Usa cuscinetto (rischio x cuscinetto/1000, min 35%)", Description = "19/11 soci: rischio proporzionale ai soldi che mancano al limite di perdita FundedNext (saldo max fine giornata - 1000). Stato in cuscinetto_stato.txt", Order = 9, GroupName = "3 Protezione perdite")]
		public bool UsaCuscinetto { get; set; }
		[NinjaScriptProperty][Range(0, 20)][Display(Name = "Riduci il rischio dopo N perdite di fila (0 = spento)", Description = "Prova: 2. Conto finanziato: 0", Order = 0, GroupName = "3 Protezione perdite")]
		public int DimezzaDopo { get; set; }
		[NinjaScriptProperty][Range(0.1, 1.0)][Display(Name = "Fattore rischio ridotto", Description = "0,5 = meta' del rischio", Order = 1, GroupName = "3 Protezione perdite")]
		public double FattoreRidotto { get; set; }
		[NinjaScriptProperty][Range(0, 20)][Display(Name = "Massimo perdite al giorno (0 = spento)", Description = "Prova: 2", Order = 2, GroupName = "3 Protezione perdite")]
		public int MaxPerditeGiorno { get; set; }

		[NinjaScriptProperty][Range(1, 1000)][Display(Name = "Contratti per scambio grosso", Description = "GC: 15", Order = 0, GroupName = "2 Segnali")]
		public int SogliaContratti { get; set; }
		[NinjaScriptProperty][Range(0.5, 10.0)][Display(Name = "Soglia z scambi grossi", Order = 1, GroupName = "2 Segnali")]
		public double SogliaZ { get; set; }
		[NinjaScriptProperty][Range(100, 10000)][Display(Name = "Candele per la deviazione", Order = 2, GroupName = "2 Segnali")]
		public int Finestra { get; set; }
		[NinjaScriptProperty][Range(0, 600)][Display(Name = "Pausa tra segnali grossi (min)", Order = 3, GroupName = "2 Segnali")]
		public int PausaMinuti { get; set; }
		#endregion
	}
}
