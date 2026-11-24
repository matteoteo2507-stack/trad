// RadarSegnaliOF - Motore Profitto (20/11/2026). SOLO VISUALIZZAZIONE: non apre ordini e non legge/modifica i bot.
// Mostra IN DIRETTA quanto manca ai segnali di GROSSI e SPINTA, con gli STESSI calcoli dei bot (OroOrderFlowNT / OroSpintaNT):
//   z = scambi grossi netti della candela 5m (compratori - venditori aggressivi, solo scambi >= soglia contratti)
//       / deviazione standard degli stessi valori nelle ultime 600 candele 08:20-13:30 NY.
//   GROSSI: scambi >= 15, |z| > 2,5 nel verso della candela, 08:20-13:30 NY, pausa 30 min, poi filtro POC 'almeno uno' (verso il POC di ieri o di oggi).
//   SPINTA: scambi >= 20, |z| >= 2,75 nel verso della candela, 08:20-12:00 NY, 1 al giorno.
// Il segnale vero si decide alla CHIUSURA della candela: qui vedi il valore che si sta formando. Pannello sotto il grafico: linee z e soglie.
// Mettere su GC 5 minuti con Tick Replay ACCESO (come il bot). Lo stato del bot (perdite, guardiano, cuscinetto) NON e' considerato: guarda l'Output.
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.Windows.Media;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
	public class RadarSegnaliOF : Indicator
	{
		private TimeZoneInfo ny;
		private double ultimoAsk, ultimoBid, ultimoPrezzo, volPrecedente; private int ultimoLato = 1;
		private double g15b, g15s, g20b, g20s;                         // candela in corso
		private readonly List<double> stG = new List<double>(), stS = new List<double>();
		private double sdG, sdS;                                        // deviazioni (aggiornate alla chiusura di ogni candela della finestra)
		private DateTime ultimoGrossi = DateTime.MinValue, spintaFatta = DateTime.MinValue;
		private readonly SortedDictionary<long, double> profilo = new SortedDictionary<long, double>();
		private DateTime giornoProf = DateTime.MinValue; private double pocIeri;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "RadarSegnaliOF";
				Description = "Quanto manca ai segnali GROSSI e SPINTA: z degli scambi grossi in diretta, soglie, verso della candela, finestra oraria, pausa e filtro POC. Solo visualizzazione.";
				Calculate = Calculate.OnEachTick; IsOverlay = false; DisplayInDataBox = true; DrawOnPricePanel = false;
				IsSuspendedWhileInactive = false; MaximumBarsLookBack = MaximumBarsLookBack.Infinite;
				SogliaG = 2.5; SogliaS = 2.75; ContrattiG = 15; ContrattiS = 20; Finestra = 600; PausaG = 30;
				AddPlot(new Stroke(Brushes.Orange, 2), PlotStyle.Bar, "zGROSSI");
				AddPlot(new Stroke(Brushes.DeepSkyBlue, 2), PlotStyle.Line, "zSPINTA");
				AddLine(new Stroke(Brushes.Orange, DashStyleHelper.Dash, 1), 2.5, "GROSSI +");
				AddLine(new Stroke(Brushes.Orange, DashStyleHelper.Dash, 1), -2.5, "GROSSI -");
				AddLine(new Stroke(Brushes.DeepSkyBlue, DashStyleHelper.Dot, 1), 2.75, "SPINTA +");
				AddLine(new Stroke(Brushes.DeepSkyBlue, DashStyleHelper.Dot, 1), -2.75, "SPINTA -");
				AddLine(new Stroke(Brushes.Gray, DashStyleHelper.Solid, 1), 0, "zero");
			}
			else if (State == State.DataLoaded) ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
		}

		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.MarketDataType == MarketDataType.Ask) ultimoAsk = e.Price;
			else if (e.MarketDataType == MarketDataType.Bid) ultimoBid = e.Price;
		}

		private static double Sd(List<double> x)
		{
			if (x.Count < 2) return 0;
			double m = 0; foreach (double v in x) m += v; m /= x.Count;
			double s = 0; foreach (double v in x) s += (v - m) * (v - m);
			return Math.Sqrt(s / (x.Count - 1));
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar == 0 && !Bars.IsTickReplay) Draw.TextFixed(this, "raAvviso", "RadarSegnaliOF: accendi Tick Replay (serve il lato di ogni scambio)", TextPosition.BottomLeft);
			if (State == State.Historical && !Bars.IsTickReplay) return;
			DateTime iniNy = TimeZoneInfo.ConvertTime(Time[0], TimeZoneInfo.Local, ny).AddMinutes(-BarsPeriod.Value);
			if (IsFirstTickOfBar)
			{
				if (CurrentBar > 0) Chiudi();
				g15b = g15s = g20b = g20s = 0; volPrecedente = 0;
			}
			double v = Volume[0] - volPrecedente; volPrecedente = Volume[0];
			if (v > 0)
			{
				double p = Close[0]; int lato;
				if (ultimoAsk > 0 && p >= ultimoAsk) lato = 1;
				else if (ultimoBid > 0 && p <= ultimoBid) lato = -1;
				else lato = p > ultimoPrezzo ? 1 : p < ultimoPrezzo ? -1 : ultimoLato;
				ultimoPrezzo = p; ultimoLato = lato;
				if (v >= ContrattiG) { if (lato > 0) g15b += v; else g15s += v; }
				if (v >= ContrattiS) { if (lato > 0) g20b += v; else g20s += v; }
				TimeSpan mp = iniNy.TimeOfDay;
				if (mp >= new TimeSpan(8, 20, 0) && mp < new TimeSpan(13, 30, 0))
				{
					if (iniNy.Date != giornoProf)
					{
						if (profilo.Count > 0) pocIeri = Poc();
						profilo.Clear(); giornoProf = iniNy.Date;
					}
					long k = (long)Math.Round(p / TickSize); double c; profilo.TryGetValue(k, out c); profilo[k] = c + v;
				}
			}
			double zg = sdG > 0 ? (g15b - g15s) / sdG : 0, zs = sdS > 0 ? (g20b - g20s) / sdS : 0;
			Values[0][0] = zg; Values[1][0] = zs;
			PlotBrushes[0][0] = Math.Abs(zg) > SogliaG ? Brushes.Lime : Brushes.Orange;
			if (State == State.Realtime || CurrentBar >= Count - 2) Pannello(iniNy, zg, zs);
		}

		private double Poc()
		{
			long best = 0; double bv = -1;
			foreach (KeyValuePair<long, double> kv in profilo) if (kv.Value > bv) { bv = kv.Value; best = kv.Key; }
			return best * TickSize;
		}

		// alla chiusura di una candela: stesse regole dei bot (aggiorna la storia solo con le candele 08:20-13:30 NY)
		private void Chiudi()
		{
			DateTime iniNy = TimeZoneInfo.ConvertTime(Time[1], TimeZoneInfo.Local, ny).AddMinutes(-BarsPeriod.Value);
			TimeSpan m = iniNy.TimeOfDay;
			if (m < new TimeSpan(8, 20, 0) || m >= new TimeSpan(13, 30, 0)) return;
			double ng = g15b - g15s, ns = g20b - g20s; int dir = Math.Sign(Close[1] - Open[1]);
			if (stG.Count >= 200 && sdG > 0 && dir != 0 && Math.Abs(ng / sdG) > SogliaG && Math.Sign(ng) == dir && (iniNy - ultimoGrossi).TotalMinutes >= PausaG)
			{
				ultimoGrossi = iniNy;
				Draw.Diamond(this, "raG" + CurrentBar, false, 1, ng / sdG, Brushes.Lime);
			}
			if (m < new TimeSpan(12, 0, 0) && stS.Count >= 200 && sdS > 0 && dir != 0 && Math.Abs(ns / sdS) >= SogliaS && Math.Sign(ns) == dir && spintaFatta != iniNy.Date)
			{
				spintaFatta = iniNy.Date;
				Draw.Square(this, "raS" + CurrentBar, false, 1, ns / sdS, Brushes.DeepSkyBlue);
			}
			stG.Add(ng); if (stG.Count > Finestra) stG.RemoveAt(0); sdG = Sd(stG);
			stS.Add(ns); if (stS.Count > Finestra) stS.RemoveAt(0); sdS = Sd(stS);
		}

		private void Pannello(DateTime iniNy, double zg, double zs)
		{
			TimeSpan m = iniNy.TimeOfDay; int dir = Math.Sign(Close[0] - Open[0]);
			string dirTxt = dir > 0 ? "verde (long)" : dir < 0 ? "rossa (short)" : "piatta";
			int sec = (int)Math.Max(0, (Time[0] - DateTime.Now).TotalSeconds);
			bool finG = m >= new TimeSpan(8, 20, 0) && m < new TimeSpan(13, 30, 0), finS = m >= new TimeSpan(8, 20, 0) && m < new TimeSpan(12, 0, 0);
			// GROSSI
			string sg;
			if (!finG) sg = "fuori orario (attivo 14:20-19:30 italiane)";
			else if (stG.Count < 200) sg = "storia in costruzione (" + stG.Count + "/200 candele)";
			else
			{
				double pct = Math.Min(999, 100 * Math.Abs(zg) / SogliaG);
				bool verso = Math.Sign(zg) == dir && dir != 0;
				int pausa = (int)Math.Max(0, PausaG - (iniNy - ultimoGrossi).TotalMinutes);
				double pocOggi = giornoProf == iniNy.Date && profilo.Count > 0 ? Poc() : 0;
				int lato = Math.Sign(zg); double px = Close[0];
				bool vI = pocIeri > 0 && Math.Sign(pocIeri - px) == lato, vO = pocOggi > 0 && Math.Sign(pocOggi - px) == lato;
				string poc = lato == 0 ? "-" : (vI || vO) ? "OK (" + (vI ? "verso POC ieri" : "") + (vI && vO ? " e " : "") + (vO ? "verso POC oggi" : "") + ")" : "NO: va via da entrambi i POC (salterebbe)";
				sg = string.Format(CultureInfo.InvariantCulture, "z {0:+0.00;-0.00} / {1:0.0}  = {2:0}% della soglia  | verso {3} | candela {4}{5}\n          filtro POC: {6}",
					zg, SogliaG, pct, zg > 0 ? "LONG" : zg < 0 ? "SHORT" : "-", dirTxt, zg == 0 ? "  (ancora nessuno scambio grosso in questa candela)" : verso ? "" : "  (z e candela NON concordano)", poc)
					+ (pausa > 0 ? "\n          in pausa ancora " + pausa + " min dopo l'ultimo segnale" : "")
					+ (Math.Abs(zg) > SogliaG && verso && pausa == 0 && (vI || vO) ? "\n          >>> SE LA CANDELA CHIUDE COSI' GROSSI ENTRA <<<" : "");
			}
			// SPINTA
			string ss;
			if (!finS) ss = "fuori orario (attiva 14:20-18:00 italiane)";
			else if (spintaFatta == iniNy.Date) ss = "gia' usata oggi (1 al giorno)";
			else if (stS.Count < 200) ss = "storia in costruzione (" + stS.Count + "/200 candele)";
			else
			{
				double pct = Math.Min(999, 100 * Math.Abs(zs) / SogliaS); bool verso = Math.Sign(zs) == dir && dir != 0;
				ss = string.Format(CultureInfo.InvariantCulture, "z {0:+0.00;-0.00} / {1:0.00} = {2:0}% della soglia  | verso {3} | candela {4}{5}",
					zs, SogliaS, pct, zs > 0 ? "LONG" : zs < 0 ? "SHORT" : "-", dirTxt, zs == 0 ? "  (ancora nessuno scambio grosso in questa candela)" : verso ? "" : "  (z e candela NON concordano)")
					+ (Math.Abs(zs) >= SogliaS && verso ? "\n          >>> SE LA CANDELA CHIUDE COSI' SPINTA ENTRA <<<" : "");
			}
			string testo = "RADAR SEGNALI (candela in corso, decide la CHIUSURA" + (State == State.Realtime ? string.Format(", mancano {0}:{1:00}", sec / 60, sec % 60) : "") + ")\n"
				+ "GROSSI:  " + sg + "\nSPINTA:  " + ss
				+ "\n(non conosce lo stato del bot: perdite del giorno, guardiano, filtro volatilita' -> vedi Output)";
			Draw.TextFixed(this, "raPannello", testo, TextPosition.TopLeft, Brushes.White, new NinjaTrader.Gui.Tools.SimpleFont("Consolas", 11), Brushes.Black, Brushes.Black, 70);
		}

		#region Properties
		[Range(0.5, 10)][Display(Name = "GROSSI: soglia z", Order = 0, GroupName = "Come i bot")]
		public double SogliaG { get; set; }
		[Range(0.5, 10)][Display(Name = "SPINTA: soglia z", Order = 1, GroupName = "Come i bot")]
		public double SogliaS { get; set; }
		[Range(1, 1000)][Display(Name = "GROSSI: contratti per scambio grosso", Order = 2, GroupName = "Come i bot")]
		public int ContrattiG { get; set; }
		[Range(1, 1000)][Display(Name = "SPINTA: contratti per scambio grosso", Order = 3, GroupName = "Come i bot")]
		public int ContrattiS { get; set; }
		[Range(100, 10000)][Display(Name = "Candele per la deviazione", Order = 4, GroupName = "Come i bot")]
		public int Finestra { get; set; }
		[Range(0, 600)][Display(Name = "GROSSI: pausa tra segnali (min)", Order = 5, GroupName = "Come i bot")]
		public int PausaG { get; set; }
		#endregion
	}
}
