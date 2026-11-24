// FootprintOro - footprint bid x ask per prezzo dentro ogni candela (NinjaTrader 8)
// Sinistra = volume eseguito sul BID (venditori aggressivi), destra = volume sull'ASK (compratori aggressivi).
// Riquadro giallo = POC della candela (prezzo con piu' volume). Numero sotto = delta (ask - bid).
// Numeri colorati forti = imbalance diagonale (ask a p contro bid a p-1 tick, e viceversa) >= Rapporto.
// Storico: serve Tick Replay acceso sulla serie del grafico; senza, conta solo da quando lo metti.
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
	public class FootprintOro : Indicator
	{
		private class Cella { public long Bid; public long Ask; }
		private class Barra
		{
			public readonly SortedDictionary<double, Cella> Livelli = new SortedDictionary<double, Cella>();
			public long Delta;
			public double Min = double.MaxValue;
		}

		private readonly Dictionary<int, Barra> barre = new Dictionary<int, Barra>();
		private readonly object blocco = new object();
		private double volPrecedente;
		private double prezzoPrecedente;
		private int latoPrecedente = 1;
		private double ultimoAsk, ultimoBid;
		private long tickTotali, tickConQuote;

		private SharpDX.Direct2D1.SolidColorBrush brSfondo, brAsk, brBid, brTesto, brPoc, brImbAsk, brImbBid;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description = "Footprint bid x ask per prezzo, delta e POC per candela";
				Name = "FootprintOro";
				Calculate = Calculate.OnEachTick;
				IsOverlay = true;
				DrawOnPricePanel = true;
				DisplayInDataBox = false;
				PaintPriceMarkers = false;
				IsSuspendedWhileInactive = false;
				MaximumBarsLookBack = MaximumBarsLookBack.Infinite;
				Rapporto = 3.0;
				VolumeMinimoImbalance = 5;
				CandeleMassime = 400;
				TickPerRiga = 5;
				CelleTrasparenti = false;
				DimensioneNumeri = 14;
				RigheAutomatiche = true;
				AltezzaRiga = 14;
			}
			else if (State == State.DataLoaded)
			{
				lock (blocco) barre.Clear();
				tickTotali = tickConQuote = 0;
				ultimoAsk = ultimoBid = 0;
			}
			else if (State == State.Terminated)
			{
				Libera();
			}
		}

		// In Tick Replay l'evento Last porta bid e ask di quel momento ed arriva prima di OnBarUpdate dello stesso tick
		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.MarketDataType == MarketDataType.Last)
			{
				// alcuni feed storici mettono bid = ask = prezzo: in quel caso non sono quote vere
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
				Draw.TextFixed(this, "fpAvviso", "FootprintOro: Tick Replay spento, conto solo da adesso", TextPosition.TopLeft);

			// senza Tick Replay lo storico arriva a candele intere: non si puo' dividere bid/ask
			if (State == State.Historical && !Bars.IsTickReplay)
				return;

			if (IsFirstTickOfBar)
				volPrecedente = 0;
			double v = Volume[0] - volPrecedente;
			volPrecedente = Volume[0];
			if (v <= 0)
				return;

			double prezzo = Instrument.MasterInstrument.RoundToTickSize(Close[0]);
			double passo = TickPerRiga * TickSize;
			double livello = Instrument.MasterInstrument.RoundToTickSize(Math.Floor(prezzo / passo + 1e-9) * passo);
			// bid/ask del tick presi da OnMarketData (GetCurrentAsk in storico restituisce il Close)
			double ask = ultimoAsk;
			double bid = ultimoBid;

			int lato;
			bool quoteValide = ask > bid && bid > 0;
			if (quoteValide && prezzo >= ask) { lato = 1; tickConQuote++; }
			else if (quoteValide && prezzo <= bid) { lato = -1; tickConQuote++; }
			else if (prezzo > prezzoPrecedente) lato = 1;
			else if (prezzo < prezzoPrecedente) lato = -1;
			else lato = latoPrecedente;
			latoPrecedente = lato;
			tickTotali++;
			if (State == State.Realtime || IsFirstTickOfBar && CurrentBar == Bars.Count - 2)
				Draw.TextFixed(this, "fpQuote", string.Format("FootprintOro: tick classificati con bid/ask veri {0:P0}, il resto con la regola del tick",
					tickTotali > 0 ? (double)tickConQuote / tickTotali : 0), TextPosition.BottomLeft);
			prezzoPrecedente = prezzo;

			long vol = (long)Math.Round(v);
			lock (blocco)
			{
				Barra b;
				if (!barre.TryGetValue(CurrentBar, out b))
				{
					b = new Barra();
					barre[CurrentBar] = b;
					barre.Remove(CurrentBar - CandeleMassime);
				}
				Cella c;
				if (!b.Livelli.TryGetValue(livello, out c))
				{
					c = new Cella();
					b.Livelli[livello] = c;
				}
				if (lato > 0) { c.Ask += vol; b.Delta += vol; }
				else { c.Bid += vol; b.Delta -= vol; }
				if (livello < b.Min) b.Min = livello;
			}
		}

		public override void OnRenderTargetChanged()
		{
			Libera();
			if (RenderTarget == null)
				return;
			brSfondo = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.07f, 0.08f, 0.10f, 1f));
			brAsk    = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.10f, 0.65f, 0.40f, 1f));
			brBid    = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.85f, 0.25f, 0.25f, 1f));
			brTesto  = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(1.00f, 1.00f, 1.00f, 1f));
			brPoc    = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(1.00f, 0.80f, 0.10f, 1f));
			brImbAsk = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.30f, 1.00f, 0.55f, 1f));
			brImbBid = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(1.00f, 0.45f, 0.45f, 1f));
		}

		// unisce le righe in blocchi da 'passo' (somma bid e ask)
		private SortedDictionary<double, Cella> Aggrega(SortedDictionary<double, Cella> src, double passo)
		{
			var out_ = new SortedDictionary<double, Cella>();
			foreach (var kv in src)
			{
				double key = Instrument.MasterInstrument.RoundToTickSize(Math.Floor(kv.Key / passo + 1e-9) * passo);
				Cella c;
				if (!out_.TryGetValue(key, out c)) { c = new Cella(); out_[key] = c; }
				c.Bid += kv.Value.Bid; c.Ask += kv.Value.Ask;
			}
			return out_;
		}
		private static string Corto(long v)
		{
			if (v >= 10000) return (v / 1000).ToString() + "k";
			if (v >= 1000) return (v / 1000.0).ToString("0.0", System.Globalization.CultureInfo.InvariantCulture) + "k";
			return v.ToString();
		}

		private void Libera()
		{
			foreach (var br in new[] { brSfondo, brAsk, brBid, brTesto, brPoc, brImbAsk, brImbBid })
				if (br != null && !br.IsDisposed) br.Dispose();
			brSfondo = brAsk = brBid = brTesto = brPoc = brImbAsk = brImbBid = null;
		}

		protected override void OnRender(ChartControl chartControl, ChartScale chartScale)
		{
			if (brSfondo == null || ChartBars == null || Bars == null || IsInHitTest)
				return;

			double baseRiga = Instrument.MasterInstrument.TickSize * TickPerRiga;
			float riga0 = Math.Abs(chartScale.GetYByValue(0) - chartScale.GetYByValue(baseRiga));
			if (riga0 < 0.05f) riga0 = 0.05f;
			// righe automatiche: con poco zoom unisce le righe vicine finche' ogni riga e' alta almeno AltezzaRiga pixel
			int k = RigheAutomatiche ? Math.Max(1, (int)Math.Ceiling(AltezzaRiga / riga0)) : 1;
			double tickSize = baseRiga * k;
			float riga = Math.Max(1f, riga0 * k);
			float mezzo = Math.Max(3f, chartControl.Properties.BarDistance * 0.45f); // spazio a sinistra per la mini candela
			float fontLargo = (mezzo - 4f) / (0.62f * 3.3f);                           // ~3 cifre devono stare nella mezza cella
			float font = Math.Min((float)DimensioneNumeri, Math.Min(riga * 0.85f, fontLargo));
			bool conTesto = font >= 7f;
			font = Math.Max(7f, font);

			var aaVecchio = RenderTarget.AntialiasMode;
			RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.Aliased;

			using (var tfBid = new SharpDX.DirectWrite.TextFormat(Core.Globals.DirectWriteFactory, "Consolas",
				SharpDX.DirectWrite.FontWeight.Bold, SharpDX.DirectWrite.FontStyle.Normal, font))
			using (var tfAsk = new SharpDX.DirectWrite.TextFormat(Core.Globals.DirectWriteFactory, "Consolas",
				SharpDX.DirectWrite.FontWeight.Bold, SharpDX.DirectWrite.FontStyle.Normal, font))
			using (var tfDelta = new SharpDX.DirectWrite.TextFormat(Core.Globals.DirectWriteFactory, "Consolas",
				SharpDX.DirectWrite.FontWeight.Bold, SharpDX.DirectWrite.FontStyle.Normal, 11f))
			{
				tfBid.TextAlignment = SharpDX.DirectWrite.TextAlignment.Trailing;
				tfAsk.TextAlignment = SharpDX.DirectWrite.TextAlignment.Leading;
				tfDelta.TextAlignment = SharpDX.DirectWrite.TextAlignment.Center;
				foreach (var tf in new[] { tfBid, tfAsk, tfDelta })
				{
					tf.ParagraphAlignment = SharpDX.DirectWrite.ParagraphAlignment.Center;
					tf.WordWrapping = SharpDX.DirectWrite.WordWrapping.NoWrap;
				}

				lock (blocco)
				{
					for (int i = Math.Max(0, ChartBars.FromIndex); i <= ChartBars.ToIndex; i++)
					{
						Barra b;
						if (!barre.TryGetValue(i, out b) || b.Livelli.Count == 0)
							continue;
						SortedDictionary<double, Cella> liv = k == 1 ? b.Livelli : Aggrega(b.Livelli, tickSize);

						float x = chartControl.GetXByBarIndex(ChartBars, i);
						long massimo = 1, pocVol = -1;
						double poc = 0;
						foreach (var kv in liv)
						{
							long tot = kv.Value.Bid + kv.Value.Ask;
							if (tot > pocVol) { pocVol = tot; poc = kv.Key; }
							massimo = Math.Max(massimo, Math.Max(kv.Value.Bid, kv.Value.Ask));
						}

						foreach (var kv in liv)
						{
							float y = chartScale.GetYByValue(kv.Key + tickSize / 2.0);
							float alto = y - riga / 2f;
							float h = Math.Max(1f, riga - 1f);
							var rBid = new SharpDX.RectangleF(x - mezzo, alto, mezzo - 1f, h);
							var rAsk = new SharpDX.RectangleF(x + 1f, alto, mezzo - 1f, h);

							float scala = CelleTrasparenti ? 0.35f : 1f;
							if (!CelleTrasparenti)
							{
								RenderTarget.FillRectangle(rBid, brSfondo);
								RenderTarget.FillRectangle(rAsk, brSfondo);
							}
							brBid.Opacity = scala * (0.08f + 0.50f * kv.Value.Bid / (float)massimo);
							brAsk.Opacity = scala * (0.08f + 0.50f * kv.Value.Ask / (float)massimo);
							RenderTarget.FillRectangle(rBid, brBid);
							RenderTarget.FillRectangle(rAsk, brAsk);

							if (!conTesto)
								continue;

							Cella sotto, sopra;
							long bidSotto = liv.TryGetValue(Instrument.MasterInstrument.RoundToTickSize(kv.Key - tickSize), out sotto) ? sotto.Bid : 0;
							long askSopra = liv.TryGetValue(Instrument.MasterInstrument.RoundToTickSize(kv.Key + tickSize), out sopra) ? sopra.Ask : 0;
							bool imbAsk = kv.Value.Ask >= VolumeMinimoImbalance && kv.Value.Ask >= Rapporto * Math.Max(bidSotto, 1);
							bool imbBid = kv.Value.Bid >= VolumeMinimoImbalance && kv.Value.Bid >= Rapporto * Math.Max(askSopra, 1);

							RenderTarget.DrawText(Corto(kv.Value.Bid), tfBid,
								new SharpDX.RectangleF(x - mezzo, alto, mezzo - 3f, h), imbBid ? brImbBid : brTesto);
							RenderTarget.DrawText(Corto(kv.Value.Ask), tfAsk,
								new SharpDX.RectangleF(x + 3f, alto, mezzo - 3f, h), imbAsk ? brImbAsk : brTesto);
						}

						float yp = chartScale.GetYByValue(poc + tickSize / 2.0);
						RenderTarget.DrawRectangle(new SharpDX.RectangleF(x - mezzo, yp - riga / 2f, 2f * mezzo, Math.Max(1f, riga - 1f)), brPoc, 1.5f);

						float yDelta = chartScale.GetYByValue(b.Min) + 2f;
						var brD = b.Delta >= 0 ? brAsk : brBid;
						brD.Opacity = 1f;
						RenderTarget.DrawText((b.Delta > 0 ? "+" : "") + b.Delta, tfDelta,
							new SharpDX.RectangleF(x - mezzo - 10f, yDelta, 2f * mezzo + 20f, 14f), brD);

						// mini candela a sinistra delle celle: apertura, chiusura, massimo, minimo
						double o = Bars.GetOpen(i), hi = Bars.GetHigh(i), lo = Bars.GetLow(i), cl = Bars.GetClose(i);
						var brC = cl >= o ? brAsk : brBid;
						brC.Opacity = 1f;
						float xc = x - mezzo - 5f;
						float yo = chartScale.GetYByValue(o), ycl = chartScale.GetYByValue(cl);
						RenderTarget.DrawLine(new SharpDX.Vector2(xc, chartScale.GetYByValue(hi)), new SharpDX.Vector2(xc, chartScale.GetYByValue(lo)), brC, 1.2f);
						RenderTarget.FillRectangle(new SharpDX.RectangleF(xc - 2.5f, Math.Min(yo, ycl), 5f, Math.Max(1.5f, Math.Abs(yo - ycl))), brC);
					}

					// prezzo attuale: linea su tutto il grafico + riquadro sulla riga del prezzo nella candela in corso
					if (Bars.Count > 0 && ChartBars.ToIndex >= Bars.Count - 1)
					{
						double ultimo = Bars.GetClose(Bars.Count - 1);
						float yu = chartScale.GetYByValue(ultimo);
						brPoc.Opacity = 0.75f;
						RenderTarget.DrawLine(new SharpDX.Vector2(ChartPanel.X, yu), new SharpDX.Vector2(ChartPanel.X + ChartPanel.W, yu), brPoc, 1f);
						brPoc.Opacity = 1f;
						float xu = chartControl.GetXByBarIndex(ChartBars, Bars.Count - 1);
						double rigaUltimo = Instrument.MasterInstrument.RoundToTickSize(Math.Floor(ultimo / tickSize + 1e-9) * tickSize);
						float yr = chartScale.GetYByValue(rigaUltimo + tickSize / 2.0);
						RenderTarget.DrawRectangle(new SharpDX.RectangleF(xu - mezzo - 1f, yr - riga / 2f - 1f, 2f * mezzo + 2f, riga + 1f), brTesto, 2f);
					}
				}
			}
			brAsk.Opacity = 1f;
			brBid.Opacity = 1f;
			RenderTarget.AntialiasMode = aaVecchio;
		}

		#region Properties
		[Display(Name = "Righe automatiche", Description = "Con poco zoom unisce le righe vicine cosi' i numeri restano leggibili", Order = 7, GroupName = "Footprint")]
		public bool RigheAutomatiche { get; set; }

		[Range(6, 40)]
		[Display(Name = "Altezza minima riga (pixel)", Description = "Piu' alto = righe piu' grandi e meno numerose", Order = 8, GroupName = "Footprint")]
		public int AltezzaRiga { get; set; }

		[Range(7, 30)]
		[Display(Name = "Grandezza numeri", Description = "Massimo in punti; i numeri crescono fino a qui se la riga e' abbastanza alta", Order = 6, GroupName = "Footprint")]
		public int DimensioneNumeri { get; set; }

		[Range(1.0, 100.0)]
		[Display(Name = "Rapporto imbalance", Description = "Ask a p contro bid a p-1 tick (e viceversa)", Order = 1, GroupName = "Footprint")]
		public double Rapporto { get; set; }

		[Range(1, int.MaxValue)]
		[Display(Name = "Volume minimo imbalance", Order = 2, GroupName = "Footprint")]
		public int VolumeMinimoImbalance { get; set; }

		[Display(Name = "Celle trasparenti (per heatmap)", Description = "Niente sfondo pieno: si vede la HeatmapOro sotto", Order = 5, GroupName = "Footprint")]
		public bool CelleTrasparenti { get; set; }

		[Range(1, 1000)]
		[Display(Name = "Tick per riga", Description = "GC: 1 tick = 0,10 $; 5 = righe da 0,50 $", Order = 0, GroupName = "Footprint")]
		public int TickPerRiga { get; set; }

		[Range(10, 100000)]
		[Display(Name = "Candele tenute in memoria", Order = 3, GroupName = "Footprint")]
		public int CandeleMassime { get; set; }
		#endregion
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private FootprintOro[] cacheFootprintOro;
		public FootprintOro FootprintOro()
		{
			return FootprintOro(Input);
		}

		public FootprintOro FootprintOro(ISeries<double> input)
		{
			if (cacheFootprintOro != null)
				for (int idx = 0; idx < cacheFootprintOro.Length; idx++)
					if (cacheFootprintOro[idx] != null &&  cacheFootprintOro[idx].EqualsInput(input))
						return cacheFootprintOro[idx];
			return CacheIndicator<FootprintOro>(new FootprintOro(), input, ref cacheFootprintOro);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.FootprintOro FootprintOro()
		{
			return indicator.FootprintOro(Input);
		}

		public Indicators.FootprintOro FootprintOro(ISeries<double> input )
		{
			return indicator.FootprintOro(input);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.FootprintOro FootprintOro()
		{
			return indicator.FootprintOro(Input);
		}

		public Indicators.FootprintOro FootprintOro(ISeries<double> input )
		{
			return indicator.FootprintOro(input);
		}
	}
}

#endregion
