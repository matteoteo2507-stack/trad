// ZoneReazioneOF - Motore Profitto (20/11/2026). SOLO VISUALIZZAZIONE + REGISTRO: non apre ordini.
// Disegna zone di reazione OGGETTIVE (regole fisse, niente discrezione) e REGISTRA come reagisce il prezzo a ogni tocco:
//   POC / VAH / VAL di ieri   profilo volumi 08:20-13:30 New York del giorno prima (70% del volume attorno al POC)
//   VPOC NUDO                 POC dei giorni prima (fino a GiorniVpoc) mai ritoccati dal prezzo
//   ASSORBIMENTO              candela con volume >= VolMolt x media 20 ma range <= RangeMax x range medio:
//                             delta negativo = venditori assorbiti -> supporto; delta positivo = compratori assorbiti -> resistenza
//   STACK IMBALANCE           >= MinStack livelli consecutivi nella stessa candela con ask >= SogliaImbalance x bid del livello sotto
//                             (compratori aggressivi -> supporto) o il contrario (venditori -> resistenza)
//   TONDO                     prezzi tondi ogni PassoTondo punti (serve come CONFRONTO: se una zona non fa meglio dei tondi, non vale)
// Tocco = il prezzo entra nella zona arrivando da fuori. Esito entro FinestraMinuti:
//   REAZIONE se si allontana di ReazionePunti nel verso del rimbalzo prima di rompere; ROTTA se va oltre l'altro lato
//   della zona di RotturaPunti; altrimenti NULLA. Lo storico caricato va in zone_reazioni_storico.csv (riscritto a ogni
//   caricamento), il tempo reale si aggiunge in zone_reazioni_live.csv (Documenti\NinjaTrader 8). In alto a sinistra: statistiche.
// Mettere su GC 5 minuti con Tick Replay ACCESO (serve il lato di ogni scambio).
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Text;
using System.Windows.Media;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.NinjaScript.DrawingTools;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
	public class ZoneReazioneOF : Indicator
	{
		private class Zona
		{
			public int Id; public string Tipo; public int Lato;      // Lato: +1 supporto, -1 resistenza, 0 entrambi (livello)
			public double Bassa, Alta; public int BarraInizio, BarraFine = -1; public bool Attiva = true;
			public int Fuori;                                          // +1 il prezzo e' sopra, -1 sotto, 0 dentro / sconosciuto
			public bool InCorso; public int Dir, Tocchi; public double Rif, Mfe, Mae; public DateTime Inizio;
		}
		private class Statistica { public int N, Reaz, Rotte; }

		private TimeZoneInfo ny;
		private readonly List<Zona> zone = new List<Zona>();
		private readonly Dictionary<string, Statistica> stat = new Dictionary<string, Statistica>();
		private int prossimoId;
		// tick
		private double ultimoAsk, ultimoBid, ultimoPrezzo, volPrecedente; private int ultimoLato = 1;
		// footprint della candela in corso: livello -> [ask, bid]
		private readonly Dictionary<long, double[]> fp = new Dictionary<long, double[]>();
		private double deltaBarra, volBarra;
		// profilo 08:20-13:30 NY del giorno
		private readonly SortedDictionary<long, double> profilo = new SortedDictionary<long, double>();
		private DateTime giornoProf = DateTime.MinValue;
		private readonly List<double> volStoria = new List<double>(), rngStoria = new List<double>();
		private StringBuilder bufStorico; private string fileStorico, fileLive;
		private DateTime ultimoTondo = DateTime.MinValue;

		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "ZoneReazioneOF";
				Description = "Zone di reazione oggettive (POC/VA di ieri, VPOC nudi, assorbimento, stack imbalance, tondi) con registro delle reazioni. Solo visualizzazione.";
				Calculate = Calculate.OnEachTick; IsOverlay = true; DisplayInDataBox = false; PaintPriceMarkers = false;
				IsSuspendedWhileInactive = false; MaximumBarsLookBack = MaximumBarsLookBack.Infinite;
				MezzaLarghezza = 1.0; ReazionePunti = 3.0; RotturaPunti = 1.0; FinestraMinuti = 30;
				GiorniVpoc = 5; VolMolt = 2.0; RangeMax = 0.6; SogliaImbalance = 3.0; MinStack = 3; TickPerLivello = 5; PassoTondo = 10;
				MostraPocVa = true; MostraVpoc = true; MostraAssorbimento = true; MostraStack = true; MostraTondi = true; Registra = true;
				MaxZoneAttive = 60;
			}
			else if (State == State.DataLoaded)
			{
				ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
				fileStorico = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "zone_reazioni_storico.csv");
				fileLive = Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "zone_reazioni_live.csv");
				bufStorico = new StringBuilder("data_ny;ora_ny;strumento;tipo;verso;zona_bassa;zona_alta;tocco;prezzo;esito;mfe;mae;minuti\n");
			}
			else if (State == State.Transition)
			{
				if (Registra && bufStorico != null) try { File.WriteAllText(fileStorico, bufStorico.ToString()); } catch { }
				bufStorico = null;
			}
		}

		protected override void OnMarketData(MarketDataEventArgs e)
		{
			if (e.MarketDataType == MarketDataType.Ask) ultimoAsk = e.Price;
			else if (e.MarketDataType == MarketDataType.Bid) ultimoBid = e.Price;
		}

		private DateTime Ny(DateTime t) { return TimeZoneInfo.ConvertTime(t, TimeZoneInfo.Local, ny); }

		protected override void OnBarUpdate()
		{
			if (CurrentBar == 0 && !Bars.IsTickReplay)
				Draw.TextFixed(this, "zrAvviso", "ZoneReazioneOF: accendi Tick Replay (serve il lato di ogni scambio)", TextPosition.BottomLeft);
			if (IsFirstTickOfBar)
			{
				if (CurrentBar > 0) BarraChiusa();
				fp.Clear(); deltaBarra = 0; volBarra = 0; volPrecedente = 0;
			}
			double v = Volume[0] - volPrecedente; volPrecedente = Volume[0];
			double p = Close[0];
			if (v > 0)
			{
				int lato;
				if (ultimoAsk > 0 && p >= ultimoAsk) lato = 1;
				else if (ultimoBid > 0 && p <= ultimoBid) lato = -1;
				else lato = p > ultimoPrezzo ? 1 : p < ultimoPrezzo ? -1 : ultimoLato;
				ultimoPrezzo = p; ultimoLato = lato;
				long lv = (long)Math.Floor(p / (TickSize * TickPerLivello) + 1e-9);
				double[] c; if (!fp.TryGetValue(lv, out c)) { c = new double[2]; fp[lv] = c; }
				if (lato > 0) c[0] += v; else c[1] += v;
				deltaBarra += lato * v; volBarra += v;
				// profilo 08:20-13:30 NY (ora di inizio candela)
				DateTime iniNy = Ny(Time[0]).AddMinutes(-BarsPeriod.Value);
				TimeSpan m = iniNy.TimeOfDay;
				if (m >= new TimeSpan(8, 20, 0) && m < new TimeSpan(13, 30, 0))
				{
					if (iniNy.Date != giornoProf) { ChiudiProfilo(); giornoProf = iniNy.Date; }
					long k = (long)Math.Round(p / TickSize); double cur; profilo.TryGetValue(k, out cur); profilo[k] = cur + v;
				}
			}
			Tocchi(p);
		}

		// ------------------------------------------------------------------ zone dai profili
		private void ChiudiProfilo()
		{
			if (profilo.Count < 10) { profilo.Clear(); return; }
			List<long> lv = new List<long>(profilo.Keys); List<double> vv = new List<double>(profilo.Values);
			int ip = 0; double tot = 0;
			for (int i = 0; i < vv.Count; i++) { tot += vv[i]; if (vv[i] > vv[ip]) ip = i; }
			int lo = ip, hi = ip; double acc = vv[ip];
			while (acc < 0.7 * tot && (lo > 0 || hi < vv.Count - 1))
			{
				double su = hi < vv.Count - 1 ? vv[hi + 1] : -1, giu = lo > 0 ? vv[lo - 1] : -1;
				if (su >= giu) { hi++; acc += su; } else { lo--; acc += giu; }
			}
			double poc = lv[ip] * TickSize, vah = lv[hi] * TickSize, val = lv[lo] * TickSize;
			profilo.Clear();
			// le zone POC/VA del giorno prima scadono: restano solo quelle di "ieri"
			foreach (Zona z in zone) if (z.Attiva && (z.Tipo == "POC_IERI" || z.Tipo == "VAH_IERI" || z.Tipo == "VAL_IERI")) Termina(z);
			foreach (Zona z in zone) if (z.Attiva && z.Tipo == "VPOC_NUDO" && CurrentBar - z.BarraInizio > GiorniVpoc * 24 * 60 / BarsPeriod.Value) Termina(z);
			if (MostraPocVa)
			{
				Nuova("POC_IERI", 0, poc - MezzaLarghezza, poc + MezzaLarghezza);
				Nuova("VAH_IERI", 0, vah - MezzaLarghezza, vah + MezzaLarghezza);
				Nuova("VAL_IERI", 0, val - MezzaLarghezza, val + MezzaLarghezza);
			}
			if (MostraVpoc) Nuova("VPOC_NUDO", 0, poc - MezzaLarghezza, poc + MezzaLarghezza);
		}

		// ------------------------------------------------------------------ zone dalla candela chiusa
		private void BarraChiusa()
		{
			double rng = High[1] - Low[1];
			if (volStoria.Count >= 20 && volBarra > 0)
			{
				double mv = 0, mr = 0; for (int i = volStoria.Count - 20; i < volStoria.Count; i++) { mv += volStoria[i]; mr += rngStoria[i]; }
				mv /= 20; mr /= 20;
				if (MostraAssorbimento && volBarra >= VolMolt * mv && rng <= RangeMax * mr && rng > 0 && Math.Abs(deltaBarra) >= 0.15 * volBarra)
					Nuova("ASSORBIMENTO", deltaBarra < 0 ? 1 : -1, Low[1], High[1]);
			}
			volStoria.Add(volBarra); rngStoria.Add(rng);
			if (volStoria.Count > 500) { volStoria.RemoveAt(0); rngStoria.RemoveAt(0); }
			if (MostraStack && fp.Count >= MinStack + 1)
			{
				List<long> lv = new List<long>(fp.Keys); lv.Sort();
				double passo = TickSize * TickPerLivello;
				for (int verso = 1; verso >= -1; verso -= 2)
				{
					int corsa = 0; long inizio = 0;
					for (int i = 1; i < lv.Count; i++)
					{
						bool ok = false;
						if (lv[i] == lv[i - 1] + 1)
						{
							double ask = fp[lv[i]][0], bidSotto = fp[lv[i - 1]][1];       // diagonale: ask del livello contro bid di quello sotto
							double bid = fp[lv[i - 1]][1], askSopra = fp[lv[i]][0];
							ok = verso > 0 ? ask >= SogliaImbalance * Math.Max(bidSotto, 1) && ask >= 5 : bid >= SogliaImbalance * Math.Max(askSopra, 1) && bid >= 5;
						}
						if (ok) { if (corsa == 0) inizio = lv[i - 1]; corsa++; }
						else
						{
							if (corsa >= MinStack) Nuova("STACK_IMBALANCE", verso, inizio * passo, (inizio + corsa + 1) * passo);
							corsa = 0;
						}
					}
					if (corsa >= MinStack) Nuova("STACK_IMBALANCE", verso, inizio * passo, (inizio + corsa + 1) * passo);
				}
			}
			// tondi: una volta al giorno, quelli vicini al prezzo
			DateTime g = Ny(Time[1]).Date;
			if (MostraTondi && g != ultimoTondo)
			{
				ultimoTondo = g;
				foreach (Zona z in zone) if (z.Attiva && z.Tipo == "TONDO") Termina(z);
				double base0 = Math.Round(Close[1] / PassoTondo) * PassoTondo;
				for (int k = -3; k <= 3; k++) { double t = base0 + k * PassoTondo; Nuova("TONDO", 0, t - MezzaLarghezza, t + MezzaLarghezza); }
			}
			// disegno ed eventuale scadenza (zone di candela: 3 giorni)
			int scad = 3 * 24 * 60 / BarsPeriod.Value;
			foreach (Zona z in zone)
			{
				if (!z.Attiva) continue;
				if ((z.Tipo == "ASSORBIMENTO" || z.Tipo == "STACK_IMBALANCE") && CurrentBar - z.BarraInizio > scad) { Termina(z); continue; }
				Disegna(z);
			}
			Statistiche();
		}

		private void Nuova(string tipo, int lato, double bassa, double alta)
		{
			int attive = 0; Zona vecchia = null;
			foreach (Zona z in zone) if (z.Attiva) { attive++; if (vecchia == null && z.Tipo != "VPOC_NUDO") vecchia = z; }
			if (attive >= MaxZoneAttive && vecchia != null) Termina(vecchia);
			Zona n = new Zona { Id = prossimoId++, Tipo = tipo, Lato = lato, Bassa = bassa, Alta = alta, BarraInizio = CurrentBar };
			n.Fuori = Close[0] > alta ? 1 : Close[0] < bassa ? -1 : 0;
			zone.Add(n);
			if (zone.Count > 3000) zone.RemoveAt(0);
			Disegna(n);
		}

		private void Termina(Zona z) { z.Attiva = false; z.BarraFine = CurrentBar; Disegna(z); }

		private Brush Colore(Zona z)
		{
			switch (z.Tipo)
			{
				case "POC_IERI": return Brushes.Gold;
				case "VAH_IERI": case "VAL_IERI": return Brushes.Khaki;
				case "VPOC_NUDO": return Brushes.Orange;
				case "ASSORBIMENTO": return z.Lato > 0 ? Brushes.DeepSkyBlue : Brushes.Violet;
				case "STACK_IMBALANCE": return z.Lato > 0 ? Brushes.LimeGreen : Brushes.OrangeRed;
				default: return Brushes.Gray;
			}
		}

		private void Disegna(Zona z)
		{
			int fine = z.BarraFine >= 0 ? z.BarraFine : CurrentBar;
			int a = Math.Max(0, CurrentBar - z.BarraInizio), b = Math.Max(0, CurrentBar - fine);
			if (a <= b) a = b + 1;
			Brush c = Colore(z);
			try { Draw.Rectangle(this, "zr" + z.Id, false, a, z.Alta, b, z.Bassa, c, c, z.Attiva ? 18 : 6); } catch { }
		}

		// ------------------------------------------------------------------ tocchi e reazioni
		private void Tocchi(double p)
		{
			DateTime ora = Time[0];
			foreach (Zona z in zone)
			{
				if (!z.Attiva && !z.InCorso) continue;
				if (z.InCorso)
				{
					double fav = (p - z.Rif) * z.Dir;
					z.Mfe = Math.Max(z.Mfe, fav); z.Mae = Math.Max(z.Mae, -fav);
					bool rotta = z.Dir > 0 ? p < z.Bassa - RotturaPunti : p > z.Alta + RotturaPunti;
					string esito = null;
					if (z.Mfe >= ReazionePunti) esito = "REAZIONE";
					else if (rotta) esito = "ROTTA";
					else if ((ora - z.Inizio).TotalMinutes >= FinestraMinuti) esito = "NULLA";
					if (esito != null)
					{
						z.InCorso = false; Scrivi(z, esito, ora);
						if (esito == "ROTTA" && z.Attiva) Termina(z);
						if (z.Tipo == "VPOC_NUDO" && z.Attiva) Termina(z);        // toccato: non e' piu' nudo
						z.Fuori = 0;
					}
					continue;
				}
				int pos = p > z.Alta ? 1 : p < z.Bassa ? -1 : 0;
				if (pos != 0) { z.Fuori = pos; continue; }
				if (z.Fuori == 0) continue;                                  // era gia' dentro: non e' un tocco nuovo
				int dir = z.Fuori;                                            // arriva da sopra -> rimbalzo verso l'alto (+1)
				z.Fuori = 0;
				if (z.Lato != 0 && z.Lato != dir) continue;                   // zona con un verso: conta solo se ci arriva dal lato giusto
				z.InCorso = true; z.Dir = dir; z.Rif = p; z.Mfe = 0; z.Mae = 0; z.Inizio = ora; z.Tocchi++;
			}
		}

		private void Scrivi(Zona z, string esito, DateTime ora)
		{
			Statistica s; if (!stat.TryGetValue(z.Tipo, out s)) { s = new Statistica(); stat[z.Tipo] = s; }
			s.N++; if (esito == "REAZIONE") s.Reaz++; else if (esito == "ROTTA") s.Rotte++;
			if (!Registra) return;
			DateTime t = Ny(z.Inizio);
			string riga = string.Format(CultureInfo.InvariantCulture, "{0:yyyy-MM-dd};{0:HH:mm};{1};{2};{3};{4};{5};{6};{7};{8};{9:0.0};{10:0.0};{11:0}\n",
				t, Instrument.FullName, z.Tipo, z.Dir > 0 ? "SUPPORTO" : "RESISTENZA", z.Bassa, z.Alta, z.Tocchi, z.Rif, esito, z.Mfe, z.Mae, (ora - z.Inizio).TotalMinutes);
			if (State == State.Historical) { if (bufStorico != null) bufStorico.Append(riga); }
			else try { File.AppendAllText(fileLive, riga); } catch { }
		}

		private void Statistiche()
		{
			if (State == State.Historical && CurrentBar < Count - 2) return;
			StringBuilder sb = new StringBuilder("ZoneReazioneOF - tocchi: % REAZIONE (+" + ReazionePunti.ToString(CultureInfo.InvariantCulture) + " punti) / % ROTTA\n");
			foreach (KeyValuePair<string, Statistica> kv in stat)
				sb.AppendFormat(CultureInfo.InvariantCulture, "{0,-16} {1,4} tocchi  reazione {2,3:0}%  rotta {3,3:0}%\n", kv.Key, kv.Value.N,
					100.0 * kv.Value.Reaz / Math.Max(1, kv.Value.N), 100.0 * kv.Value.Rotte / Math.Max(1, kv.Value.N));
			Draw.TextFixed(this, "zrStat", sb.ToString(), TextPosition.TopLeft);
		}

		#region Properties
		[NinjaScriptProperty][Range(0.1, 50)][Display(Name = "Mezza larghezza delle zone-livello (punti)", Description = "POC, VAH, VAL, VPOC e tondi: livello +/- questo valore", Order = 0, GroupName = "1 Zone")]
		public double MezzaLarghezza { get; set; }
		[NinjaScriptProperty][Range(1, 30)][Display(Name = "Giorni VPOC nudi", Order = 1, GroupName = "1 Zone")]
		public int GiorniVpoc { get; set; }
		[NinjaScriptProperty][Range(1.0, 10.0)][Display(Name = "Assorbimento: volume >= x media 20", Order = 2, GroupName = "1 Zone")]
		public double VolMolt { get; set; }
		[NinjaScriptProperty][Range(0.1, 1.5)][Display(Name = "Assorbimento: range <= x range medio", Order = 3, GroupName = "1 Zone")]
		public double RangeMax { get; set; }
		[NinjaScriptProperty][Range(1.5, 10.0)][Display(Name = "Imbalance: rapporto minimo", Order = 4, GroupName = "1 Zone")]
		public double SogliaImbalance { get; set; }
		[NinjaScriptProperty][Range(2, 10)][Display(Name = "Imbalance: livelli consecutivi", Order = 5, GroupName = "1 Zone")]
		public int MinStack { get; set; }
		[NinjaScriptProperty][Range(1, 50)][Display(Name = "Tick per livello del footprint", Description = "GC: 5 (= 0,5 punti)", Order = 6, GroupName = "1 Zone")]
		public int TickPerLivello { get; set; }
		[NinjaScriptProperty][Range(1, 1000)][Display(Name = "Passo dei prezzi tondi (punti)", Order = 7, GroupName = "1 Zone")]
		public double PassoTondo { get; set; }
		[NinjaScriptProperty][Range(10, 500)][Display(Name = "Massimo zone attive", Order = 8, GroupName = "1 Zone")]
		public int MaxZoneAttive { get; set; }
		[NinjaScriptProperty][Range(0.1, 100)][Display(Name = "Reazione: punti di rimbalzo", Order = 0, GroupName = "2 Registro")]
		public double ReazionePunti { get; set; }
		[NinjaScriptProperty][Range(0, 100)][Display(Name = "Rottura: punti oltre la zona", Order = 1, GroupName = "2 Registro")]
		public double RotturaPunti { get; set; }
		[NinjaScriptProperty][Range(1, 600)][Display(Name = "Finestra (minuti)", Order = 2, GroupName = "2 Registro")]
		public int FinestraMinuti { get; set; }
		[NinjaScriptProperty][Display(Name = "Scrivi il registro CSV", Order = 3, GroupName = "2 Registro")]
		public bool Registra { get; set; }
		[NinjaScriptProperty][Display(Name = "Mostra POC/VAH/VAL di ieri", Order = 0, GroupName = "3 Mostra")]
		public bool MostraPocVa { get; set; }
		[NinjaScriptProperty][Display(Name = "Mostra VPOC nudi", Order = 1, GroupName = "3 Mostra")]
		public bool MostraVpoc { get; set; }
		[NinjaScriptProperty][Display(Name = "Mostra assorbimento", Order = 2, GroupName = "3 Mostra")]
		public bool MostraAssorbimento { get; set; }
		[NinjaScriptProperty][Display(Name = "Mostra stack imbalance", Order = 3, GroupName = "3 Mostra")]
		public bool MostraStack { get; set; }
		[NinjaScriptProperty][Display(Name = "Mostra prezzi tondi (confronto)", Order = 4, GroupName = "3 Mostra")]
		public bool MostraTondi { get; set; }
		#endregion
	}
}
