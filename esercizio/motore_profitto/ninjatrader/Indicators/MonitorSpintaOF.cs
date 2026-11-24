// MonitorSpintaOF - Motore Profitto (13/11/2026). SOLO VISUALIZZAZIONE: non apre ordini e non modifica i bot.
// Mostra cosa fa la strategia OroSpintaNT: frecce dei trade SPINTA, linee entrata (bianca) / stop (rossa) / target (verde)
// fino all'uscita a 60 minuti, e un pannello con lo stato (trade di oggi, perdite, orario attivo, stato del bot oro).
// Legge Documenti\NinjaTrader 8\segnali_oro_of.csv (righe SPINTA), spinta_stato.txt e of_stato.txt.
// Va su qualsiasi grafico oro (GC o MGC). Se il grafico e' GC 5 minuti con Tick Replay, mostra anche la forza
// degli scambi grossi (z) della candela in corso, calcolata come la strategia.
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Windows.Media;
using NinjaTrader.Data;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
	public class MonitorSpintaOF : Indicator
	{
		private TimeZoneInfo ny;
		private DateTime ultimaLettura = DateTime.MinValue, barIniNy = DateTime.MinValue;
		private double ultimoAsk, ultimoBid, ultimoPrezzo, volPrecedente, gbuy, gsell, zOra = double.NaN;
		private int ultimoLato = 1;
		private readonly List<double> storiaG = new List<double>();

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "MonitorSpintaOF";
				Description = "Mostra sul grafico cosa fa OroSpintaNT: trade SPINTA con entrata/stop/target e pannello di stato. Solo visualizzazione.";
				Calculate = Calculate.OnEachTick;
				IsOverlay = true;
				DisplayInDataBox = false;
				PaintPriceMarkers = false;
				RischioBase = 0.75; SogliaContratti = 20; SogliaZ = 2.75; Finestra = 600; MinutiUscita = 60; GiorniDaMostrare = 5;
			}
			else if (State == State.DataLoaded)
			{
				ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
			}
		}

		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.MarketDataType == MarketDataType.Last) { if (e.Ask > e.Bid && e.Bid > 0) { ultimoAsk = e.Ask; ultimoBid = e.Bid; } }
			else if (e.MarketDataType == MarketDataType.Ask) ultimoAsk = e.Price;
			else if (e.MarketDataType == MarketDataType.Bid) ultimoBid = e.Price;
		}

		protected override void OnBarUpdate()
		{
			bool calcolaZ = Bars.IsTickReplay && BarsPeriod.BarsPeriodType == BarsPeriodType.Minute && BarsPeriod.Value == 5;
			if (IsFirstTickOfBar)
			{
				if (calcolaZ && CurrentBar > 0)
				{
					TimeSpan m = barIniNy.TimeOfDay;
					if (m >= new TimeSpan(8, 20, 0) && m < new TimeSpan(13, 30, 0))
					{
						storiaG.Add(gbuy - gsell);
						if (storiaG.Count > Finestra) storiaG.RemoveAt(0);
					}
				}
				gbuy = gsell = 0; volPrecedente = 0;
				barIniNy = TimeZoneInfo.ConvertTime(Time[0], TimeZoneInfo.Local, ny).AddMinutes(-BarsPeriod.Value);
			}
			if (calcolaZ)
			{
				double v = Volume[0] - volPrecedente; volPrecedente = Volume[0];
				if (v > 0)
				{
					double p = Close[0]; int lato;
					if (ultimoAsk > 0 && p >= ultimoAsk) lato = 1;
					else if (ultimoBid > 0 && p <= ultimoBid) lato = -1;
					else lato = p > ultimoPrezzo ? 1 : p < ultimoPrezzo ? -1 : ultimoLato;
					ultimoPrezzo = p; ultimoLato = lato;
					if (v >= SogliaContratti) { if (lato > 0) gbuy += v; else gsell += v; }
				}
				zOra = double.NaN;
				if (storiaG.Count >= 200)
				{
					double media = 0; foreach (double x in storiaG) media += x; media /= storiaG.Count;
					double var = 0; foreach (double x in storiaG) var += (x - media) * (x - media);
					double sd = Math.Sqrt(var / (storiaG.Count - 1));
					if (sd > 0) zOra = (gbuy - gsell) / sd;
				}
			}
			if (State != State.Realtime && CurrentBar < Count - 2) return;
			if ((DateTime.Now - ultimaLettura).TotalSeconds < 2) return;
			ultimaLettura = DateTime.Now;
			Disegna(calcolaZ);
		}

		private void Disegna(bool calcolaZ)
		{
			string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "segnali_oro_of.csv");
			string ultimo = "nessuno"; int tradeOggi = 0;
			DateTime oggiNy = TimeZoneInfo.ConvertTime(DateTime.Now, TimeZoneInfo.Local, ny).Date;
			try
			{
				if (File.Exists(f))
				{
					string[] righe;
					using (FileStream fs = new FileStream(f, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
					using (StreamReader sr = new StreamReader(fs)) righe = sr.ReadToEnd().Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
					for (int i = 1; i < righe.Length; i++)
					{
						string[] c = righe[i].Trim().Split(';');
						if (c.Length < 8 || c[2] != "SPINTA" || !c[7].Trim().StartsWith("ORDINE")) continue;
						DateTime t;
						if (!DateTime.TryParseExact(c[0], "yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture, DateTimeStyles.None, out t)) continue;
						if ((DateTime.Now - t).TotalDays > GiorniDaMostrare) continue;
						int lato = c[3] == "LONG" ? 1 : -1;
						double ent, st, tg;
						if (!double.TryParse(c[4], NumberStyles.Any, CultureInfo.InvariantCulture, out ent)) continue;
						if (!double.TryParse(c[5], NumberStyles.Any, CultureInfo.InvariantCulture, out st)) continue;
						if (!double.TryParse(c[6], NumberStyles.Any, CultureInfo.InvariantCulture, out tg)) tg = double.NaN;
						DateTime fine = t.AddMinutes(MinutiUscita);
						string tag = "ms_" + i;
						Brush col = lato > 0 ? Brushes.DeepSkyBlue : Brushes.Magenta;
						if (lato > 0) Draw.ArrowUp(this, tag + "_f", false, t, ent - 8 * TickSize, col);
						else Draw.ArrowDown(this, tag + "_f", false, t, ent + 8 * TickSize, col);
						Draw.Text(this, tag + "_t", false, "SPINTA " + (lato > 0 ? "LONG" : "SHORT"), t, lato > 0 ? ent - 18 * TickSize : ent + 18 * TickSize, 0, col,
							new SimpleFont("Arial", 10), System.Windows.TextAlignment.Center, Brushes.Transparent, Brushes.Transparent, 0);
						Draw.Line(this, tag + "_e", false, t, ent, fine, ent, Brushes.White, DashStyleHelper.Solid, 1);
						Draw.Line(this, tag + "_s", false, t, st, fine, st, Brushes.Red, DashStyleHelper.Dash, 2);
						if (!double.IsNaN(tg) && tg > 0) Draw.Line(this, tag + "_g", false, t, tg, fine, tg, Brushes.LimeGreen, DashStyleHelper.Dash, 2);
						Draw.VerticalLine(this, tag + "_v", fine, Brushes.DimGray, DashStyleHelper.Dot, 1);
						if (TimeZoneInfo.ConvertTime(t, TimeZoneInfo.Local, ny).Date == oggiNy) tradeOggi++;
						ultimo = string.Format(CultureInfo.InvariantCulture, "{0:dd/MM HH:mm} {1} entrata {2} stop {3} target {4} (esce entro {5:HH:mm})",
							t, lato > 0 ? "LONG" : "SHORT", ent, st, double.IsNaN(tg) ? "-" : tg.ToString(CultureInfo.InvariantCulture), fine);
					}
				}
			}
			catch (Exception ex) { Print("MonitorSpintaOF: errore lettura segnali " + ex.Message); }

			// stato della strategia e del bot oro
			int fila = 0, persOggi = 0; DateTime gP = DateTime.MinValue, gF = DateTime.MinValue;
			try
			{
				string fs2 = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "spinta_stato.txt");
				if (File.Exists(fs2))
				{
					string[] p = File.ReadAllText(fs2).Trim().Split(';');
					fila = int.Parse(p[0]); persOggi = int.Parse(p[1]); gP = DateTime.ParseExact(p[2], "yyyy-MM-dd", CultureInfo.InvariantCulture);
					if (p.Length > 3) gF = DateTime.ParseExact(p[3], "yyyy-MM-dd", CultureInfo.InvariantCulture);
				}
			}
			catch { }
			int botFila = 0, botOggi = 0;
			try
			{
				string fb = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "of_stato.txt");
				if (File.Exists(fb))
				{
					string[] p = File.ReadAllText(fb).Trim().Split(';');
					botFila = int.Parse(p[0]);
					if (DateTime.ParseExact(p[2], "yyyy-MM-dd", CultureInfo.InvariantCulture) == oggiNy) botOggi = int.Parse(p[1]);
				}
			}
			catch { }
			if (gP != oggiNy) persOggi = 0;
			int filaTot = Math.Max(fila, botFila);
			double rischio = RischioBase * (filaTot >= 2 ? 0.5 : 1.0);
			TimeSpan oraNy = TimeZoneInfo.ConvertTime(DateTime.Now, TimeZoneInfo.Local, ny).TimeOfDay;
			string stato;
			if (gF == oggiNy || tradeOggi > 0) stato = "trade di oggi GIA' FATTO (riprende domani)";
			else if (botOggi >= 2) stato = "FERMO oggi (il bot oro ha 2 perdite)";
			else if (oraNy >= new TimeSpan(8, 20, 0) && oraNy < new TimeSpan(12, 0, 0)) stato = "ATTIVO: aspetta una spinta degli scambi grossi";
			else if (oraNy < new TimeSpan(8, 20, 0)) stato = "in attesa (apre alle 08:20 NY)";
			else stato = "fuori orario (finestra 08:20-12:00 NY finita)";
			string zTxt = calcolaZ ? (double.IsNaN(zOra) ? "in calcolo (servono 200 candele)" : string.Format(CultureInfo.InvariantCulture, "{0:+0.00;-0.00} (segnale da +/-{1})", zOra, SogliaZ))
				: "serve grafico GC 5 min con Tick Replay";
			string pannello = string.Format(CultureInfo.InvariantCulture,
				"BOT ORO SPINTA: {0}\nOrario: 08:20-12:00 NY, max 1 trade al giorno, uscita dopo {1} min\nRischio prossimo trade: {2}%{3}\nPerdite di fila: {4} (bot oro {5})   Perdite oro oggi: {6}\nForza scambi grossi candela in corso: {7}\nUltimo: {8}",
				stato, MinutiUscita, rischio, filaTot >= 2 ? " (ridotto dopo 2 perdite)" : "", fila, botFila, botOggi, zTxt, ultimo);
			Draw.TextFixed(this, "ms_pannello", pannello, TextPosition.TopRight, Brushes.White, new SimpleFont("Consolas", 12), Brushes.DeepSkyBlue, Brushes.Black, 70);
		}

		#region Properties
		[NinjaScriptProperty][Range(0.01, 5)][Display(Name = "Rischio base SPINTA (%)", Description = "Lo stesso 'Rischio % a trade' di OroSpintaNT (prova: 0,75)", Order = 0, GroupName = "Parametri")]
		public double RischioBase { get; set; }
		[NinjaScriptProperty][Range(1, 1000)][Display(Name = "Contratti per scambio grosso", Order = 1, GroupName = "Parametri")]
		public int SogliaContratti { get; set; }
		[NinjaScriptProperty][Range(0.5, 10.0)][Display(Name = "Soglia z", Order = 2, GroupName = "Parametri")]
		public double SogliaZ { get; set; }
		[NinjaScriptProperty][Range(100, 10000)][Display(Name = "Candele per la deviazione", Order = 3, GroupName = "Parametri")]
		public int Finestra { get; set; }
		[NinjaScriptProperty][Range(5, 600)][Display(Name = "Uscita dopo (minuti)", Order = 4, GroupName = "Parametri")]
		public int MinutiUscita { get; set; }
		[NinjaScriptProperty][Range(1, 60)][Display(Name = "Giorni di trade da mostrare", Order = 5, GroupName = "Parametri")]
		public int GiorniDaMostrare { get; set; }
		#endregion
	}
}
