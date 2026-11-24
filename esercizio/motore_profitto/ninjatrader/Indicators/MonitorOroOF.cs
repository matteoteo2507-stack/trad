// MonitorOroOF - Motore Profitto (12/11/2026). SOLO VISUALIZZAZIONE: non apre ordini e non modifica il bot.
// Da mettere sul grafico GC 5 minuti (lo stesso di OroOrderFlowNT, con Tick Replay acceso).
// Legge Documenti\NinjaTrader 8\segnali_oro_of.csv (ogni trade del bot) e of_stato.txt (perdite di fila / di oggi)
// e disegna: frecce sui segnali GROSSI / FADE / AGGIUNTA, linee di entrata (bianca), stop (rossa), target (verde),
// la linea del POC di ieri (oro, profilo 08:20-13:30 New York come il bot) e un pannello con lo stato del bot.
// 18/11: anche la linea del POC di OGGI (profilo dalle 08:20 NY fino ad ora): GROSSI entra se va verso almeno uno dei due.
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Windows.Media;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
	public class MonitorOroOF : Indicator
	{
		private TimeZoneInfo ny;
		private readonly SortedDictionary<long, double> profilo = new SortedDictionary<long, double>();
		private DateTime giornoProf = DateTime.MinValue, barIniNy = DateTime.MinValue, ultimaLettura = DateTime.MinValue, ultimaModifica = DateTime.MinValue;
		private double pocIeri, volPrecedente;
		private int righeDisegnate;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "MonitorOroOF";
				Description = "Mostra sul grafico cosa fa OroOrderFlowNT: segnali, entrata/stop/target, POC di ieri e stato della protezione. Solo visualizzazione.";
				Calculate = Calculate.OnEachTick;
				IsOverlay = true;
				DisplayInDataBox = false;
				PaintPriceMarkers = false;
				RischioBase = 0.75;
				GiorniDaMostrare = 5;
			}
			else if (State == State.DataLoaded)
			{
				ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
			}
		}

		protected override void OnBarUpdate()
		{
			if (IsFirstTickOfBar)
			{
				volPrecedente = 0;
				barIniNy = TimeZoneInfo.ConvertTime(Time[0], TimeZoneInfo.Local, ny).AddMinutes(-BarsPeriod.Value);
			}
			// profilo volume 08:20-13:30 NY (stesso calcolo del bot) -> POC di ieri
			double v = Volume[0] - volPrecedente; volPrecedente = Volume[0];
			TimeSpan m = barIniNy.TimeOfDay;
			if (v > 0 && m >= new TimeSpan(8, 20, 0) && m < new TimeSpan(13, 30, 0))
			{
				if (barIniNy.Date != giornoProf)
				{
					if (profilo.Count > 0)
					{
						long best = 0; double bv = -1;
						foreach (KeyValuePair<long, double> kv in profilo) if (kv.Value > bv) { bv = kv.Value; best = kv.Key; }
						pocIeri = best * TickSize;
					}
					profilo.Clear(); giornoProf = barIniNy.Date;
				}
				long lv = (long)Math.Round(Close[0] / TickSize);
				double cur; profilo.TryGetValue(lv, out cur); profilo[lv] = cur + v;
			}
			if (State != State.Realtime && CurrentBar < Count - 2) return;
			if ((DateTime.Now - ultimaLettura).TotalSeconds < 2) return;
			ultimaLettura = DateTime.Now;
			Disegna();
		}

		private double PocDiOggi()
		{
			DateTime oggiNy = TimeZoneInfo.ConvertTime(DateTime.Now, TimeZoneInfo.Local, ny).Date;
			if (profilo.Count == 0 || giornoProf != oggiNy) return 0;
			long best = 0; double bv = -1;
			foreach (KeyValuePair<long, double> kv in profilo) if (kv.Value > bv) { bv = kv.Value; best = kv.Key; }
			return best * TickSize;
		}

		private void Disegna()
		{
			double pocOggi = PocDiOggi();
			if (pocOggi > 0)
			{
				Draw.HorizontalLine(this, "mo_poc2", false, pocOggi, Brushes.DeepSkyBlue, DashStyleHelper.Dash, 2);
				Draw.Text(this, "mo_poc2_txt", false, "POC di oggi " + pocOggi.ToString("0.0", CultureInfo.InvariantCulture), 0, pocOggi, -8, Brushes.DeepSkyBlue,
					new SimpleFont("Arial", 11), System.Windows.TextAlignment.Right, Brushes.Transparent, Brushes.Transparent, 0);
			}
			else { RemoveDrawObject("mo_poc2"); RemoveDrawObject("mo_poc2_txt"); }
			if (pocIeri > 0)
			{
				Draw.HorizontalLine(this, "mo_poc", false, pocIeri, Brushes.Gold, DashStyleHelper.Dash, 2);
				Draw.Text(this, "mo_poc_txt", false, "POC di ieri " + pocIeri.ToString("0.0", CultureInfo.InvariantCulture), 0, pocIeri, 8, Brushes.Gold,
					new SimpleFont("Arial", 11), System.Windows.TextAlignment.Right, Brushes.Transparent, Brushes.Transparent, 0);
			}

			// segnali del bot
			string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "segnali_oro_of.csv");
			int tradeOggi = 0; string ultimo = "nessuno";
			try
			{
				if (File.Exists(f))
				{
					DateTime mod = File.GetLastWriteTime(f);
					string[] righe;
					using (FileStream fs = new FileStream(f, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
					using (StreamReader sr = new StreamReader(fs)) righe = sr.ReadToEnd().Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
					DateTime oggiNy = TimeZoneInfo.ConvertTime(DateTime.Now, TimeZoneInfo.Local, ny).Date;
					for (int i = 1; i < righe.Length; i++)
					{
						string[] c = righe[i].Trim().Split(';');
						if (c.Length < 7) continue;
						DateTime t;
						if (!DateTime.TryParseExact(c[0], "yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture, DateTimeStyles.None, out t)) continue;
						if ((DateTime.Now - t).TotalDays > GiorniDaMostrare) continue;
						string tipo = c[2]; int lato = c[3] == "LONG" ? 1 : -1;
						double ent, st, tg = double.NaN;
						if (!double.TryParse(c[4], NumberStyles.Any, CultureInfo.InvariantCulture, out ent)) continue;
						if (!double.TryParse(c[5], NumberStyles.Any, CultureInfo.InvariantCulture, out st)) continue;
						if (c[6].Length > 0) double.TryParse(c[6], NumberStyles.Any, CultureInfo.InvariantCulture, out tg);
						DateTime tNy = TimeZoneInfo.ConvertTime(t, TimeZoneInfo.Local, ny);
						DateTime fineNy = tNy.Date.Add(tipo == "FADE" ? new TimeSpan(16, 0, 0) : new TimeSpan(13, 30, 0));
						if (fineNy <= tNy) fineNy = tNy.AddHours(1);
						DateTime fine = TimeZoneInfo.ConvertTime(fineNy, ny, TimeZoneInfo.Local);
						string tag = "mo_" + i;
						// righe del bot = "ORDINE ..." (trade aperto); le altre le scrive l'indicatore SegnaliOroOF (segnale visto, il bot puo' averlo saltato)
						bool ordine = c.Length > 7 && c[7].Trim().StartsWith("ORDINE");
						if (!ordine)
						{
							if (lato > 0) Draw.ArrowUp(this, tag + "_f", false, t, ent - 6 * TickSize, Brushes.Gray);
							else Draw.ArrowDown(this, tag + "_f", false, t, ent + 6 * TickSize, Brushes.Gray);
							Draw.Text(this, tag + "_t", false, tipo + (lato > 0 ? " LONG" : " SHORT") + " (non preso)", t, lato > 0 ? ent - 14 * TickSize : ent + 14 * TickSize, 0, Brushes.Gray,
								new SimpleFont("Arial", 10), System.Windows.TextAlignment.Center, Brushes.Transparent, Brushes.Transparent, 0);
							continue;
						}
						Brush col = tipo == "AGGIUNTA" ? Brushes.DeepSkyBlue : (lato > 0 ? Brushes.LimeGreen : Brushes.OrangeRed);
						if (lato > 0) Draw.ArrowUp(this, tag + "_f", false, t, ent - 6 * TickSize, col);
						else Draw.ArrowDown(this, tag + "_f", false, t, ent + 6 * TickSize, col);
						Draw.Text(this, tag + "_t", false, tipo + (lato > 0 ? " LONG" : " SHORT"), t, lato > 0 ? ent - 14 * TickSize : ent + 14 * TickSize, 0, col,
							new SimpleFont("Arial", 10), System.Windows.TextAlignment.Center, Brushes.Transparent, Brushes.Transparent, 0);
						Draw.Line(this, tag + "_e", false, t, ent, fine, ent, Brushes.White, DashStyleHelper.Solid, 1);
						Draw.Line(this, tag + "_s", false, t, st, fine, st, Brushes.Red, DashStyleHelper.Dash, 2);
						if (!double.IsNaN(tg) && tg > 0) Draw.Line(this, tag + "_g", false, t, tg, fine, tg, Brushes.LimeGreen, DashStyleHelper.Dash, 2);
						if (tNy.Date == oggiNy && tipo != "AGGIUNTA") tradeOggi++;
						ultimo = string.Format(CultureInfo.InvariantCulture, "{0:dd/MM HH:mm} {1} {2} entrata {3} stop {4}{5}", t, tipo, lato > 0 ? "LONG" : "SHORT", ent, st,
							double.IsNaN(tg) ? "" : " target " + tg.ToString(CultureInfo.InvariantCulture));
					}
				}
			}
			catch (Exception ex) { Print("MonitorOroOF: errore lettura segnali " + ex.Message); }

			// stato della protezione
			int fila = 0, persOggi = 0; DateTime gP = DateTime.MinValue;
			try
			{
				string fs2 = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "of_stato.txt");
				if (File.Exists(fs2))
				{
					string[] p = File.ReadAllText(fs2).Trim().Split(';');
					fila = int.Parse(p[0]); persOggi = int.Parse(p[1]); gP = DateTime.ParseExact(p[2], "yyyy-MM-dd", CultureInfo.InvariantCulture);
				}
			}
			catch { }
			DateTime oggi = TimeZoneInfo.ConvertTime(DateTime.Now, TimeZoneInfo.Local, ny).Date;
			if (gP != oggi) persOggi = 0;
			double rischio = RischioBase * (fila >= 2 ? 0.5 : 1.0);
			string stato = persOggi >= 2 ? "FERMO fino a domani (2 perdite oggi)" : "attivo";
			TimeSpan oraNy = TimeZoneInfo.ConvertTime(DateTime.Now, TimeZoneInfo.Local, ny).TimeOfDay;
			string fin = oraNy >= new TimeSpan(8, 20, 0) && oraNy < new TimeSpan(13, 30, 0) ? "GROSSI attivo" : "GROSSI fuori orario";
			if (oraNy >= new TimeSpan(9, 30, 0) && oraNy < new TimeSpan(16, 0, 0)) fin += " | FADE attivo"; else fin += " | FADE fuori orario";
			string pannello = string.Format(CultureInfo.InvariantCulture,
				"BOT ORO ORDER FLOW: {0}\nRischio prossimo trade: {1}%{2}\nPerdite di fila: {3}   Perdite oggi: {4}/2\nPOC di ieri: {5}   POC di oggi: {9}  (GROSSI: verso almeno uno)\nTrade oggi: {6}   ({7})\nUltimo: {8}",
				stato, rischio, fila >= 2 ? " (ridotto dopo 2 perdite)" : "", fila, persOggi, pocIeri > 0 ? pocIeri.ToString("0.0", CultureInfo.InvariantCulture) : "in calcolo",
				tradeOggi, fin, ultimo, pocOggi > 0 ? pocOggi.ToString("0.0", CultureInfo.InvariantCulture) : "dalle 14:20 IT");
			Draw.TextFixed(this, "mo_pannello", pannello, TextPosition.TopLeft, Brushes.White, new SimpleFont("Consolas", 12), Brushes.Gray, Brushes.Black, 70);
		}

		#region Properties
		[NinjaScriptProperty][Range(0.01, 5)][Display(Name = "Rischio base del bot (%)", Description = "Lo stesso 'Rischio % a trade' di OroOrderFlowNT (ora: 0,75)", Order = 0, GroupName = "Parametri")]
		public double RischioBase { get; set; }
		[NinjaScriptProperty][Range(1, 60)][Display(Name = "Giorni di segnali da mostrare", Order = 1, GroupName = "Parametri")]
		public int GiorniDaMostrare { get; set; }
		#endregion
	}
}
