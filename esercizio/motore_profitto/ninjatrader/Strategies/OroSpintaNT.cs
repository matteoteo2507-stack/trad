// OroSpintaNT - Motore Profitto (13/11/2026). Seconda strategia oro order flow, SEPARATA da OroOrderFlowNT (non lo modifica).
// Da mettere su GC (oro grande) 5 minuti, Tick Replay ACCESO (lo stesso grafico del bot va bene). Ordini su MGC.
//  SPINTA: tra 08:20 e 12:00 di New York, candela 5m in cui gli scambi GROSSI (>= 20 contratti) netti superano 2,75 deviazioni
//          (deviazione sulle ultime 600 candele 08:20-13:30, come il bot) nello stesso verso della candela.
//          Entrata a mercato, STOP a META' della distanza entrata-estremo della candela, TARGET 4 volte lo stop
//          (= stessa distanza del 2R del bot), uscita dopo 60 minuti se non tocca nulla. Massimo 1 trade al giorno.
// Test 1 anno (nov 2025-nov 2026): circa 9 trade al mese, R +0,89 a trade, 12 mesi positivi su 13, correlazione col bot 0,25.
// Protezioni: rischio % del conto (prova 0,75); dopo 2 perdite di fila (sue o del bot) rischio dimezzato; se il bot ha gia'
// 2 perdite oggi non entra; tetto contratti MGC dell'INTERO conto (bot + questa); non entra se il conto ha MGC nel verso opposto;
// guardiano: perdita del giorno oltre StopGiornoDollari (equity dalla mezzanotte di Atene) -> chiude e si ferma fino a domani.
// Ordini SOLO in tempo reale. Stato in Documenti\NinjaTrader 8\spinta_stato.txt. Eventi in eventi_bot.txt (avvisi Telegram).
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
	public class OroSpintaNT : Strategy
	{
		private class Trade
		{
			public string nome; public int lato, qty, chiesti, entrati; public double stop, target, sommaEnt, pnl; public DateTime fineUtc;
			public Order ent, st, tg, ex; public bool chiudi, finito, contato;
			public DateTime segnale = DateTime.MinValue;
		}
		private int perseFila, perseOggi; private DateTime giornoPerse = DateTime.MinValue, giornoFatto = DateTime.MinValue;
		private double ultimoAsk, ultimoBid, ultimoPrezzo, volPrecedente;
		private int ultimoLato = 1;
		private double gbuy, gsell;
		private readonly List<double> storiaG = new List<double>();
		private DateTime barIniNy = DateTime.MinValue;
		private int conta;
		private TimeZoneInfo ny, ate;
		private readonly List<Trade> trades = new List<Trade>();
		private const int IDX = 1;
		private double virtBase = -1;
		private DateTime gsGiorno = DateTime.MinValue; private double gsRif; private bool gsFermo;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "OroSpintaNT";
				Description = "Oro order flow SPINTA: scambi grossi 20+, stop a meta' candela, target 4R, uscita dopo 60 min, 1 trade al giorno. Calcola su GC (Tick Replay), opera su MGC.";
				Calculate = Calculate.OnEachTick;
				IsUnmanaged = true;
				IsExitOnSessionCloseStrategy = false;
				BarsRequiredToTrade = 0;
				StartBehavior = StartBehavior.ImmediatelySubmit;
				ContrattoOrdini = "MGC 12-26";
				Rischio = 0.75; MaxIniziale = 10; MaxMicroConto = 15; StopGiornoDollari = 490; ContoVirtuale = 0;
				SogliaContratti = 20; SogliaZ = 2.75; Finestra = 600;
				FrazioneStop = 0.5; TargetR = 4.0; MinutiUscita = 60; UnoAlGiorno = true;
				DimezzaDopo = 2; FattoreRidotto = 0.5; RispettaBot = true; MaxRitardoSecondi = 0; UsaCuscinetto = true;   // 13/11: blocco spento, resta solo la misura del ritardo
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
				Print(string.Format(CultureInfo.InvariantCulture, "OroSpintaNT avviato: rischio {0}% a trade, scambi grossi >= {1}, z {2}, stop {3} della candela, target {4}R, uscita {5} min, max {6} MGC iniziali, tetto conto {7} MGC, stop giorno {8} $, conto virtuale {9} (vero {10:0.00}), storia {11} candele",
					Rischio, SogliaContratti, SogliaZ, FrazioneStop, TargetR, MinutiUscita, MaxIniziale, MaxMicroConto, StopGiornoDollari, ContoVirtuale, virtBase, storiaG.Count));
				Print(string.Format("OroSpintaNT protezione: perdite di fila {0} (sue), oggi {1}; rispetta lo stato del bot oro: {2}", perseFila, perseOggi, RispettaBot ? "si" : "no"));
				if (UsaCuscinetto) { string ic; NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Moltiplicatore(Account, out ic); Print("OroSpintaNT CUSCINETTO acceso: " + ic); } else Print("OroSpintaNT cuscinetto: spento");
			}
		}

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
			if (g != gsGiorno) { gsGiorno = g; gsRif = eq; if (gsFermo) Print("OroSpintaNT: nuovo giorno, si riparte"); gsFermo = false; }
			if (gsFermo) return false;
			if (StopGiornoDollari > 0 && eq <= gsRif - StopGiornoDollari)
			{
				gsFermo = true;
				foreach (Trade t in trades) if (!t.finito) Chiudi(t);
				Pr(string.Format("OroSpintaNT GUARDIANO: perdita del giorno oltre {0} $ (equity {1:0.00}, inizio {2:0.00}): chiuso, fermo fino a domani", StopGiornoDollari, eq, gsRif));
				return false;
			}
			return true;
		}
		private int ContoMGC()
		{
			try { return PositionsAccount[IDX].MarketPosition == MarketPosition.Flat ? 0 : (PositionsAccount[IDX].MarketPosition == MarketPosition.Long ? 1 : -1) * PositionsAccount[IDX].Quantity; }
			catch { return 0; }
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
				if (State == State.Realtime) UsciteATempo();
				return;
			}
			if (CurrentBars[0] == 0 && !Bars.IsTickReplay)
				Draw.TextFixed(this, "spAvviso", "OroSpintaNT: accendi Tick Replay sul grafico GC (serve il lato di ogni scambio)", TextPosition.BottomLeft);
			if (State == State.Historical && !Bars.IsTickReplay) return;

			if (IsFirstTickOfBar)
			{
				if (CurrentBar > 0) BarraChiusa();
				gbuy = gsell = 0; volPrecedente = 0;
				barIniNy = TimeZoneInfo.ConvertTime(Time[0], TimeZoneInfo.Local, ny).AddMinutes(-BarsPeriod.Value);
			}
			double v = Volume[0] - volPrecedente; volPrecedente = Volume[0];
			if (v <= 0) return;
			double p = Close[0]; int lato;
			if (ultimoAsk > 0 && p >= ultimoAsk) lato = 1;
			else if (ultimoBid > 0 && p <= ultimoBid) lato = -1;
			else lato = p > ultimoPrezzo ? 1 : p < ultimoPrezzo ? -1 : ultimoLato;
			ultimoPrezzo = p; ultimoLato = lato;
			if (v >= SogliaContratti) { if (lato > 0) gbuy += v; else gsell += v; }
		}

		private void BarraChiusa()
		{
			DateTime fineNy = TimeZoneInfo.ConvertTime(Time[1], TimeZoneInfo.Local, ny);
			DateTime inizioNy = fineNy.AddMinutes(-BarsPeriod.Value);
			TimeSpan m = inizioNy.TimeOfDay; DateTime g = inizioNy.Date;
			double gnet = gbuy - gsell;
			if (m < new TimeSpan(8, 20, 0) || m >= new TimeSpan(13, 30, 0)) return;     // la deviazione si calcola solo sulle candele 08:20-13:30 (come il bot)
			if (m < new TimeSpan(12, 0, 0) && storiaG.Count >= 200 && !(UnoAlGiorno && g == giornoFatto))
			{
				double media = 0; foreach (double x in storiaG) media += x; media /= storiaG.Count;
				double var = 0; foreach (double x in storiaG) var += (x - media) * (x - media);
				double sd = Math.Sqrt(var / (storiaG.Count - 1));
				int dir = Math.Sign(Close[1] - Open[1]);
				if (sd > 0 && dir != 0)
				{
					double z = gnet / sd;
					if (Math.Abs(z) >= SogliaZ && Math.Sign(z) == dir)
						Apri(dir, dir > 0 ? Low[1] - TickSize : High[1] + TickSize, g, string.Format(CultureInfo.InvariantCulture, "z {0:0.0}", z));
				}
			}
			storiaG.Add(gnet);
			if (storiaG.Count > Finestra) storiaG.RemoveAt(0);
		}

		// ------------------------------------------------------------------ ordini
		private void Apri(int dir, double estremo, DateTime giornoNy, string nota)
		{
			Brush col = dir > 0 ? Brushes.DeepSkyBlue : Brushes.Magenta;
			string tag = "sp" + CurrentBar;
			if (dir > 0) Draw.ArrowUp(this, tag, false, 0, Low[0] - 8 * TickSize, col);
			else Draw.ArrowDown(this, tag, false, 0, High[0] + 8 * TickSize, col);
			if (State != State.Realtime || !Guardiano()) return;
			double ritardo = (DateTime.Now - Time[1]).TotalSeconds;
			if (MaxRitardoSecondi > 0 && ritardo > MaxRitardoSecondi)
			{ Pr(string.Format(CultureInfo.InvariantCulture, "OroSpintaNT: segnale in RITARDO di {0:0} s (massimo {1}), salto", ritardo, MaxRitardoSecondi)); return; }
			nota += string.Format(CultureInfo.InvariantCulture, ", ritardo {0:0.0} s", ritardo);

			MasterInstrument mi = Instruments[IDX].MasterInstrument;
			double px = dir > 0 ? GetCurrentAsk(IDX) : GetCurrentBid(IDX);
			if (px <= 0) px = Closes[IDX][0];
			double d0 = (px - estremo) * dir;
			if (d0 <= 2 * mi.TickSize) { Print("OroSpintaNT: prezzo gia' oltre l'estremo della candela, salto"); return; }
			double rk = mi.RoundToTickSize(Math.Max(d0 * FrazioneStop, 3 * mi.TickSize));
			double stop = mi.RoundToTickSize(px - dir * rk), target = mi.RoundToTickSize(px + dir * TargetR * rk);

			AggiornaGiorno();
			int botFila = 0, botOggi = 0;
			if (RispettaBot) LeggiBot(out botFila, out botOggi);
			if (RispettaBot && botOggi >= 2) { Pr(string.Format("OroSpintaNT: il bot oro ha gia' {0} perdite oggi, salto fino a domani", botOggi)); giornoFatto = giornoNy; SalvaStato(); return; }
			int fila = Math.Max(perseFila, botFila);
			double rischioPct = Rischio * ((DimezzaDopo > 0 && fila >= DimezzaDopo) ? FattoreRidotto : 1.0);
			if (rischioPct < Rischio) Pr(string.Format("OroSpintaNT: {0} perdite di fila, rischio ridotto a {1}%", fila, rischioPct));
			if (UsaCuscinetto) { string ic; double mc = NinjaTrader.NinjaScript.AddOns.CuscinettoMP.Moltiplicatore(Account, out ic); rischioPct *= mc; Pr("OroSpintaNT " + ic); }   // 19/11 cuscinetto

			int conto = ContoMGC();
			if (conto != 0 && Math.Sign(conto) != dir) { Pr(string.Format("OroSpintaNT: sul conto ci sono gia' {0} MGC nel verso opposto (bot), salto", conto)); return; }
			double grezzo = rischioPct / 100.0 * Equity() / (rk * mi.PointValue);
			int q = (int)Math.Floor(grezzo + 1e-9);
			if (q < 1) q = grezzo >= 0.5 ? 1 : 0;
			q = Math.Min(Math.Min(q, MaxIniziale), MaxMicroConto - Math.Abs(conto));
			if (q < 1) { Pr(string.Format("OroSpintaNT: contratti 0 (stop {0:0.0} punti, sul conto {1} MGC, tetto {2}), salto", rk, conto, MaxMicroConto)); return; }

			giornoFatto = giornoNy; SalvaStato();
			Trade t = new Trade();
			conta++;
			t.nome = "OFS" + conta; t.lato = dir; t.chiesti = q; t.stop = stop; t.target = target; t.fineUtc = DateTime.UtcNow.AddMinutes(MinutiUscita); t.segnale = Time[1];
			trades.Add(t);
			t.ent = SubmitOrderUnmanaged(IDX, dir > 0 ? OrderAction.Buy : OrderAction.SellShort, OrderType.Market, q, 0, 0, "", t.nome);
			string riga = string.Format(CultureInfo.InvariantCulture, "{0:yyyy-MM-dd HH:mm:ss};{1};SPINTA;{2};{3};{4};{5};ORDINE {6} contratti, {7}, stop {8} punti, esce entro {9} min",
				Time[0], Instruments[IDX].FullName, dir > 0 ? "LONG" : "SHORT", px, stop, target, q, nota, rk, MinutiUscita);
			Pr("OroSpintaNT " + riga);
			try
			{
				string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "segnali_oro_of.csv");
				if (!File.Exists(f)) File.WriteAllText(f, "ora;strumento;tipo;lato;entrata;stop;target;nota" + Environment.NewLine);
				File.AppendAllText(f, riga + Environment.NewLine);
			}
			catch (Exception ex) { Print("OroSpintaNT: errore scrittura " + ex.Message); }
		}

		private void UsciteATempo()
		{
			Guardiano();
			foreach (Trade t in trades)
				if (!t.finito && !t.chiudi && DateTime.UtcNow >= t.fineUtc) { Pr("OroSpintaNT " + t.nome + ": " + MinutiUscita + " minuti passati, esco"); Chiudi(t); }
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
			if (Attivo(t.st)) { CancelOrder(t.st); if (Attivo(t.tg)) CancelOrder(t.tg); return; }
			Esci(t);
		}
		private void Esci(Trade t)
		{
			if (t.qty <= 0) { if (!Attivo(t.ent)) t.finito = true; return; }
			if (Attivo(t.ex)) return;
			t.ex = SubmitOrderUnmanaged(IDX, t.lato > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.Market, t.qty, 0, 0, "", t.nome + "_X");
		}

		// ------------------------------------------------------------------ stato
		private void AggiornaGiorno()
		{
			DateTime g = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, ny).Date;
			if (g != giornoPerse) { giornoPerse = g; perseOggi = 0; SalvaStato(); }
		}
		private string FileStato() { return Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "spinta_stato.txt"); }
		private void SalvaStato()
		{
			try { File.WriteAllText(FileStato(), string.Format(CultureInfo.InvariantCulture, "{0};{1};{2:yyyy-MM-dd};{3:yyyy-MM-dd}", perseFila, perseOggi, giornoPerse, giornoFatto)); }
			catch (Exception ex) { Print("OroSpintaNT: errore salvataggio stato " + ex.Message); }
		}
		private void LeggiStato()
		{
			try
			{
				if (!File.Exists(FileStato())) return;
				string[] p = File.ReadAllText(FileStato()).Trim().Split(';');
				perseFila = int.Parse(p[0]); perseOggi = int.Parse(p[1]);
				giornoPerse = DateTime.ParseExact(p[2], "yyyy-MM-dd", CultureInfo.InvariantCulture);
				if (p.Length > 3) giornoFatto = DateTime.ParseExact(p[3], "yyyy-MM-dd", CultureInfo.InvariantCulture);
			}
			catch (Exception ex) { Print("OroSpintaNT: errore lettura stato " + ex.Message); }
		}
		// stato del bot OroOrderFlowNT (solo lettura): perdite di fila; perdite di oggi (giorno di New York)
		private void LeggiBot(out int fila, out int oggi)
		{
			fila = 0; oggi = 0;
			try
			{
				string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "of_stato.txt");
				if (!File.Exists(f)) return;
				string[] p = File.ReadAllText(f).Trim().Split(';');
				fila = int.Parse(p[0]);
				DateTime g = DateTime.ParseExact(p[2], "yyyy-MM-dd", CultureInfo.InvariantCulture);
				if (g == TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, ny).Date) oggi = int.Parse(p[1]);
			}
			catch { }
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
			if (orderState == OrderState.Rejected) Pr(string.Format("OroSpintaNT: ordine {0} RIFIUTATO ({1} {2})", order.Name, error, comment));
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
				t.st = SubmitOrderUnmanaged(IDX, t.lato > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.StopMarket, t.qty, 0, t.stop, oco, t.nome + "_S");
				t.tg = SubmitOrderUnmanaged(IDX, t.lato > 0 ? OrderAction.Sell : OrderAction.BuyToCover, OrderType.Limit, t.qty, t.target, 0, oco, t.nome + "_T");
				Pr(string.Format("OroSpintaNT {0}: entrato {1} contratti a {2}, stop {3}, target {4}{5}", t.nome, t.qty, price, t.stop, t.target,
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
						Pr(string.Format("OroSpintaNT {0}: risultato {1:0.00} punti x contratti -> perdite di fila {2}, perdite oggi {3}", t.nome, t.pnl, perseFila, perseOggi));
					}
					if (Attivo(t.st)) CancelOrder(t.st);
					if (Attivo(t.tg)) CancelOrder(t.tg);
					if (Attivo(t.ex)) CancelOrder(t.ex);
					Pr(string.Format("OroSpintaNT {0}: chiuso a {1} ({2})", t.nome, price, o.Name.EndsWith("_T") ? "target" : o.Name.EndsWith("_S") ? "stop" : "uscita"));
				}
			}
		}

		#region Properties
		[NinjaScriptProperty][Display(Name = "Usa cuscinetto (rischio x cuscinetto/1000, min 35%)", Description = "19/11 soci: rischio proporzionale ai soldi che mancano al limite di perdita FundedNext (saldo max fine giornata - 1000). Stato in cuscinetto_stato.txt", Order = 9, GroupName = "3 Protezione perdite")]
		public bool UsaCuscinetto { get; set; }
		[NinjaScriptProperty][Display(Name = "Contratto per gli ordini", Description = "MGC della stessa scadenza del grafico GC", Order = 0, GroupName = "1 Ordini")]
		public string ContrattoOrdini { get; set; }
		[NinjaScriptProperty][Range(0.01, 5)][Display(Name = "Rischio % a trade", Description = "Prova Rapid Daily: 0,75 (accanto al bot a 1,5)", Order = 1, GroupName = "1 Ordini")]
		public double Rischio { get; set; }
		[NinjaScriptProperty][Range(1, 100)][Display(Name = "Massimo contratti MGC del trade", Order = 2, GroupName = "1 Ordini")]
		public int MaxIniziale { get; set; }
		[NinjaScriptProperty][Range(1, 100)][Display(Name = "Tetto MGC dell'intero conto (bot + questa)", Description = "15 come il bot", Order = 3, GroupName = "1 Ordini")]
		public int MaxMicroConto { get; set; }
		[NinjaScriptProperty][Range(0, 1000000)][Display(Name = "Stop giorno in $ (0 = spento)", Order = 4, GroupName = "1 Ordini")]
		public double StopGiornoDollari { get; set; }
		[NinjaScriptProperty][Range(0, 10000000)][Display(Name = "Conto virtuale $ (0 = usa il conto vero)", Description = "Demo da 50.000: 25000. Conto FundedNext vero: 0", Order = 5, GroupName = "1 Ordini")]
		public double ContoVirtuale { get; set; }

		[NinjaScriptProperty][Range(1, 1000)][Display(Name = "Contratti per scambio grosso", Description = "Test: 20", Order = 0, GroupName = "2 Segnale")]
		public int SogliaContratti { get; set; }
		[NinjaScriptProperty][Range(0.5, 10.0)][Display(Name = "Soglia z", Description = "Test: 2,75", Order = 1, GroupName = "2 Segnale")]
		public double SogliaZ { get; set; }
		[NinjaScriptProperty][Range(100, 10000)][Display(Name = "Candele per la deviazione (08:20-13:30)", Order = 2, GroupName = "2 Segnale")]
		public int Finestra { get; set; }
		[NinjaScriptProperty][Range(0.1, 1.0)][Display(Name = "Stop: frazione della candela", Description = "0,5 = a meta' tra entrata ed estremo della candela", Order = 3, GroupName = "2 Segnale")]
		public double FrazioneStop { get; set; }
		[NinjaScriptProperty][Range(0.5, 10.0)][Display(Name = "Target in R", Description = "4 = 4 volte lo stop", Order = 4, GroupName = "2 Segnale")]
		public double TargetR { get; set; }
		[NinjaScriptProperty][Range(5, 600)][Display(Name = "Uscita dopo (minuti)", Order = 5, GroupName = "2 Segnale")]
		public int MinutiUscita { get; set; }
		[NinjaScriptProperty][Display(Name = "Massimo 1 trade al giorno", Order = 6, GroupName = "2 Segnale")]
		public bool UnoAlGiorno { get; set; }

		[NinjaScriptProperty][Range(0, 20)][Display(Name = "Riduci il rischio dopo N perdite di fila (0 = spento)", Order = 0, GroupName = "3 Protezione")]
		public int DimezzaDopo { get; set; }
		[NinjaScriptProperty][Range(0.1, 1.0)][Display(Name = "Fattore rischio ridotto", Order = 1, GroupName = "3 Protezione")]
		public double FattoreRidotto { get; set; }
		[NinjaScriptProperty][Display(Name = "Rispetta lo stato del bot oro (2 perdite oggi = stop)", Order = 2, GroupName = "3 Protezione")]
		public bool RispettaBot { get; set; }
		[NinjaScriptProperty][Range(0, 600)][Display(Name = "Salta se il segnale arriva oltre N secondi (0 = spento)", Description = "0 = spento (consigliato)", Order = 3, GroupName = "3 Protezione")]
		public int MaxRitardoSecondi { get; set; }
		#endregion
	}
}
