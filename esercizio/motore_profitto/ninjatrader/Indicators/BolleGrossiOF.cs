// BolleGrossiOF - Motore Profitto (20/11/2026). SOLO VISUALIZZAZIONE: non apre ordini. Stile "big trades" di DeepCharts, solo Level 1.
// Ogni scambio grosso diventa una bolla al suo prezzo e al suo momento dentro la candela: verde = compratore aggressivo (ask),
// rossa = venditore aggressivo (bid). Grandezza proporzionale ai contratti.
// AGGREGAZIONE: gli scambi dello stesso lato, allo stesso prezzo (+/- TickAggrega tick) e a meno di FinestraMs millisecondi l'uno
// dall'altro vengono sommati: un ordine grande spezzato in tanti pezzi piccoli diventa UNA bolla (come DeepCharts).
// Mostra solo le bolle >= Soglia contratti. Serve Tick Replay per lo storico. In basso a sinistra: le ultime bolle.
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
	public class BolleGrossiOF : Indicator
	{
		private class Bolla { public int Barra; public double Frazione, Prezzo; public long Vol; public int Lato; public DateTime T; }
		private readonly List<Bolla> bolle = new List<Bolla>();
		private readonly object blocco = new object();
		private double ultimoAsk, ultimoBid, prezzoPrec; private int latoPrec = 1;
		// scambio in costruzione (aggregazione)
		private bool aperta; private double aPrezzo; private long aVol; private int aLato; private DateTime aT0, aT1; private int aBarra;
		private SharpDX.Direct2D1.SolidColorBrush brBuy, brSell, brTesto, brBordo;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "BolleGrossiOF";
				Description = "Bolle dei grossi scambi (aggregati come DeepCharts): verde compratori, rosso venditori. Solo visualizzazione, Level 1.";
				Calculate = Calculate.OnEachTick; IsOverlay = true; DrawOnPricePanel = true; DisplayInDataBox = false; PaintPriceMarkers = false;
				IsSuspendedWhileInactive = false; MaximumBarsLookBack = MaximumBarsLookBack.Infinite;
				Soglia = 40; FinestraMs = 50; TickAggrega = 1; RaggioMax = 16; Opacita = 45; CandeleMassime = 600; MostraNumeri = true; MostraElenco = false;
			}
			else if (State == State.DataLoaded) lock (blocco) bolle.Clear();
			else if (State == State.Terminated) Libera();
		}

		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.MarketDataType == MarketDataType.Ask) { ultimoAsk = e.Price; return; }
			if (e.MarketDataType == MarketDataType.Bid) { ultimoBid = e.Price; return; }
			if (e.MarketDataType != MarketDataType.Last || e.Volume <= 0) return;
			if (State == State.Historical && !Bars.IsTickReplay) return;
			double ask = e.Ask > e.Bid && e.Bid > 0 ? e.Ask : ultimoAsk, bid = e.Ask > e.Bid && e.Bid > 0 ? e.Bid : ultimoBid;
			double p = e.Price;
			int lato = ask > bid && bid > 0 && p >= ask ? 1 : ask > bid && bid > 0 && p <= bid ? -1 : p > prezzoPrec ? 1 : p < prezzoPrec ? -1 : latoPrec;
			latoPrec = lato; prezzoPrec = p;
			bool unisci = aperta && lato == aLato && Math.Abs(p - aPrezzo) <= TickAggrega * TickSize + 1e-9 && (e.Time - aT1).TotalMilliseconds <= FinestraMs;
			if (unisci) { aVol += (long)e.Volume; aT1 = e.Time; if (lato > 0) aPrezzo = Math.Max(aPrezzo, p); else aPrezzo = Math.Min(aPrezzo, p); return; }
			Chiudi();
			aperta = true; aPrezzo = p; aVol = (long)e.Volume; aLato = lato; aT0 = aT1 = e.Time; aBarra = Math.Max(0, CurrentBar);
		}

		private void Chiudi()
		{
			if (!aperta) return;
			aperta = false;
			if (aVol < Soglia || CurrentBar < 0) return;
			// posizione dentro la candela in base all'ora dello scambio
			double fr = 0.5;
			try
			{
				DateTime fine = Bars.GetTime(aBarra), inizio = aBarra > 0 ? Bars.GetTime(aBarra - 1) : fine.AddMinutes(-BarsPeriod.Value);
				if (fine > inizio) fr = Math.Max(0, Math.Min(1, (aT0 - inizio).TotalMilliseconds / (fine - inizio).TotalMilliseconds));
			}
			catch { }
			lock (blocco)
			{
				bolle.Add(new Bolla { Barra = aBarra, Frazione = fr, Prezzo = aPrezzo, Vol = aVol, Lato = aLato, T = aT0 });
				bolle.RemoveAll(b => b.Barra < CurrentBar - CandeleMassime);
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar == 0 && !Bars.IsTickReplay) Draw.TextFixed(this, "bgAvviso", "BolleGrossiOF: Tick Replay spento, bolle solo da adesso", TextPosition.TopLeft);
			if (State == State.Realtime && aperta && (DateTime.Now - aT1).TotalMilliseconds > Math.Max(FinestraMs, 200)) Chiudi();
		}

		public override void OnRenderTargetChanged()
		{
			Libera(); if (RenderTarget == null) return;
			brBuy = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.15f, 0.85f, 0.45f, 1f));
			brSell = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.95f, 0.25f, 0.30f, 1f));
			brTesto = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(1f, 1f, 1f, 1f));
			brBordo = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.05f, 0.05f, 0.05f, 1f));
		}
		private void Libera()
		{
			foreach (var b in new[] { brBuy, brSell, brTesto, brBordo }) if (b != null && !b.IsDisposed) b.Dispose();
			brBuy = brSell = brTesto = brBordo = null;
		}

		protected override void OnRender(ChartControl chartControl, ChartScale chartScale)
		{
			if (brBuy == null || ChartBars == null || IsInHitTest) return;
			float dist = chartControl.Properties.BarDistance;
			using (var tf = new SharpDX.DirectWrite.TextFormat(Core.Globals.DirectWriteFactory, "Consolas", SharpDX.DirectWrite.FontWeight.Bold, SharpDX.DirectWrite.FontStyle.Normal, 10f))
			{
				tf.TextAlignment = SharpDX.DirectWrite.TextAlignment.Center; tf.ParagraphAlignment = SharpDX.DirectWrite.ParagraphAlignment.Center;
				lock (blocco)
				{
					long mx = Soglia;
					foreach (Bolla b in bolle) if (b.Barra >= ChartBars.FromIndex && b.Barra <= ChartBars.ToIndex) mx = Math.Max(mx, b.Vol);
					List<Bolla> ultime = new List<Bolla>();
					foreach (Bolla b in bolle)
					{
						if (b.Barra < ChartBars.FromIndex || b.Barra > ChartBars.ToIndex) continue;
						float x = chartControl.GetXByBarIndex(ChartBars, b.Barra) - dist / 2f + (float)b.Frazione * dist;
						float y = chartScale.GetYByValue(b.Prezzo);
						float r = Math.Max(3f, (float)(RaggioMax * Math.Sqrt((double)b.Vol / mx)));
						var br = b.Lato > 0 ? brBuy : brSell; br.Opacity = Opacita / 100f;
						var el = new SharpDX.Direct2D1.Ellipse(new SharpDX.Vector2(x, y), r, r);
						RenderTarget.FillEllipse(el, br); brBordo.Opacity = 0.8f; RenderTarget.DrawEllipse(el, brBordo, 1f);
						if (MostraNumeri && r >= 11f) RenderTarget.DrawText(b.Vol.ToString(), tf, new SharpDX.RectangleF(x - r, y - 7f, 2f * r, 14f), brTesto);
					}
					if (MostraElenco)
					{
						int n = 0; float y0 = ChartPanel.Y + 4f;
						for (int i = bolle.Count - 1; i >= 0 && n < 6; i--, n++)
						{
							Bolla b = bolle[i];
							string s = string.Format(CultureInfo.InvariantCulture, "{0:HH:mm:ss} {1} {2} @ {3}", b.T, b.Lato > 0 ? "COMPRA" : "VENDE ", b.Vol, b.Prezzo);
							var br = b.Lato > 0 ? brBuy : brSell; br.Opacity = 1f;
							RenderTarget.DrawText(s, tf, new SharpDX.RectangleF(ChartPanel.X + ChartPanel.W - 230f, y0 + n * 13f, 220f, 13f), br);
						}
					}
				}
			}
			brBuy.Opacity = brSell.Opacity = 1f;
		}

		#region Properties
		[Range(1, 100000)][Display(Name = "Soglia (contratti)", Description = "GC: 40 = circa 1 bolla ogni 2-3 candele in orario NY; 60 = solo i giganti", Order = 0, GroupName = "Bolle")]
		public int Soglia { get; set; }
		[Range(0, 5000)][Display(Name = "Aggregazione: finestra (ms)", Description = "Scambi a meno di N millisecondi = stesso ordine", Order = 1, GroupName = "Bolle")]
		public int FinestraMs { get; set; }
		[Range(0, 20)][Display(Name = "Aggregazione: distanza prezzo (tick)", Order = 2, GroupName = "Bolle")]
		public int TickAggrega { get; set; }
		[Range(5, 80)][Display(Name = "Raggio massimo (pixel)", Order = 3, GroupName = "Bolle")]
		public int RaggioMax { get; set; }
		[Range(10, 100)][Display(Name = "Opacita' %", Order = 4, GroupName = "Bolle")]
		public int Opacita { get; set; }
		[Display(Name = "Numeri dentro le bolle", Order = 5, GroupName = "Bolle")]
		public bool MostraNumeri { get; set; }
		[Display(Name = "Elenco ultime bolle", Order = 6, GroupName = "Bolle")]
		public bool MostraElenco { get; set; }
		[Range(10, 100000)][Display(Name = "Candele tenute in memoria", Order = 7, GroupName = "Bolle")]
		public int CandeleMassime { get; set; }
		#endregion
	}
}
