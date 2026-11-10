# Sentinelle phyto: French pesticide authorisation and grace-period MCP server

**MCP server and pay-per-call API for AI agents.** For any plant protection product registered in France (AMM number or trade name), it tells whether the product is still authorised, can still be sold, or can only be used from existing stocks, use by use and crop by crop, and until which date, from the official Anses E-Phy register.

- **MCP endpoint (streamable HTTP):** `https://phyto.amacunia.fr/mcp`
- **REST endpoint:** `GET https://phyto.amacunia.fr/v1/phyto?produits=BRIVELA,2120131&culture=Vigne`
- **Free sample:** https://phyto.amacunia.fr/v1/exemple
- **Docs for agents:** https://phyto.amacunia.fr/llms.txt
- **Price:** 0.01 USDC per call (1 to 20 products per call), paid with the [x402](https://x402.org) protocol on Base. No account, no API key, no subscription. Free trial: 3 calls per day per caller on the REST endpoint.
- **Official MCP Registry:** `io.github.Marcoco27/sentinelle-phyto`

## Why it exists

When France withdraws the authorisation (AMM) of a pesticide, or of one of its uses, the decision usually grants a grace period: at most **six months** to sell and distribute existing stocks, then at most **one more year** to store and use them (art. 46 of Regulation (EC) No 1107/2009). After that, selling or using the product is an offence (art. L253-1 Code rural et de la pêche maritime).

The two dates are published use by use in E-Phy, which changes every week. Farm suppliers, co-ops, growers, landscapers and their advisers have to check them product by product before selling or spraying. This server reads the register and gives the verdict, the dates and the days left, for up to 20 products per call.

## Tools

| Tool | Price | What it does |
|---|---|---|
| `phyto_lookup` | 0.01 USDC (x402) | Authorisation status, sale and use deadlines, use by use, for 1 to 20 products |
| `phyto_example` | free | A real answer (a fungicide in its sale grace period, computed as of 2026-11-09) to see the output shape |

**Input of `phyto_lookup`:**

- `produits`: 1 to 20 AMM numbers (7 digits) or trade names (accents and case ignored), comma-separated. A name not found returns suggestions. Invalid input is refused and never charged.
- `culture` (optional): a crop word as written in E-Phy (`Vigne`, `Blé`, `Pommier`…), to filter the uses.
- `date` (optional): `YYYY-MM-DD`, default today, to plan a treatment.

## Example output

The fungicide BRIVELA was withdrawn on 6 September 2026. It can still be sold until 6 March 2027 and used until 6 March 2028.

```json
{
  "date_calcul": "2026-11-09",
  "culture": null,
  "produits_en_delai_de_grace": 1,
  "produits_interdits": 0,
  "resultats": [{
    "saisie": "BRIVELA",
    "trouve": true,
    "produits": [{
      "amm": "2210556",
      "nom": "BRIVELA",
      "fonctions": "Fongicide",
      "etat_autorisation": "RETIRE",
      "date_retrait_produit": "2026-09-06",
      "verdict": "delai_de_grace_vente",
      "vente_permise": true,
      "utilisation_permise": true,
      "derniere_fin_vente": "2027-03-06",
      "derniere_fin_utilisation": "2028-03-06",
      "jours_avant_prochaine_echeance": 117,
      "usages": [{
        "usage": "Blé*Trt Part.Aer.*Rouille(s)",
        "verdict": "delai_de_grace_vente",
        "fin_vente": "2027-03-06",
        "fin_utilisation": "2028-03-06",
        "dose": "1.5 L/ha"
      }]
    }]
  }],
  "donnees": { "millesime": "2026-11-03", "adresse": "https://www.data.gouv.fr/datasets/575e9fac88ee38072a640390/" },
  "source": "Catalogue E-Phy, Anses, data.gouv.fr (Licence Ouverte) ; délai de grâce : art. 46 du règlement (CE) n° 1107/2009",
  "avertissement": "Information, pas un conseil réglementaire. Seule la décision de l'Anses fait foi…"
}
```

Field names are in French. `verdict` is one of `autorise`, `delai_de_grace_vente`, `delai_de_grace_utilisation`, `interdit`, `aucun_usage_pour_cette_culture`. The product verdict is the most permissive status among the uses considered: filter by crop for a precise answer.

## Connect

Any MCP client can connect and call `phyto_example`. Calling `phyto_lookup` returns an x402 *payment required* answer: the client must support x402 payments to pay it (see below).

**Claude Code**

```bash
claude mcp add --transport http sentinelle-phyto https://phyto.amacunia.fr/mcp
```

**Claude Desktop / claude.ai:** Settings, Connectors, *Add custom connector*, URL `https://phyto.amacunia.fr/mcp`.

**Cursor** (`~/.cursor/mcp.json`)

```json
{ "mcpServers": { "sentinelle-phyto": { "url": "https://phyto.amacunia.fr/mcp" } } }
```

**VS Code** (`.vscode/mcp.json`)

```json
{ "servers": { "sentinelle-phyto": { "type": "http", "url": "https://phyto.amacunia.fr/mcp" } } }
```

## Paying with x402

The paid tool follows the x402 MCP convention: the first call returns the payment requirements (scheme `exact`, network Base `eip155:8453`, asset USDC, amount `10000` = 0.01 USDC); the client signs a payment, puts it in the request `_meta` under `x402/payment`, and calls again. The payment is settled only if the tool succeeds: invalid input is never charged.

A minimal Python client with the official `x402` SDK is in [`examples/pay_mcp.py`](examples/pay_mcp.py). The same service is also sold over plain HTTP (`GET /v1/phyto`, HTTP 402 then retry), which every x402 HTTP client supports.

## Data and limits

- Source: E-Phy, the register of plant protection products of the Agence nationale de sécurité sanitaire de l'alimentation, de l'environnement et du travail (Anses), published on data.gouv.fr under the Licence Ouverte (Etalab), refreshed every 12 hours (Anses publishes weekly).
- Rule, per use: on or before `fin_vente`, sale and use are allowed; after it and on or before `fin_utilisation`, only the use of existing stocks; after that, forbidden.
- Old withdrawals may carry no published grace dates (`retrait_sans_delai_de_grace_publie`): treat them as forbidden.
- Parallel trade permits are not covered yet.
- No personal data is returned or stored.
- Information only, not regulatory advice. The Anses decision and the label prevail.

## Same author

- [Sentinelle créances](https://github.com/Marcoco27/sentinelle-creances-mcp): French insolvency notices per company and the creditor claim filing deadline.
- [Sentinelle catnat](https://github.com/Marcoco27/sentinelle-catnat-mcp): French natural-disaster decrees per commune and the open insurance-claim deadline.

## About this repository

This repository holds the public documentation, the MCP Registry manifest ([`server.json`](server.json)) and client examples. The service itself runs at `phyto.amacunia.fr`. Issues and questions are welcome; contact: contact@amacunia.fr.

---

### En français

Serveur MCP et API payable à l'appel pour les agents IA : pour un produit phytosanitaire (numéro d'AMM ou nom commercial), dit s'il est autorisé, encore vendable ou seulement utilisable, usage par usage, et jusqu'à quelle date, d'après le catalogue E-Phy de l'Anses. Un centime de dollar par appel (protocole x402, USDC sur Base), jusqu'à 20 produits. Information, pas un conseil réglementaire. Présentation : https://phyto.amacunia.fr
