// HeatmapOro - heat map del book (Level 2) nel tempo, profilo del book attuale e bolle dei grossi scambi (NinjaTrader 8)
// Colori: blu = poca liquidita', ciano/giallo = tanta, arancio = muro. Scala sul 97o percentile delle celle visibili.
// Il book NON ha storico dal feed: l'indicatore lo registra su disco (Documenti\NinjaTrader 8\heatmap) e lo ricarica all'avvio,
// cosi' la mappa si accumula giorno dopo giorno. Le bolle usano i tick (con Tick Replay anche lo storico).
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Text;
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
	public class HeatmapOro : Indicator
	{
		private class Livello { public double Prezzo; public long Vol; }
		private class Colonna { public DateTime T; public double[] Prezzi; public long[] Vol; public bool[] Ask; public bool[] Ricordo; public double Ultimo; }
		private class Memoria { public long Vol; public bool Ask; public DateTime Visto; }
		private readonly Dictionary<double, Memoria> memoria = new Dictionary<double, Memoria>();

		// aggiunge alla fotografia i muri visti prima e usciti dai 10 livelli del feed (ultimo valore visto)
		private Colonna Arricchisci(Colonna raw)
		{
			if (!MemoriaLivelli || raw.Prezzi.Length == 0)
				return raw;
			double bestAsk = double.MaxValue, bestBid = double.MinValue, minVis = double.MaxValue, maxVis = double.MinValue;
			var visti = new HashSet<double>();
			for (int k = 0; k < raw.Prezzi.Length; k++)
			{
				double p = raw.Prezzi[k];
				if (raw.Vol[k] <= 0) continue;
				visti.Add(p);
				if (raw.Ask[k]) bestAsk = Math.Min(bestAsk, p); else bestBid = Math.Max(bestBid, p);
				minVis = Math.Min(minVis, p); maxVis = Math.Max(maxVis, p);
				memoria[p] = new Memoria { Vol = raw.Vol[k], Ask = raw.Ask[k], Visto = raw.T };
			}
			var via = new List<double>();
			foreach (var kv in memoria)
			{
				double p = kv.Key;
				if (visti.Contains(p)) continue;
				bool dentroFinestra = p >= minVis && p <= maxVis;            // il feed lo vede e dice che non c'e' piu'
				bool attraversato = kv.Value.Ask ? p < bestAsk : p > bestBid;  // il prezzo ci e' passato sopra
				bool scaduto = (raw.T - kv.Value.Visto).TotalMinutes > MemoriaMinuti;
				bool piccolo = kv.Value.Vol < sogliaMuro;                      // fuori dal book si ricordano solo i muri
				if (dentroFinestra || attraversato || scaduto || piccolo) via.Add(p);
			}
			foreach (var p in via) memoria.Remove(p);
			int n = memoria.Count;
			var c = new Colonna { T = raw.T, Ultimo = raw.Ultimo, Prezzi = new double[n], Vol = new long[n], Ask = new bool[n], Ricordo = new bool[n] };
			int i = 0;
			foreach (var kv in memoria)
			{
				c.Prezzi[i] = kv.Key; c.Vol[i] = kv.Value.Vol; c.Ask[i] = kv.Value.Ask; c.Ricordo[i] = !visti.Contains(kv.Key); i++;
			}
			return c;
		}
		private class Scambio { public DateTime T; public double P; public long V; public int Lato; }

		private readonly List<Livello> libroAsk = new List<Livello>();
		private readonly List<Livello> libroBid = new List<Livello>();
		private readonly List<Colonna> colonne = new List<Colonna>();
		private readonly List<Scambio> scambi = new List<Scambio>();
		private readonly object blocco = new object();
		private DateTime ultimoScatto = DateTime.MinValue;
		private bool profonditaRicevuta;
		private DateTime avvio;
		private double ultimoAsk, ultimoBid, prezzoPrec;
		private int latoPrec = 1;
		private double passoMemoriaMs = 1000;
		private DateTime ultimoInMemoria = DateTime.MinValue;
		private bool registraAttivo;

		// un solo file per strumento e giorno, condiviso fra tutti i grafici aperti
		private class Registratore { public StreamWriter W; public DateTime Ultimo; }
		private static readonly Dictionary<string, Registratore> registratori = new Dictionary<string, Registratore>();
		private static readonly object bloccoFile = new object();
		private static int istanzeRegistranti;

		private SharpDX.Direct2D1.SolidColorBrush brCella, brAsk, brBid, brTesto, brBordo, brLinea;

		// ---- zone di ordini: muri grossi che restano nel book (solo livelli visti davvero, non la memoria)
		private class Zona { public double Prezzo; public bool Ask; public DateTime Inizio, Fine; public long VolMax; public bool Attiva; }
		private readonly List<Zona> zoneChiuse = new List<Zona>();
		private readonly Dictionary<string, Zona> zoneAperte = new Dictionary<string, Zona>();
		private readonly List<long> campioni = new List<long>();
		private int campIdx, contaFoto;
		private double sogliaMuro = double.MaxValue;

		private void AggiornaZone(Colonna raw)
		{
			for (int k = 0; k < raw.Vol.Length; k++)
			{
				if (raw.Vol[k] <= 0) continue;
				if (campioni.Count < 20000) campioni.Add(raw.Vol[k]);
				else { campioni[campIdx] = raw.Vol[k]; campIdx = (campIdx + 1) % 20000; }
			}
			if (++contaFoto % 100 == 0 && campioni.Count >= 300)
			{
				var ord = new List<long>(campioni);
				ord.Sort();
				sogliaMuro = Math.Max(2, ord[Math.Min(ord.Count - 1, (int)(ord.Count * PercentileMuro / 100.0))]);
			}
			if (sogliaMuro == double.MaxValue)
				return;
			var presenti = new HashSet<string>();
			for (int k = 0; k < raw.Vol.Length; k++)
			{
				if (raw.Vol[k] < sogliaMuro) continue;
				string chiave = (raw.Ask[k] ? "A" : "B") + raw.Prezzi[k].ToString(CultureInfo.InvariantCulture);
				presenti.Add(chiave);
				Zona z;
				if (zoneAperte.TryGetValue(chiave, out z)) { z.Fine = raw.T; z.VolMax = Math.Max(z.VolMax, raw.Vol[k]); }
				else zoneAperte[chiave] = new Zona { Prezzo = raw.Prezzi[k], Ask = raw.Ask[k], Inizio = raw.T, Fine = raw.T, VolMax = raw.Vol[k], Attiva = true };
			}
			var chiuse = new List<string>();
			foreach (var kv in zoneAperte)
				if (!presenti.Contains(kv.Key) && (raw.T - kv.Value.Fine).TotalSeconds > 5) chiuse.Add(kv.Key);  // 5 s di tolleranza
			foreach (var ch in chiuse)
			{
				var z = zoneAperte[ch];
				zoneAperte.Remove(ch);
				z.Attiva = false;
				if ((z.Fine - z.Inizio).TotalSeconds >= DurataMuroSec)
				{
					zoneChiuse.Add(z);
					if (zoneChiuse.Count > 3000) zoneChiuse.RemoveAt(0);
				}
			}
		}

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description = "Heat map del book (Level 2), profilo del book e bolle dei grossi scambi";
				Name = "HeatmapOro";
				Calculate = Calculate.OnEachTick;
				IsOverlay = true;
				DrawOnPricePanel = true;
				DisplayInDataBox = false;
				PaintPriceMarkers = false;
				IsSuspendedWhileInactive = false;
				MaximumBarsLookBack = MaximumBarsLookBack.Infinite;
				IntervalloMs = 1000;
				ColonneMassime = 30000;
				SogliaBolla = 30;
				RegistraSuDisco = true;
				GiorniDaCaricare = 3;
				MemoriaLivelli = true;
				MemoriaMinuti = 30;
				LarghezzaProfilo = 140;
				Percentile = 99;
				Pulizia = 0.12;
				PercentileMuro = 95;
				DurataMuroSec = 60;
				ZoneMassime = 8;
				NascondiCandele = true;
			}
			else if (State == State.DataLoaded)
			{
				lock (blocco)
				{
					libroAsk.Clear(); libroBid.Clear(); colonne.Clear(); scambi.Clear(); memoria.Clear();
					zoneChiuse.Clear(); zoneAperte.Clear(); campioni.Clear(); campIdx = 0; contaFoto = 0; sogliaMuro = double.MaxValue;
				}
				avvio = DateTime.Now;
				passoMemoriaMs = Math.Max(IntervalloMs, PeriodoMs() / 60.0);
				CaricaDaDisco();
				if (RegistraSuDisco)
				{
					lock (bloccoFile) istanzeRegistranti++;
					registraAttivo = true;
				}
			}
			else if (State == State.Historical)
			{
				SetZOrder(-1); // dietro alle candele
			}
			else if (State == State.Terminated)
			{
				Libera();
				if (registraAttivo)
				{
					registraAttivo = false;
					lock (bloccoFile)
					{
						istanzeRegistranti--;
						if (istanzeRegistranti <= 0)
						{
							foreach (var r in registratori.Values) try { r.W.Dispose(); } catch { }
							registratori.Clear();
							istanzeRegistranti = 0;
						}
					}
				}
			}
		}

		private double PeriodoMs()
		{
			if (BarsPeriod == null) return IntervalloMs;
			switch (BarsPeriod.BarsPeriodType)
			{
				case BarsPeriodType.Second: return BarsPeriod.Value * 1000.0;
				case BarsPeriodType.Minute: return BarsPeriod.Value * 60000.0;
				case BarsPeriodType.Day: return BarsPeriod.Value * 86400000.0;
				default: return IntervalloMs;
			}
		}

		private string CartellaDati()
		{
			return Path.Combine(Core.Globals.UserDataDir, "heatmap");
		}

		private string FileDelGiorno(DateTime giorno)
		{
			return Path.Combine(CartellaDati(), Instrument.FullName.Replace(' ', '_') + "_" + giorno.ToString("yyyyMMdd") + ".txt");
		}

		// riga: ticks|ultimo|prezzo:vol:a;prezzo:vol:a;...  (a = 1 ask, 0 bid)
		private void Scrivi(Colonna c)
		{
			try
			{
				string percorso = FileDelGiorno(c.T.Date);
				lock (bloccoFile)
				{
					Registratore r;
					if (!registratori.TryGetValue(percorso, out r))
					{
						Directory.CreateDirectory(CartellaDati());
						var fs = new FileStream(percorso, FileMode.Append, FileAccess.Write, FileShare.ReadWrite);
						r = new Registratore { W = new StreamWriter(fs, Encoding.ASCII), Ultimo = DateTime.MinValue };
						registratori[percorso] = r;
					}
					if (c.T <= r.Ultimo)
						return;
					r.Ultimo = c.T;
					var sb = new StringBuilder();
					sb.Append(c.T.Ticks).Append('|').Append(c.Ultimo.ToString(CultureInfo.InvariantCulture)).Append('|');
					for (int k = 0; k < c.Prezzi.Length; k++)
					{
						if (k > 0) sb.Append(';');
						sb.Append(c.Prezzi[k].ToString(CultureInfo.InvariantCulture)).Append(':').Append(c.Vol[k]).Append(':').Append(c.Ask[k] ? '1' : '0');
					}
					r.W.WriteLine(sb.ToString());
					r.W.Flush();
				}
			}
			catch { }
		}

		private void CaricaDaDisco()
		{
			try
			{
				DateTime prossimo = DateTime.MinValue;
				for (int g = GiorniDaCaricare - 1; g >= 0; g--)
				{
					string percorso = FileDelGiorno(DateTime.Now.Date.AddDays(-g));
					if (!File.Exists(percorso)) continue;
					using (var fs = new FileStream(percorso, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
					using (var rd = new StreamReader(fs))
					{
						string riga;
						while ((riga = rd.ReadLine()) != null)
						{
							var parti = riga.Split('|');
							if (parti.Length < 3) continue;
							long ticks;
							if (!long.TryParse(parti[0], out ticks)) continue;
							var t = new DateTime(ticks);
							var liv = parti[2].Length > 0 ? parti[2].Split(';') : new string[0];
							var c = new Colonna { T = t, Prezzi = new double[liv.Length], Vol = new long[liv.Length], Ask = new bool[liv.Length] };
							double.TryParse(parti[1], NumberStyles.Float, CultureInfo.InvariantCulture, out c.Ultimo);
							for (int k = 0; k < liv.Length; k++)
							{
								var x = liv[k].Split(':');
								if (x.Length < 3) continue;
								double.TryParse(x[0], NumberStyles.Float, CultureInfo.InvariantCulture, out c.Prezzi[k]);
								long.TryParse(x[1], out c.Vol[k]);
								c.Ask[k] = x[2] == "1";
							}
							AggiornaZone(c);
							var ricca = Arricchisci(c);
							if (t < prossimo) continue;
							prossimo = t.AddMilliseconds(passoMemoriaMs);
							colonne.Add(ricca);
						}
					}
				}
				if (colonne.Count > ColonneMassime)
					colonne.RemoveRange(0, colonne.Count - ColonneMassime);
				if (colonne.Count > 0)
					ultimoInMemoria = colonne[colonne.Count - 1].T;
			}
			catch { }
		}

		protected override void OnBarUpdate()
		{
			// stile ATAS/Bookmap: niente candele, il prezzo e' la linea + le bolle
			if (NascondiCandele)
			{
				BarBrush = Brushes.Transparent;
				CandleOutlineBrush = Brushes.Transparent;
			}
		}

		protected override void OnMarketDepth(MarketDepthEventArgs e)
		{
			lock (blocco)
			{
				List<Livello> lato = e.MarketDataType == MarketDataType.Ask ? libroAsk
					: e.MarketDataType == MarketDataType.Bid ? libroBid : null;
				if (lato == null)
					return;
				if (e.Operation == Operation.Add)
				{
					if (e.Position <= lato.Count)
						lato.Insert(e.Position, new Livello { Prezzo = e.Price, Vol = e.Volume });
				}
				else if (e.Operation == Operation.Update)
				{
					if (e.Position < lato.Count) { lato[e.Position].Prezzo = e.Price; lato[e.Position].Vol = e.Volume; }
					else if (e.Position == lato.Count) lato.Add(new Livello { Prezzo = e.Price, Vol = e.Volume });
				}
				else if (e.Operation == Operation.Remove)
				{
					if (e.Position < lato.Count) lato.RemoveAt(e.Position);
				}
				profonditaRicevuta = true;

				DateTime t = e.Time;
				if ((t - ultimoScatto).TotalMilliseconds < IntervalloMs)
					return;
				ultimoScatto = t;
				int n = libroAsk.Count + libroBid.Count;
				var col = new Colonna { T = t, Prezzi = new double[n], Vol = new long[n], Ask = new bool[n], Ultimo = prezzoPrec };
				int k = 0;
				foreach (var l in libroAsk) { col.Prezzi[k] = l.Prezzo; col.Vol[k] = l.Vol; col.Ask[k] = true; k++; }
				foreach (var l in libroBid) { col.Prezzi[k] = l.Prezzo; col.Vol[k] = l.Vol; k++; }
				if (registraAttivo)
					Scrivi(col);
				AggiornaZone(col);
				var ricca = Arricchisci(col);
				if ((t - ultimoInMemoria).TotalMilliseconds >= passoMemoriaMs)
				{
					ultimoInMemoria = t;
					colonne.Add(ricca);
					if (colonne.Count > ColonneMassime)
						colonne.RemoveRange(0, colonne.Count - ColonneMassime);
				}
			}
		}

		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.MarketDataType == MarketDataType.Ask) { ultimoAsk = e.Price; return; }
			if (e.MarketDataType == MarketDataType.Bid) { ultimoBid = e.Price; return; }
			if (e.MarketDataType != MarketDataType.Last)
				return;
			if (e.Ask > e.Bid && e.Bid > 0) { ultimoAsk = e.Ask; ultimoBid = e.Bid; }

			int lato;
			if (ultimoAsk > ultimoBid && ultimoBid > 0 && e.Price >= ultimoAsk) lato = 1;
			else if (ultimoAsk > ultimoBid && ultimoBid > 0 && e.Price <= ultimoBid) lato = -1;
			else if (e.Price > prezzoPrec) lato = 1;
			else if (e.Price < prezzoPrec) lato = -1;
			else lato = latoPrec;
			latoPrec = lato;
			prezzoPrec = e.Price;

			if (e.Volume < SogliaBolla)
				return;
			lock (blocco)
			{
				scambi.Add(new Scambio { T = e.Time, P = e.Price, V = e.Volume, Lato = lato });
				if (scambi.Count > 20000)
					scambi.RemoveRange(0, scambi.Count - 20000);
			}
		}

		// zone migliori: i muri piu' forti (contratti x minuti) visibili, con etichetta; quelli ancora nel book arrivano al bordo destro
		private void DisegnaZone(ChartControl cc, ChartScale cs, float riga, float xMin, float xMax, double pMin, double pMax)
		{
			if (ZoneMassime <= 0)
				return;
			var cand = new List<Zona>(zoneChiuse);
			foreach (var z in zoneAperte.Values)
				if ((z.Fine - z.Inizio).TotalSeconds >= DurataMuroSec) cand.Add(z);
			var scelte = new List<Tuple<double, Zona, float, float>>();
			foreach (var z in cand)
			{
				if (z.Prezzo > pMax || z.Prezzo < pMin) continue;
				bool ok0, ok1;
				float x0 = XDelTempo(cc, z.Inizio, out ok0);
				float x1 = z.Attiva ? xMax : XDelTempo(cc, z.Fine, out ok1);
				if (!ok0 || x1 < xMin || x0 > xMax) continue;
				double forza = z.VolMax * Math.Max(1.0, (z.Fine - z.Inizio).TotalMinutes);
				scelte.Add(Tuple.Create(forza, z, Math.Max(x0, xMin), Math.Min(x1, xMax)));
			}
			scelte.Sort((a, b) => b.Item1.CompareTo(a.Item1));
			if (scelte.Count > ZoneMassime)
				scelte.RemoveRange(ZoneMassime, scelte.Count - ZoneMassime);

			using (var fillAsk = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(1f, 0.35f, 0.25f, 0.22f)))
			using (var fillBid = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.25f, 1f, 0.55f, 0.22f)))
			using (var bordoAsk = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(1f, 0.45f, 0.30f, 1f)))
			using (var bordoBid = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.35f, 1f, 0.60f, 1f)))
			using (var fondo = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.05f, 0.05f, 0.08f, 0.85f)))
			using (var tf = new SharpDX.DirectWrite.TextFormat(Core.Globals.DirectWriteFactory, "Segoe UI",
				SharpDX.DirectWrite.FontWeight.SemiBold, SharpDX.DirectWrite.FontStyle.Normal, 11f))
			{
				tf.WordWrapping = SharpDX.DirectWrite.WordWrapping.NoWrap;
				tf.ParagraphAlignment = SharpDX.DirectWrite.ParagraphAlignment.Center;
				var etichette = new List<SharpDX.RectangleF>();
				foreach (var sc in scelte)
				{
					var z = sc.Item2;
					float y = cs.GetYByValue(z.Prezzo);
					float h = Math.Max(riga, 5f);
					var r = new SharpDX.RectangleF(sc.Item3, y - h / 2f, Math.Max(2f, sc.Item4 - sc.Item3), h);
					RenderTarget.FillRectangle(r, z.Ask ? fillAsk : fillBid);
					RenderTarget.DrawRectangle(r, z.Ask ? bordoAsk : bordoBid, z.Attiva ? 2f : 1.2f);
					string testo = string.Format(CultureInfo.InvariantCulture, "{0} {1:0.0} · {2} lotti · {3:0} min{4}",
						z.Ask ? "SELL" : "BUY", z.Prezzo, z.VolMax, (z.Fine - z.Inizio).TotalMinutes, z.Attiva ? " · attivo" : "");
					float lx = z.Attiva ? sc.Item4 - LarghezzaProfilo - 215f : sc.Item4 + 4f;
					lx = Math.Max(xMin + 2f, Math.Min(lx, xMax - 210f));
					var rt = new SharpDX.RectangleF(lx, y - 9f, 205f, 18f);
					// niente etichette sovrapposte: le sposto (sell in su, buy in giu') finche' c'e' spazio
					for (int prova = 0; prova < 12; prova++)
					{
						bool tocca = false;
						foreach (var u in etichette)
							if (rt.Left < u.Right && u.Left < rt.Right && rt.Top < u.Bottom && u.Top < rt.Bottom) { tocca = true; break; }
						if (!tocca) break;
						rt.Y += z.Ask ? -19f : 19f;
					}
					etichette.Add(rt);
					RenderTarget.FillRectangle(rt, fondo);
					RenderTarget.DrawText(" " + testo, tf, rt, z.Ask ? bordoAsk : bordoBid);
				}
			}
		}

		// x sullo schermo per un istante: dentro la candela in proporzione al tempo trascorso
		private float XDelTempo(ChartControl cc, DateTime t, out bool valido)
		{
			valido = false;
			if (Bars == null || Bars.Count == 0)
				return 0;
			int idx = Bars.GetBar(t);
			if (idx < 0)
				return 0;
			DateTime fine = Bars.GetTime(idx);
			DateTime inizio = idx > 0 ? Bars.GetTime(idx - 1) : fine.AddMinutes(-1);
			double durata = (fine - inizio).TotalMilliseconds;
			double fr = durata > 0 ? (t - inizio).TotalMilliseconds / durata : 1;
			fr = Math.Max(0, Math.Min(1, fr));
			float bd = cc.Properties.BarDistance;
			valido = true;
			return cc.GetXByBarIndex(ChartBars, idx) - bd / 2f + (float)fr * bd;
		}

		private static readonly float[][] scalaAsk =
		{
			// rosso scuro -> rosso -> arancio -> giallo (muri in vendita)
			new[] { 0.00f, 0.22f, 0.02f, 0.08f },
			new[] { 0.35f, 0.55f, 0.06f, 0.14f },
			new[] { 0.65f, 0.95f, 0.30f, 0.10f },
			new[] { 1.00f, 1.00f, 0.85f, 0.35f },
		};
		private static readonly float[][] scalaBid =
		{
			// blu notte -> blu -> verde -> verde chiaro (muri in acquisto)
			new[] { 0.00f, 0.02f, 0.06f, 0.28f },
			new[] { 0.35f, 0.08f, 0.22f, 0.65f },
			new[] { 0.65f, 0.15f, 0.75f, 0.30f },
			new[] { 1.00f, 0.70f, 1.00f, 0.55f },
		};

		private static SharpDX.Color4 Gradiente(float i, bool ask)
		{
			float[][] s = ask ? scalaAsk : scalaBid;
			i = Math.Max(0f, Math.Min(1f, i));
			for (int k = 1; k < s.Length; k++)
			{
				if (i <= s[k][0])
				{
					float f = (i - s[k - 1][0]) / (s[k][0] - s[k - 1][0]);
					return new SharpDX.Color4(
						s[k - 1][1] + f * (s[k][1] - s[k - 1][1]),
						s[k - 1][2] + f * (s[k][2] - s[k - 1][2]),
						s[k - 1][3] + f * (s[k][3] - s[k - 1][3]),
						0.85f);
				}
			}
			var u = s[s.Length - 1];
			return new SharpDX.Color4(u[1], u[2], u[3], 0.95f);
		}

		public override void OnRenderTargetChanged()
		{
			Libera();
			if (RenderTarget == null)
				return;
			brCella  = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0f, 0f, 0f, 1f));
			brAsk    = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.95f, 0.25f, 0.35f, 0.90f));
			brBid    = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.30f, 0.55f, 1.00f, 0.90f));
			brLinea  = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.55f, 0.75f, 1.00f, 1f));
			brTesto  = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(0.90f, 0.92f, 0.95f, 1f));
			brBordo  = new SharpDX.Direct2D1.SolidColorBrush(RenderTarget, new SharpDX.Color4(1f, 1f, 1f, 0.8f));
		}

		private void Libera()
		{
			foreach (var br in new[] { brCella, brAsk, brBid, brTesto, brBordo, brLinea })
				if (br != null && !br.IsDisposed) br.Dispose();
			brCella = brAsk = brBid = brTesto = brBordo = brLinea = null;
		}

		protected override void OnRender(ChartControl chartControl, ChartScale chartScale)
		{
			if (brCella == null || ChartBars == null || Bars == null || IsInHitTest)
				return;

			double tick = Instrument.MasterInstrument.TickSize;
			float riga = Math.Max(1f, Math.Abs(chartScale.GetYByValue(0) - chartScale.GetYByValue(tick)));
			float bd = chartControl.Properties.BarDistance;
			double periodoMs = Bars.Count > 1 ? Math.Max(1000, (Bars.GetTime(Bars.Count - 1) - Bars.GetTime(Bars.Count - 2)).TotalMilliseconds) : 60000;
			float larg = Math.Max(1f, (float)(bd * IntervalloMs / periodoMs) + 0.6f);
			float xMin = ChartPanel.X, xMax = ChartPanel.X + ChartPanel.W;
			double pMax = chartScale.MaxValue, pMin = chartScale.MinValue;

			var aa = RenderTarget.AntialiasMode;
			RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.Aliased;

			using (var tf = new SharpDX.DirectWrite.TextFormat(Core.Globals.DirectWriteFactory, "Consolas", 10f))
			using (var tfAvviso = new SharpDX.DirectWrite.TextFormat(Core.Globals.DirectWriteFactory, "Segoe UI", 14f))
			{
				tf.WordWrapping = SharpDX.DirectWrite.WordWrapping.NoWrap;
				tf.ParagraphAlignment = SharpDX.DirectWrite.ParagraphAlignment.Center;
				tfAvviso.WordWrapping = SharpDX.DirectWrite.WordWrapping.NoWrap;

				lock (blocco)
				{
					// 1) riferimento di scala: percentile dei volumi visibili
					var visibili = new List<Colonna>();
					var vols = new List<long>();
					float xPrec = float.MinValue;
					foreach (var c in colonne)
					{
						bool ok;
						float x = XDelTempo(chartControl, c.T, out ok);
						if (!ok || x < xMin - larg || x > xMax) continue;
						if (x - xPrec < 1f) continue; // una colonna per pixel
						xPrec = x;
						visibili.Add(c);
						for (int k = 0; k < c.Vol.Length; k++)
							if (c.Prezzi[k] <= pMax && c.Prezzi[k] >= pMin) vols.Add(c.Vol[k]);
					}
					double rif = 1;
					if (vols.Count > 0)
					{
						vols.Sort();
						rif = Math.Max(1, vols[Math.Min(vols.Count - 1, (int)(vols.Count * Percentile / 100.0))]);
					}

					// 2) heat map
					var xs = new float[visibili.Count];
					for (int j = 0; j < visibili.Count; j++)
					{
						bool ok;
						xs[j] = XDelTempo(chartControl, visibili[j].T, out ok);
					}
					for (int j = 0; j < visibili.Count; j++)
					{
						var c = visibili[j];
						float x = xs[j];
						// la colonna arriva fino alla fotografia successiva (niente buchi), al massimo 30 fotografie
						float w = j + 1 < visibili.Count ? xs[j + 1] - x : larg;
						w = Math.Max(1f, Math.Min(w, larg * 30f));
						for (int k = 0; k < c.Vol.Length; k++)
						{
							double p = c.Prezzi[k];
							if (p > pMax || p < pMin || c.Vol[k] <= 0) continue;
							float i = (float)Math.Pow(Math.Min(1.0, c.Vol[k] / rif), 1.3); // livelli piccoli scuri, si accendono solo i muri
							if (i < Pulizia) continue;                                         // rumore: non disegnato
							var colore = Gradiente(i, c.Ask[k]);
							if (c.Ricordo != null && c.Ricordo[k]) colore.Alpha *= 0.45f;
							brCella.Color = colore;
							float y = chartScale.GetYByValue(p);
							RenderTarget.FillRectangle(new SharpDX.RectangleF(x, (float)Math.Floor(y - riga / 2f), w + 0.5f, (float)Math.Ceiling(riga) + 1f), brCella);
						}
					}

					// 2a) linea del prezzo sulle chiusure delle candele (c'e' sempre, anche senza book registrato)
					RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.PerPrimitive;
					if (NascondiCandele)
					{
						for (int b = Math.Max(1, ChartBars.FromIndex); b <= ChartBars.ToIndex; b++)
						{
							double c0 = Bars.GetClose(b - 1), c1 = Bars.GetClose(b);
							var a = new SharpDX.Vector2(chartControl.GetXByBarIndex(ChartBars, b - 1), chartScale.GetYByValue(c0));
							var z = new SharpDX.Vector2(chartControl.GetXByBarIndex(ChartBars, b), chartScale.GetYByValue(c1));
							RenderTarget.DrawLine(a, z, c1 >= c0 ? brLinea : brAsk, 1.6f);
						}
					}

					// 2b) linea del prezzo fine (ultimo scambio a ogni fotografia)
					for (int j = 1; j < visibili.Count; j++)
					{
						double p0 = visibili[j - 1].Ultimo, p1 = visibili[j].Ultimo;
						if (p0 <= 0 || p1 <= 0) continue;
						var a = new SharpDX.Vector2(xs[j - 1], chartScale.GetYByValue(p0));
						var b = new SharpDX.Vector2(xs[j], chartScale.GetYByValue(p1));
						RenderTarget.DrawLine(a, new SharpDX.Vector2(b.X, a.Y), brLinea, 2f);
						RenderTarget.DrawLine(new SharpDX.Vector2(b.X, a.Y), b, p1 >= p0 ? brLinea : brAsk, 2f);
					}
					RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.Aliased;

					// 3) bolle dei grossi scambi
					// bolle "a sfera": acquisti argento/blu, vendite rosse, con riflesso in alto a sinistra
					RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.PerPrimitive;
					using (var gsBuy = new SharpDX.Direct2D1.GradientStopCollection(RenderTarget, new[]
					{
						new SharpDX.Direct2D1.GradientStop { Position = 0f, Color = new SharpDX.Color4(1f, 1f, 1f, 0.95f) },
						new SharpDX.Direct2D1.GradientStop { Position = 0.45f, Color = new SharpDX.Color4(0.62f, 0.72f, 0.88f, 0.9f) },
						new SharpDX.Direct2D1.GradientStop { Position = 1f, Color = new SharpDX.Color4(0.18f, 0.25f, 0.45f, 0.9f) },
					}))
					using (var gsSell = new SharpDX.Direct2D1.GradientStopCollection(RenderTarget, new[]
					{
						new SharpDX.Direct2D1.GradientStop { Position = 0f, Color = new SharpDX.Color4(1f, 0.85f, 0.85f, 0.95f) },
						new SharpDX.Direct2D1.GradientStop { Position = 0.45f, Color = new SharpDX.Color4(0.90f, 0.25f, 0.30f, 0.9f) },
						new SharpDX.Direct2D1.GradientStop { Position = 1f, Color = new SharpDX.Color4(0.40f, 0.05f, 0.08f, 0.9f) },
					}))
					{
						double sogliaBolle = SogliaBolla;
						if (scambi.Count > 50)
						{
							var vv = new List<long>(scambi.Count);
							foreach (var s0 in scambi) vv.Add(s0.V);
							vv.Sort();
							sogliaBolle = Math.Max(sogliaBolle, vv[(int)(vv.Count * 0.90)]);   // solo il 10% piu' grosso
						}
						foreach (var s in scambi)
						{
							if (s.V < sogliaBolle) continue;
							if (s.P > pMax || s.P < pMin) continue;
							bool ok;
							float x = XDelTempo(chartControl, s.T, out ok);
							if (!ok || x < xMin || x > xMax) continue;
							float r = (float)Math.Min(28, 3 + Math.Sqrt(s.V) * 1.6);
							var centro = new SharpDX.Vector2(x, chartScale.GetYByValue(s.P));
							var prop = new SharpDX.Direct2D1.RadialGradientBrushProperties
							{
								Center = centro, GradientOriginOffset = new SharpDX.Vector2(-r * 0.35f, -r * 0.35f), RadiusX = r, RadiusY = r
							};
							using (var rg = new SharpDX.Direct2D1.RadialGradientBrush(RenderTarget, prop, s.Lato > 0 ? gsBuy : gsSell))
								RenderTarget.FillEllipse(new SharpDX.Direct2D1.Ellipse(centro, r, r), rg);
						}
					}
					RenderTarget.AntialiasMode = SharpDX.Direct2D1.AntialiasMode.Aliased;

					// 3b) zone migliori di ordini: i muri piu' forti (contratti x durata) nell'area visibile
					DisegnaZone(chartControl, chartScale, riga, xMin, xMax, pMin, pMax);

					// 4) profilo del book attuale sul bordo destro
					long maxLibro = 1;
					foreach (var l in libroAsk) maxLibro = Math.Max(maxLibro, l.Vol);
					foreach (var l in libroBid) maxLibro = Math.Max(maxLibro, l.Vol);
					for (int lato = 0; lato < 2; lato++)
					{
						var libro = lato == 0 ? libroAsk : libroBid;
						var br = lato == 0 ? brAsk : brBid;
						foreach (var l in libro)
						{
							if (l.Prezzo > pMax || l.Prezzo < pMin) continue;
							float y = chartScale.GetYByValue(l.Prezzo);
							float w = (float)(LarghezzaProfilo * l.Vol / (double)maxLibro);
							float h = Math.Max(1f, riga - 1f);
							RenderTarget.FillRectangle(new SharpDX.RectangleF(xMax - w, y - h / 2f, w, h), br);
							if (riga >= 9f)
								RenderTarget.DrawText(l.Vol.ToString(), tf, new SharpDX.RectangleF(xMax - LarghezzaProfilo - 40f, y - h / 2f, 38f, h), brTesto);
						}
					}

					if (!profonditaRicevuta)
					{
						string msg = (DateTime.Now - avvio).TotalSeconds < 20
							? "HeatmapOro: in attesa del book (Level 2)..."
							: "HeatmapOro: nessun dato di profondita' dal feed (serve il Level 2 del COMEX)";
						RenderTarget.DrawText(msg, tfAvviso, new SharpDX.RectangleF(xMin + 10f, ChartPanel.Y + 30f, 700f, 22f), brTesto);
					}
				}
			}
			RenderTarget.AntialiasMode = aa;
		}

		#region Properties
		[Range(100, 60000)]
		[Display(Name = "Fotografia del book ogni (ms)", Order = 0, GroupName = "Heatmap")]
		public int IntervalloMs { get; set; }

		[Range(1, 100)]
		[Display(Name = "Percentile della scala colori", Description = "Piu' basso = colori piu' accesi", Order = 1, GroupName = "Heatmap")]
		public double Percentile { get; set; }

		[Range(1, int.MaxValue)]
		[Display(Name = "Bolla dai contratti", Description = "Scambi con almeno questi contratti diventano bolle", Order = 2, GroupName = "Heatmap")]
		public int SogliaBolla { get; set; }

		[Range(20, 600)]
		[Display(Name = "Larghezza profilo book (px)", Order = 3, GroupName = "Heatmap")]
		public int LarghezzaProfilo { get; set; }

		[Display(Name = "Nascondi candele", Description = "Solo heat map, linea del prezzo e bolle", Order = 5, GroupName = "Heatmap")]
		public bool NascondiCandele { get; set; }

		[Display(Name = "Registra il book su disco", Description = "Salva le fotografie del book e le ricarica all'avvio", Order = 6, GroupName = "Heatmap")]
		public bool RegistraSuDisco { get; set; }

		[Range(1, 60)]
		[Display(Name = "Giorni di book da ricaricare", Order = 7, GroupName = "Heatmap")]
		public int GiorniDaCaricare { get; set; }

		[Display(Name = "Memoria dei muri", Description = "Tiene i livelli usciti dai 10 del feed (ultimo valore visto, piu' spenti)", Order = 8, GroupName = "Heatmap")]
		public bool MemoriaLivelli { get; set; }

		[Range(1, 1440)]
		[Display(Name = "Memoria massima (minuti)", Order = 9, GroupName = "Heatmap")]
		public int MemoriaMinuti { get; set; }

		[Range(0.0, 0.9)]
		[Display(Name = "Pulizia (0-0,9)", Description = "Livelli sotto questa intensita' non vengono disegnati", Order = 10, GroupName = "Zone e pulizia")]
		public double Pulizia { get; set; }

		[Range(50, 99.9)]
		[Display(Name = "Muro: percentile dei contratti", Order = 11, GroupName = "Zone e pulizia")]
		public double PercentileMuro { get; set; }

		[Range(5, 3600)]
		[Display(Name = "Muro: durata minima (secondi)", Order = 12, GroupName = "Zone e pulizia")]
		public int DurataMuroSec { get; set; }

		[Range(0, 50)]
		[Display(Name = "Zone mostrate (le piu' forti)", Order = 13, GroupName = "Zone e pulizia")]
		public int ZoneMassime { get; set; }

		[Range(1000, 500000)]
		[Display(Name = "Fotografie tenute in memoria", Order = 4, GroupName = "Heatmap")]
		public int ColonneMassime { get; set; }
		#endregion
	}
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
	public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
	{
		private HeatmapOro[] cacheHeatmapOro;
		public HeatmapOro HeatmapOro()
		{
			return HeatmapOro(Input);
		}

		public HeatmapOro HeatmapOro(ISeries<double> input)
		{
			if (cacheHeatmapOro != null)
				for (int idx = 0; idx < cacheHeatmapOro.Length; idx++)
					if (cacheHeatmapOro[idx] != null &&  cacheHeatmapOro[idx].EqualsInput(input))
						return cacheHeatmapOro[idx];
			return CacheIndicator<HeatmapOro>(new HeatmapOro(), input, ref cacheHeatmapOro);
		}
	}
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
	public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
	{
		public Indicators.HeatmapOro HeatmapOro()
		{
			return indicator.HeatmapOro(Input);
		}

		public Indicators.HeatmapOro HeatmapOro(ISeries<double> input )
		{
			return indicator.HeatmapOro(input);
		}
	}
}

namespace NinjaTrader.NinjaScript.Strategies
{
	public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
	{
		public Indicators.HeatmapOro HeatmapOro()
		{
			return indicator.HeatmapOro(Input);
		}

		public Indicators.HeatmapOro HeatmapOro(ISeries<double> input )
		{
			return indicator.HeatmapOro(input);
		}
	}
}

#endregion
