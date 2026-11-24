// CuscinettoMP - Motore Profitto (19/11/2026). Modulo comune ai 3 bot (OroOrderFlowNT, OroSpintaNT, PortafoglioIntradayNT).
// CUSCINETTO = soldi che mancano prima di toccare il limite di perdita FundedNext (perdita massima 1.000 $ trailing sul saldo di FINE GIORNATA,
// che si blocca a saldo iniziale + 100). Regola decisa dai soci 19/11: rischio x (cuscinetto / 1.000), minimo 35%.
// Il saldo massimo di fine giornata si calcola da solo: ogni giornata FundedNext finisce alle 17:00 di New York; il saldo visto per ultimo
// prima delle 17:00 NY diventa il saldo di fine giornata. Stato salvato in Documenti\NinjaTrader 8\cuscinetto_stato.txt (picco;giorno;ultimo saldo).
// Lo stato e' condiviso in memoria tra i 3 bot (stessa classe statica) e su file (riavvii).
#region Using declarations
using System;
using System.Globalization;
using System.IO;
using NinjaTrader.Cbi;
#endregion

namespace NinjaTrader.NinjaScript.AddOns
{
	public static class CuscinettoMP
	{
		public const double SaldoIniziale = 25000.0;   // conto Rapid 25k
		public const double PerditaMassima = 1000.0;   // trailing di fine giornata
		public const double Riferimento = 1000.0;      // cuscinetto a cui si rischia il 100%
		public const double Minimo = 0.35;             // rischio minimo (35%)
		private static readonly object blocco = new object();
		private static bool caricato;
		private static double picco = SaldoIniziale, ultimoSaldo;
		private static DateTime giorno = DateTime.MinValue, ultimoSalvataggio = DateTime.MinValue;
		private static TimeZoneInfo ny;

		private static string FileStato() { return Path.Combine(NinjaTrader.Core.Globals.UserDataDir, "cuscinetto_stato.txt"); }
		private static DateTime GiornoFunded()
		{
			if (ny == null) ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
			return TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, ny).AddHours(7).Date;   // dalle 17:00 NY e' gia' il giorno dopo
		}
		private static void Carica()
		{
			caricato = true;
			try
			{
				if (!File.Exists(FileStato())) return;
				string[] p = File.ReadAllText(FileStato()).Trim().Split(';');
				picco = double.Parse(p[0], CultureInfo.InvariantCulture);
				giorno = DateTime.ParseExact(p[1], "yyyy-MM-dd", CultureInfo.InvariantCulture);
				ultimoSaldo = double.Parse(p[2], CultureInfo.InvariantCulture);
			}
			catch { }
		}
		private static void Salva()
		{
			for (int t = 0; t < 3; t++)
				try { File.WriteAllText(FileStato(), string.Format(CultureInfo.InvariantCulture, "{0:0.00};{1:yyyy-MM-dd};{2:0.00}", picco, giorno, ultimoSaldo)); ultimoSalvataggio = DateTime.UtcNow; return; }
				catch { System.Threading.Thread.Sleep(20); }
		}
		private static double Saldo(Account acc)
		{
			if (acc == null) return 0;
			double nl = acc.Get(AccountItem.NetLiquidation, Currency.UsDollar);
			return nl > 0 ? nl : acc.Get(AccountItem.CashValue, Currency.UsDollar);
		}
		// da chiamare spesso (anche senza trade): registra il saldo e, al cambio di giornata, aggiorna il saldo massimo di fine giornata
		public static void Aggiorna(Account acc)
		{
			double s = Saldo(acc);
			if (s <= 0) return;
			lock (blocco)
			{
				if (!caricato) Carica();
				DateTime g = GiornoFunded();
				bool cambio = false;
				if (giorno == DateTime.MinValue) { giorno = g; cambio = true; }
				else if (g != giorno)
				{
					if (ultimoSaldo > picco) picco = ultimoSaldo;   // fine giornata precedente
					giorno = g; cambio = true;
				}
				ultimoSaldo = s;
				if (cambio || (DateTime.UtcNow - ultimoSalvataggio).TotalSeconds >= 30) Salva();
			}
		}
		public static double Limite()
		{
			lock (blocco) { if (!caricato) Carica(); return Math.Min(picco - PerditaMassima, SaldoIniziale + 100.0); }
		}
		// moltiplicatore del rischio (0,35 ... 1) e descrizione per l'Output
		public static double Moltiplicatore(Account acc, out string info)
		{
			Aggiorna(acc);
			double s = Saldo(acc), lim = Limite(), c = s - lim;
			double m = Math.Max(Minimo, Math.Min(1.0, c / Riferimento));
			info = string.Format(CultureInfo.InvariantCulture, "cuscinetto {0:0} $ (saldo {1:0}, limite {2:0}) -> rischio x{3:0.00}", c, s, lim, m);
			return m;
		}
	}
}
