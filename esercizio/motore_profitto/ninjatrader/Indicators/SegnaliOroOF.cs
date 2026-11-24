// SegnaliOroOF - Motore Profitto (10/11/2026). Solo segnali, NON apre ordini.
// Da mettere su GC (oro grande) 5 minuti, Tick Replay acceso, almeno 15 giorni caricati.
// Due segnali trovati nei test order flow (tick GC nov 2025 - nov 2026), da verificare IN AVANTI:
//  GROSSI (v2 10/11): tra 08:20 e 13:30 di New York, ogni candela 5m in cui gli scambi grossi (>= SogliaContratti,
//          default 15) netti sono oltre SogliaZ deviazioni e nello stesso verso della candela (pausa PausaMinuti tra due segnali).
//          Entrata all'apertura della candela dopo, stop oltre l'estremo opposto della candela, target 2R.
//  FADE:   range della candela 09:30-09:35 NY; una candela chiude fuori, poi una chiude di nuovo dentro
//          -> entrata contro la rottura SOLO se il delta cumulato dalle 09:30 e' nel verso del trade.
//          Stop oltre l'estremo raggiunto, nessun target, uscita alle 16:00 NY.
// In tempo reale ogni segnale viene scritto in Documenti\NinjaTrader 8\segnali_oro_of.csv
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
using NinjaTrader.Gui.Tools;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
	public class SegnaliOroOF : Indicator
	{
		private double ultimoAsk, ultimoBid, ultimoPrezzo, volPrecedente;
		private int ultimoLato = 1;
		private double buy, sell, gbuy, gsell;
		private readonly List<double> storiaG = new List<double>();
		private DateTime ultimoGrossi = DateTime.MinValue, giornoFade = DateTime.MinValue;
		private double fHi, fLo, fEst, cumDelta;
		private int fRott;
		private bool fRange, fFatto;
		private TimeZoneInfo ny;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "SegnaliOroOF";
				Description = "Segnali order flow sull'oro (scambi grossi + fade 09:30 con delta). Solo segnali, nessun ordine.";
				Calculate = Calculate.OnEachTick;
				IsOverlay = true;
				DisplayInDataBox = false;
				PaintPriceMarkers = false;
				SogliaContratti = 15;
				PausaMinuti = 30;
				SogliaZ = 2.5;
				Finestra = 600;
				FadeStopMinimo = 5.0;
			}
			else if (State == State.DataLoaded)
			{
				ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
			}
		}

		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.MarketDataType == MarketDataType.Last)
			{
				if (e.Ask > e.Bid && e.Bid > 0) { ultimoAsk = e.Ask; ultimoBid = e.Bid; }
			}
			else if (e.MarketDataType == MarketDataType.Ask)
				ultimoAsk = e.Price;
			else if (e.MarketDataType == MarketDataType.Bid)
				ultimoBid = e.Price;
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar == 0 && !Bars.IsTickReplay)
				Draw.TextFixed(this, "ofAvviso", "SegnaliOroOF: accendi Tick Replay (serve il lato di ogni scambio)", TextPosition.TopLeft);
			if (State == State.Historical && !Bars.IsTickReplay)
				return;

			if (IsFirstTickOfBar)
			{
				if (CurrentBar > 0)
					BarraChiusa();
				buy = sell = gbuy = gsell = 0;
				volPrecedente = 0;
			}
			double v = Volume[0] - volPrecedente;
			volPrecedente = Volume[0];
			if (v <= 0)
				return;
			double p = Close[0];
			int lato;
			if (ultimoAsk > 0 && p >= ultimoAsk) lato = 1;
			else if (ultimoBid > 0 && p <= ultimoBid) lato = -1;
			else lato = p > ultimoPrezzo ? 1 : p < ultimoPrezzo ? -1 : ultimoLato;
			ultimoPrezzo = p; ultimoLato = lato;
			// 'v' puo' sommare piu' scambi solo se arrivano nello stesso aggiornamento: con Tick Replay e' uno scambio
			if (lato > 0) { buy += v; if (v >= SogliaContratti) gbuy += v; }
			else { sell += v; if (v >= SogliaContratti) gsell += v; }
		}

		// chiamata al primo tick della candela nuova: la candela chiusa e' quella con indice 1
		private void BarraChiusa()
		{
			DateTime fineNy = TimeZoneInfo.ConvertTime(Time[1], TimeZoneInfo.Local, ny);
			DateTime inizioNy = fineNy.AddMinutes(-BarsPeriod.Value);
			TimeSpan m = inizioNy.TimeOfDay;
			DateTime g = inizioNy.Date;
			double delta = buy - sell, gnet = gbuy - gsell;

			// ---- GROSSI
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
							double entrata = Open[0];
							double target = entrata + 2 * (entrata - stop);
							Segnale("GROSSI", dir, entrata, stop, target, string.Format(CultureInfo.InvariantCulture, "z {0:0.0}, se non tocca esci alle 13:30 NY", z));
						}
					}
				}
				storiaG.Add(gnet);
				if (storiaG.Count > Finestra) storiaG.RemoveAt(0);
			}

			// ---- FADE 09:30 con delta
			if (g != giornoFade)
			{
				giornoFade = g; fRange = false; fFatto = false; fRott = 0; cumDelta = 0;
			}
			if (m >= new TimeSpan(9, 30, 0) && m < new TimeSpan(16, 0, 0))
			{
				cumDelta += delta;
				if (m == new TimeSpan(9, 30, 0))
				{
					fHi = High[1]; fLo = Low[1]; fRange = true;
				}
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
							fFatto = true;
							int dir = -fRott;
							if (Math.Sign(cumDelta) == dir)
							{
								double stop = fRott > 0 ? fEst + TickSize : fEst - TickSize;
								string notaF = "delta " + cumDelta.ToString("0", CultureInfo.InvariantCulture) + ", uscita 16:00 NY";
								// 18/11: stop minimo come il bot (se piu' vicino di FadeStopMinimo punti lo allarga)
								if (FadeStopMinimo > 0 && (Open[0] - stop) * dir < FadeStopMinimo)
								{
									notaF += string.Format(CultureInfo.InvariantCulture, ", stop allargato a {0:0.0} punti", FadeStopMinimo);
									stop = Instrument.MasterInstrument.RoundToTickSize(Open[0] - dir * FadeStopMinimo);
								}
								Segnale("FADE", dir, Open[0], stop, double.NaN, notaF);
							}
						}
					}
				}
			}
		}

		private void Segnale(string tipo, int dir, double entrata, double stop, double target, string nota)
		{
			string tag = "of" + tipo + CurrentBar;
			Brush col = dir > 0 ? Brushes.LimeGreen : Brushes.OrangeRed;
			if (dir > 0)
				Draw.ArrowUp(this, tag, false, 0, Low[0] - 4 * TickSize, col);
			else
				Draw.ArrowDown(this, tag, false, 0, High[0] + 4 * TickSize, col);
			Draw.Text(this, tag + "t", false, tipo + (dir > 0 ? " LONG" : " SHORT") + "\nstop " + stop.ToString("0.0", CultureInfo.InvariantCulture)
				+ (double.IsNaN(target) ? "" : "\ntarget " + target.ToString("0.0", CultureInfo.InvariantCulture)),
				0, dir > 0 ? Low[0] - 14 * TickSize : High[0] + 14 * TickSize, 0, col, new SimpleFont("Segoe UI", 11), System.Windows.TextAlignment.Center, Brushes.Transparent, Brushes.Transparent, 0);
			Draw.Square(this, tag + "s", false, 0, stop, Brushes.Red);
			if (!double.IsNaN(target))
				Draw.Diamond(this, tag + "g", false, 0, target, Brushes.DodgerBlue);

			if (State == State.Realtime)
			{
				string riga = string.Format(CultureInfo.InvariantCulture, "{0:yyyy-MM-dd HH:mm:ss};{1};{2};{3};{4};{5};{6};{7}",
					Time[0], Instrument.FullName, tipo, dir > 0 ? "LONG" : "SHORT", entrata, stop, double.IsNaN(target) ? "" : target.ToString(CultureInfo.InvariantCulture), nota);
				try
				{
					string f = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "segnali_oro_of.csv");
					if (!File.Exists(f)) File.WriteAllText(f, "ora;strumento;tipo;lato;entrata;stop;target;nota" + Environment.NewLine);
					File.AppendAllText(f, riga + Environment.NewLine);
				}
				catch (Exception ex) { Print("SegnaliOroOF: errore scrittura " + ex.Message); }
				Print("SegnaliOroOF " + riga);
			}
		}

		#region Properties
		[Range(1, 1000)]
		[Display(Name = "Contratti per scambio grosso", Description = "GC: 15 (test 10/11: buono da 10 a 40). Su MGC non usare: metti l'indicatore su GC", Order = 0, GroupName = "Segnali")]
		public int SogliaContratti { get; set; }

		[Range(0.5, 10.0)]
		[Display(Name = "Soglia z scambi grossi", Order = 1, GroupName = "Segnali")]
		public double SogliaZ { get; set; }

		[Range(100, 10000)]
		[Display(Name = "Candele per la deviazione", Order = 2, GroupName = "Segnali")]
		public int Finestra { get; set; }

		[Range(0, 600)]
		[Display(Name = "Pausa tra segnali grossi (min)", Order = 3, GroupName = "Segnali")]
		public int PausaMinuti { get; set; }
		[Range(0, 50)][Display(Name = "FADE: stop minimo in punti (0 = spento)", Description = "18/11: come OroOrderFlowNT (soci: 5)", Order = 10, GroupName = "Parametri")]
		public double FadeStopMinimo { get; set; }
		#endregion
	}
}
