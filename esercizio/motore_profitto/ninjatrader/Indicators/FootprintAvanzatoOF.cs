// FootprintAvanzatoOF - Motore Profitto (20/11/2026). SOLO VISUALIZZAZIONE: non apre ordini. Basato su FootprintOro, in piu':
//  - 3 modi: 0 = bid x ask (classico), 1 = delta per livello (ask - bid, verde/rosso), 2 = volume per livello (istogramma)
//  - IMBALANCE diagonali colorati e STACK (>= MinStack livelli di fila): fascia estesa a destra finche' il prezzo non la attraversa
//  - ASTA NON FINITA: sul massimo/minimo della candela ci sono scambi sia sul bid sia sull'ask (rombo giallo): spesso il prezzo ci torna
//  - ESAURIMENTO: sul massimo/minimo pochissimo volume (<= EsaurimentoMax): nessuno spinge piu' in quella direzione (triangolo)
//  - SCAMBIO GROSSO: cella in cui c'e' stato un singolo scambio >= GrossoMin contratti (bordo bianco)
//  - TABELLA sotto le candele: volume, delta, delta %, delta minimo e massimo dentro la candela, delta cumulato di sessione (dalle 18:00 NY)
// Serve Tick Replay acceso per lo storico (lato di ogni scambio). Righe automatiche con poco zoom come FootprintOro.
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
	public class FootprintAvanzatoOF : Indicator
	{
		private class Cella { public long Bid, Ask, Max; }
		private class Barra
		{
			public readonly SortedDictionary<double, Cella> Livelli = new SortedDictionary<double, Cella>();
			public long Delta, Vol, DMin, DMax, Cum;
		}
		private class Stack { public double Lo, Hi; public int Lato, Da, A = -1; }

		private readonly Dictionary<int, Barra> barre = new Dictionary<int, Barra>();
		private readonly List<Stack> stacks = new List<Stack>();
		private readonly object blocco = new object();
		private double volPrecedente, prezzoPrecedente, ultimoAsk, ultimoBid;
		private int latoPrecedente = 1;
		private long cumSessione; private DateTime sessione = DateTime.MinValue;
		private TimeZoneInfo ny;
		private SharpDX.Direct2D1.SolidColorBrush brSfondo, brAsk, brBid, brTesto, brPoc, brImbAsk, brImbBid, brGiallo, brGrigio, brBianco, brCandSu, brCandGiu;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "FootprintAvanzatoOF";
				Description = "Footprint avanzato: bid x ask / delta / volume per livello, imbalance e stack estesi, aste non finite, esaurimento, scambi grossi, tabella statistiche. Solo visualizzazione.";
				Calculate = Calculate.OnEachTick; IsOverlay = true; DrawOnPricePanel = true; DisplayInDataBox = false; PaintPriceMarkers = false;
				IsSuspendedWhileInactive = false; MaximumBarsLookBack = MaximumBarsLookBack.Infinite;
				Modo = 0; TickPerRiga = 5; Rapporto = 3.0; VolumeMinimoImbalance = 5; MinStack = 3; EsaurimentoMax = 5; GrossoMin = 15;
				CandeleMassime = 400; DimensioneNumeri = 13; RigheAutomatiche = true; AltezzaRiga = 14; MostraTabella = true; MostraStack = true;
				MostraAste = false; TabellaCompleta = false;
			}
			else if (State == State.DataLoaded)
			{
				ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
				lock (blocco) { barre.Clear(); stacks.Clear(); }
			}
			else if (State == State.Terminated) Libera();
		}

		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.MarketDataType == MarketDataType.Last) { if (e.Ask > e.Bid && e.Bid > 0) { ultimoAsk = e.Ask; ultimoBid = e.Bid; } }
			else if (e.MarketDataType == MarketDataType.Ask) ultimoAsk = e.Price;
			else if (e.MarketDataType == MarketDataType.Bid) ultimoBid = e.Price;
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar == 0 && !Bars.IsTickReplay) Draw.TextFixed(this, "faAvviso", "FootprintAvanzatoOF: Tick Replay spento, conto solo da adesso", TextPosition.TopLeft);
			if (State == State.Historical && !Bars.IsTickReplay) return;
			if (IsFirstTickOfBar)
			{
				volPrecedente = 0;
				if (CurrentBar > 0) lock (blocco) ChiudiBarra(CurrentBar - 1);
			}
			double v = Volume[0] - volPrecedente; volPrecedente = Volume[0];
			if (v <= 0) return;
			double prezzo = Instrument.MasterInstrument.RoundToTickSize(Close[0]);
			double passo = TickPerRiga * TickSize;
			double livello = Instrument.MasterInstrument.RoundToTickSize(Math.Floor(prezzo / passo + 1e-9) * passo);
			bool q = ultimoAsk > ultimoBid && ultimoBid > 0;
			int lato = q && prezzo >= ultimoAsk ? 1 : q && prezzo <= ultimoBid ? -1 : prezzo > prezzoPrecedente ? 1 : prezzo < prezzoPrecedente ? -1 : latoPrecedente;
			latoPrecedente = lato; prezzoPrecedente = prezzo;
			DateTime ses = TimeZoneInfo.ConvertTime(Time[0], TimeZoneInfo.Local, ny).AddHours(6).Date;     // sessione CME dalle 18:00 NY
			if (ses != sessione) { sessione = ses; cumSessione = 0; }
			long vol = (long)Math.Round(v);
			lock (blocco)
			{
				Barra b;
				if (!barre.TryGetValue(CurrentBar, out b)) { b = new Barra(); barre[CurrentBar] = b; barre.Remove(CurrentBar - CandeleMassime); }
				Cella c; if (!b.Livelli.TryGetValue(livello, out c)) { c = new Cella(); b.Livelli[livello] = c; }
				if (lato > 0) { c.Ask += vol; b.Delta += vol; cumSessione += vol; } else { c.Bid += vol; b.Delta -= vol; cumSessione -= vol; }
				c.Max = Math.Max(c.Max, vol); b.Vol += vol;
				b.DMin = Math.Min(b.DMin, b.Delta); b.DMax = Math.Max(b.DMax, b.Delta); b.Cum = cumSessione;
				// gli stack aperti finiscono quando il prezzo li attraversa
				foreach (Stack s in stacks) if (s.A < 0 && CurrentBar > s.Da && prezzo > s.Lo && prezzo < s.Hi) s.A = CurrentBar;
			}
		}

		private void ChiudiBarra(int i)
		{
			Barra b; if (!barre.TryGetValue(i, out b) || !MostraStack) return;
			double passo = TickPerRiga * TickSize;
			for (int verso = 1; verso >= -1; verso -= 2)
			{
				int corsa = 0; double inizio = 0, prec = double.NaN;
				foreach (KeyValuePair<double, Cella> kv in b.Livelli)
				{
					bool imb = Imb(b.Livelli, kv.Key, kv.Value, passo, verso);
					bool vicino = !double.IsNaN(prec) && Math.Abs(kv.Key - prec - passo) < passo * 0.1;
					if (imb && (corsa == 0 || vicino)) { if (corsa == 0) inizio = kv.Key; corsa++; }
					else
					{
						if (corsa >= MinStack) stacks.Add(new Stack { Lo = inizio, Hi = prec + passo, Lato = verso, Da = i });
						corsa = imb ? 1 : 0; if (imb) inizio = kv.Key;
					}
					prec = kv.Key;
				}
				if (corsa >= MinStack) stacks.Add(new Stack { Lo = inizio, Hi = prec + passo, Lato = verso, Da = i });
			}
			stacks.RemoveAll(s => s.Da < i - CandeleMassime);
		}

		private bool Imb(SortedDictionary<double, Cella> liv, double p, Cella c, double passo, int verso)
		{
			Cella x;
			if (verso > 0)
			{
				long bidSotto = liv.TryGetValue(Instrument.MasterInstrument.RoundToTickSize(p - passo), out x) ? x.Bid : 0;
				return c.Ask >= VolumeMinimoImbalance && c.Ask >= Rapporto * Math.Max(bidSotto, 1);
			}
			long askSopra = liv.TryGetValue(Instrument.MasterInstrument.RoundToTickSize(p + passo), out x) ? x.Ask : 0;
			return c.Bid >= VolumeMinimoImbalance && c.Bid >= Rapporto * Math.Max(askSopra, 1);
		}

		public override void OnRenderTargetChanged()
		{
			Libera();
			if (RenderTarget == null) return;
			brSfondo = Pennello(0.07f, 0.08f, 0.10f); brAsk = Pennello(0.10f, 0.65f, 0.40f); brBid = Pennello(0.85f, 0.25f, 0.25f);
			brTesto = Pennello(0.95f, 0.95f, 0.95f); brPoc = Pennello(1.00f, 0.80f, 0.10f); brImbAsk = Pennello(0.30f, 1.00f, 0.55f);
			brImbBid = Pennello(1.00f, 0.45f, 0.45f); brGiallo = Pennello(1.00f, 0.90f, 0.20f); brGrigio = Pennello(0.55f, 0.58f, 0.62f); brBianco = Pennello(1f, 1f, 1f);
			brCandSu = Pennello(0.15f, 0.85f, 0.35f); brCandGiu = Pennello(0.62f, 0.30f, 0.95f);   // candele: verde su, viola giu'
		}
		private SharpDX.Direct2D1.SolidColorBrush Pennello(float r, float g, float b) { return new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(r, g, b, 1f)); }
		private void Libera()
		{
			foreach (var br in new[] { brSfondo, brAsk, brBid, brTesto, brPoc, brImbAsk, brImbBid, brGiallo, brGrigio, brBianco, brCandSu, brCandGiu })
				if (br != null && !br.IsDisposed) br.Dispose();
			brSfondo = brAsk = brBid = brTesto = brPoc = brImbAsk = brImbBid = brGiallo = brGrigio = brBianco = brCandSu = brCandGiu = null;
		}
		private SortedDictionary<double, Cella> Aggrega(SortedDictionary<double, Cella> src, double passo)
		{
			var o = new SortedDictionary<double, Cella>();
			foreach (var kv in src)
			{
				double key = Instrument.MasterInstrument.RoundToTickSize(Math.Floor(kv.Key / passo + 1e-9) * passo);
				Cella c; if (!o.TryGetValue(key, out c)) { c = new Cella(); o[key] = c; }
				c.Bid += kv.Value.Bid; c.Ask += kv.Value.Ask; c.Max = Math.Max(c.Max, kv.Value.Max);
			}
			return o;
		}
		private static string Corto(long v)
		{
			long a = Math.Abs(v); string s = v < 0 ? "-" : "";
			if (a >= 10000) return s + (a / 1000) + "k";
			if (a >= 1000) return s + (a / 1000.0).ToString("0.0", CultureInfo.InvariantCulture) + "k";
			return v.ToString();
		}

		protected override void OnRender(ChartControl chartControl, ChartScale chartScale)
		{
			if (brSfondo == null || ChartBars == null || Bars == null || IsInHitTest) return;
			double baseRiga = TickSize * TickPerRiga;
			float riga0 = Math.Max(0.05f, Math.Abs(chartScale.GetYByValue(0) - chartScale.GetYByValue(baseRiga)));
			int k = RigheAutomatiche ? Math.Max(1, (int)Math.Ceiling(AltezzaRiga / riga0)) : 1;
			double passo = baseRiga * k; float riga = Math.Max(1f, riga0 * k);
			float mezzo = Math.Max(3f, chartControl.Properties.BarDistance * 0.45f);
			float font = Math.Min((float)DimensioneNumeri, Math.Min(riga * 0.85f, (mezzo - 4f) / (0.62f * 3.3f)));
			bool conTesto = font >= 7f; font = Math.Max(7f, font);
			var aa = RenderTarget.AntialiasMode; RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.Aliased;
			using (var tfB = Formato(font, SharpDX.DirectWrite.TextAlignment.Trailing))
			using (var tfA = Formato(font, SharpDX.DirectWrite.TextAlignment.Leading))
			using (var tfC = Formato(font, SharpDX.DirectWrite.TextAlignment.Center))
			using (var tfT = Formato(10f, SharpDX.DirectWrite.TextAlignment.Center))
			using (var tfL = Formato(10f, SharpDX.DirectWrite.TextAlignment.Leading))
			lock (blocco)
			{
				// stack estesi (sotto alle celle)
				if (MostraStack)
					foreach (Stack s in stacks)
					{
						if (s.A >= 0 && s.A < ChartBars.FromIndex) continue;
						if (s.Da > ChartBars.ToIndex) continue;
						float x0 = chartControl.GetXByBarIndex(ChartBars, Math.Max(s.Da, ChartBars.FromIndex));
						float x1 = s.A >= 0 ? chartControl.GetXByBarIndex(ChartBars, Math.Min(s.A, ChartBars.ToIndex)) : ChartPanel.X + ChartPanel.W;
						float y0 = chartScale.GetYByValue(s.Hi), y1 = chartScale.GetYByValue(s.Lo);
						var br = s.Lato > 0 ? brImbAsk : brImbBid; br.Opacity = s.A >= 0 ? 0.10f : 0.22f;
						RenderTarget.FillRectangle(new SharpDX.RectangleF(x0, y0, Math.Max(1f, x1 - x0), Math.Max(1f, y1 - y0)), br);
					}
				int[] righeTab = TabellaCompleta ? new[] { 0, 1, 2, 3, 4, 5 } : new[] { 0, 1, 5 };
				bool tabOk = MostraTabella && 2f * mezzo >= 26f;
				float yTab = ChartPanel.Y + ChartPanel.H - righeTab.Length * 12f - 4f;
				for (int i = Math.Max(0, ChartBars.FromIndex); i <= ChartBars.ToIndex; i++)
				{
					Barra b; if (!barre.TryGetValue(i, out b) || b.Livelli.Count == 0) continue;
					var liv = k == 1 ? b.Livelli : Aggrega(b.Livelli, passo);
					float x = chartControl.GetXByBarIndex(ChartBars, i);
					long massimo = 1, pocVol = -1, maxDelta = 1; double poc = 0;
					foreach (var kv in liv)
					{
						long tot = kv.Value.Bid + kv.Value.Ask;
						if (tot > pocVol) { pocVol = tot; poc = kv.Key; }
						massimo = Math.Max(massimo, Modo == 2 ? tot : Math.Max(kv.Value.Bid, kv.Value.Ask)); maxDelta = Math.Max(maxDelta, Math.Abs(kv.Value.Ask - kv.Value.Bid));
					}
					double alto = double.MinValue, basso = double.MaxValue;
					foreach (var kv in liv) { alto = Math.Max(alto, kv.Key); basso = Math.Min(basso, kv.Key); }
					foreach (var kv in liv)
					{
						Cella c = kv.Value;
						float y = chartScale.GetYByValue(kv.Key + passo / 2.0), top = y - riga / 2f, h = Math.Max(1f, riga - 1f);
						var rB = new SharpDX.RectangleF(x - mezzo, top, mezzo - 1f, h); var rA = new SharpDX.RectangleF(x + 1f, top, mezzo - 1f, h);
						var rT = new SharpDX.RectangleF(x - mezzo, top, 2f * mezzo - 1f, h);
						RenderTarget.FillRectangle(rT, brSfondo);
						bool iA = Imb(liv, kv.Key, c, passo, 1), iB = Imb(liv, kv.Key, c, passo, -1);
						if (Modo == 0)
						{
							brBid.Opacity = 0.08f + 0.5f * c.Bid / (float)massimo; brAsk.Opacity = 0.08f + 0.5f * c.Ask / (float)massimo;
							RenderTarget.FillRectangle(rB, brBid); RenderTarget.FillRectangle(rA, brAsk);
							if (conTesto)
							{
								RenderTarget.DrawText(Corto(c.Bid), tfB, new SharpDX.RectangleF(x - mezzo, top, mezzo - 3f, h), iB ? brImbBid : brTesto);
								RenderTarget.DrawText(Corto(c.Ask), tfA, new SharpDX.RectangleF(x + 3f, top, mezzo - 3f, h), iA ? brImbAsk : brTesto);
							}
						}
						else if (Modo == 1)
						{
							long d = c.Ask - c.Bid; var br = d >= 0 ? brAsk : brBid; br.Opacity = 0.10f + 0.6f * Math.Abs(d) / (float)maxDelta;
							RenderTarget.FillRectangle(rT, br);
							if (conTesto) RenderTarget.DrawText((d > 0 ? "+" : "") + Corto(d), tfC, rT, iA ? brImbAsk : iB ? brImbBid : brTesto);
						}
						else
						{
							long tot = c.Bid + c.Ask; float w = (2f * mezzo - 2f) * tot / massimo;
							brGrigio.Opacity = 0.75f; RenderTarget.FillRectangle(new SharpDX.RectangleF(x - mezzo, top, Math.Max(1f, w), h), brGrigio);
							if (conTesto) RenderTarget.DrawText(Corto(tot), tfA, new SharpDX.RectangleF(x - mezzo + 2f, top, 2f * mezzo, h), brTesto);
						}
						if (c.Max >= GrossoMin) RenderTarget.DrawRectangle(rT, brBianco, 1.2f);
						// aste non finite ed esaurimento sugli estremi
						if (kv.Key == alto || kv.Key == basso)
						{
							bool sopra = kv.Key == alto; float ym = sopra ? top - 5f : top + h + 5f;
							if (MostraAste && c.Bid >= VolumeMinimoImbalance && c.Ask >= VolumeMinimoImbalance)
							{
								var g = new SharpDX.Vector2(x + mezzo + 4f, ym);
								brGiallo.Opacity = 1f; RenderTarget.FillEllipse(new SharpDX.Direct2D1.Ellipse(g, 3f, 3f), brGiallo);
							}
							if (MostraAste && c.Bid + c.Ask <= EsaurimentoMax)
							{
								brTesto.Opacity = 1f;
								RenderTarget.DrawText(sopra ? "v" : "^", tfC, new SharpDX.RectangleF(x - mezzo - 14f, top, 12f, h), brGiallo);
							}
						}
					}
					float yp = chartScale.GetYByValue(poc + passo / 2.0);
					RenderTarget.DrawRectangle(new SharpDX.RectangleF(x - mezzo, yp - riga / 2f, 2f * mezzo, Math.Max(1f, riga - 1f)), brPoc, 1.5f);
					// mini candela
					double o = Bars.GetOpen(i), hi = Bars.GetHigh(i), lo = Bars.GetLow(i), cl = Bars.GetClose(i);
					var brC = cl >= o ? brCandSu : brCandGiu; brC.Opacity = 1f; float xc = x - mezzo - 5f;
					float yo = chartScale.GetYByValue(o), ycl = chartScale.GetYByValue(cl);
					RenderTarget.DrawLine(new SharpDX.Vector2(xc, chartScale.GetYByValue(hi)), new SharpDX.Vector2(xc, chartScale.GetYByValue(lo)), brC, 1.2f);
					RenderTarget.FillRectangle(new SharpDX.RectangleF(xc - 2.5f, Math.Min(yo, ycl), 5f, Math.Max(1.5f, Math.Abs(yo - ycl))), brC);
					// tabella
					if (tabOk)
					{
						string[] val = { Corto(b.Vol), (b.Delta > 0 ? "+" : "") + Corto(b.Delta), b.Vol > 0 ? (100.0 * b.Delta / b.Vol).ToString("0", CultureInfo.InvariantCulture) + "%" : "-",
							Corto(b.DMin), "+" + Corto(b.DMax), Corto(b.Cum) };
						for (int j = 0; j < righeTab.Length; j++)
						{
							int r = righeTab[j];
							var rr = new SharpDX.RectangleF(x - mezzo, yTab + j * 12f, 2f * mezzo, 12f);
							brSfondo.Opacity = 0.85f; RenderTarget.FillRectangle(rr, brSfondo); brSfondo.Opacity = 1f;
							long segno = r == 0 ? 0 : r == 1 || r == 2 ? b.Delta : r == 3 ? -1 : r == 4 ? 1 : b.Cum;
							var bt = segno > 0 ? brImbAsk : segno < 0 ? brImbBid : brTesto;
							RenderTarget.DrawText(val[r], tfT, rr, bt);
						}
					}
				}
				if (tabOk)
				{
					string[] nomi = { "Volume", "Delta", "Delta %", "Delta min", "Delta max", "Delta cum." };
					for (int j = 0; j < righeTab.Length; j++)
					{
						var rl = new SharpDX.RectangleF(ChartPanel.X, yTab + j * 12f, 72f, 12f);
						RenderTarget.FillRectangle(rl, brSfondo);
						RenderTarget.DrawText(nomi[righeTab[j]], tfL, new SharpDX.RectangleF(ChartPanel.X + 3f, yTab + j * 12f, 70f, 12f), brGrigio);
					}
				}
			}
			brAsk.Opacity = brBid.Opacity = brImbAsk.Opacity = brImbBid.Opacity = brGrigio.Opacity = 1f;
			RenderTarget.AntialiasMode = aa;
		}
		private SharpDX.DirectWrite.TextFormat Formato(float size, SharpDX.DirectWrite.TextAlignment al)
		{
			var tf = new SharpDX.DirectWrite.TextFormat(Core.Globals.DirectWriteFactory, "Consolas", SharpDX.DirectWrite.FontWeight.Bold, SharpDX.DirectWrite.FontStyle.Normal, size);
			tf.TextAlignment = al; tf.ParagraphAlignment = SharpDX.DirectWrite.ParagraphAlignment.Center; tf.WordWrapping = SharpDX.DirectWrite.WordWrapping.NoWrap;
			return tf;
		}

		#region Properties
		[Range(0, 2)][Display(Name = "Modo (0 bid x ask, 1 delta, 2 volume)", Order = 0, GroupName = "Footprint")]
		public int Modo { get; set; }
		[Range(1, 1000)][Display(Name = "Tick per riga", Description = "GC: 5 = righe da 0,50 $", Order = 1, GroupName = "Footprint")]
		public int TickPerRiga { get; set; }
		[Range(1.0, 100.0)][Display(Name = "Rapporto imbalance", Order = 2, GroupName = "Footprint")]
		public double Rapporto { get; set; }
		[Range(1, int.MaxValue)][Display(Name = "Volume minimo imbalance", Order = 3, GroupName = "Footprint")]
		public int VolumeMinimoImbalance { get; set; }
		[Range(2, 20)][Display(Name = "Stack: livelli consecutivi", Order = 4, GroupName = "Footprint")]
		public int MinStack { get; set; }
		[Display(Name = "Mostra stack estesi", Order = 5, GroupName = "Footprint")]
		public bool MostraStack { get; set; }
		[Range(0, 1000)][Display(Name = "Esaurimento: volume massimo sull'estremo", Order = 6, GroupName = "Footprint")]
		public int EsaurimentoMax { get; set; }
		[Range(1, 100000)][Display(Name = "Scambio grosso: contratti", Description = "GC: 15 come il bot", Order = 7, GroupName = "Footprint")]
		public int GrossoMin { get; set; }
		[Display(Name = "Mostra tabella statistiche", Description = "Compare solo se le candele sono abbastanza larghe (zoom)", Order = 8, GroupName = "Footprint")]
		public bool MostraTabella { get; set; }
		[Display(Name = "Tabella completa (6 righe)", Description = "No = volume, delta, delta cumulato", Order = 13, GroupName = "Footprint")]
		public bool TabellaCompleta { get; set; }
		[Display(Name = "Mostra aste non finite / esaurimento", Description = "Sull'oro sono molto frequenti: spenti di base", Order = 14, GroupName = "Footprint")]
		public bool MostraAste { get; set; }
		[Range(7, 30)][Display(Name = "Grandezza numeri", Order = 9, GroupName = "Footprint")]
		public int DimensioneNumeri { get; set; }
		[Display(Name = "Righe automatiche", Order = 10, GroupName = "Footprint")]
		public bool RigheAutomatiche { get; set; }
		[Range(6, 40)][Display(Name = "Altezza minima riga (pixel)", Order = 11, GroupName = "Footprint")]
		public int AltezzaRiga { get; set; }
		[Range(10, 100000)][Display(Name = "Candele tenute in memoria", Order = 12, GroupName = "Footprint")]
		public int CandeleMassime { get; set; }
		#endregion
	}
}
