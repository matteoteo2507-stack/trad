# agents/

Prompt di sistema per i subagent del workspace. Ogni file `.md` è il system prompt di un agent.

## Convenzione di scrittura di un agent prompt

Ogni file segue questa struttura:

1. **Identità** (chi sei) — pattern ispirato a `dexter/SOUL.md`.
2. **Framework di analisi** (come pensi).
3. **Output atteso** (formato della risposta).
4. **Vincoli operativi** (cosa non fare).

## Subagent disponibili

| Agent | Ruolo | Stage in cui si attiva |
|---|---|---|
| `stock_selector.md` | Subagent che agentizza il sistema V6.0 di selezione SP500 | Stage 1 |
| `consensus/damodaran.md` | Persona "Aswath Damodaran" del Consensus Layer | Stage 4 |
| `consensus/buffett.md` | Persona "Warren Buffett" del Consensus Layer | Stage 4 |
| `consensus/burry.md` | Persona "Michael Burry" del Consensus Layer | Stage 4 |
| `consensus/taleb.md` | Persona "Nassim Taleb" del Consensus Layer | Stage 4 |

## Note sul Consensus Layer (Stage 4)

Le 4 personas del consensus sono pescate da `ai-hedge-fund` (riferimento esterno). I prompt sono
**adattati al contesto del nostro Stock Selector**: ricevono in input una top pick generata dal
sistema V6.0 e producono una valutazione indipendente.

Output di ogni persona: `{signal: bullish|bearish|neutral, confidence: 0-100, reasoning: str}`.

Il sistema **non aggrega** i 4 voti in una decisione meccanica. Restituisce a Matteo una tabella
con le 4 valutazioni; la decisione finale resta sua.
