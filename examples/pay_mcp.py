# /// script
# requires-python = ">=3.12"
# dependencies = ["x402[evm,mcp]>=2.27"]
# ///
"""Call the paid MCP tool phyto_lookup and pay it with x402 (USDC on Base).

Usage:
    PRIVATE_KEY=0x... uv run examples/pay_mcp.py BRIVELA,2120131 [crop, e.g. Vigne]

PRIVATE_KEY is the key of a wallet holding a little USDC on Base. Use a dedicated,
low-balance wallet: never your main one. Each call costs 0.01 USDC; no ETH is needed
for gas, the facilitator pays it.
"""
import asyncio
import os
import sys

from eth_account import Account
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from x402 import x402Client
from x402.mcp.client import x402MCPSession
from x402.mechanisms.evm.exact import ExactEvmClientScheme
from x402.mechanisms.evm.signers import EthAccountSigner

URL = "https://phyto.amacunia.fr/mcp"


async def main() -> None:
    produits = sys.argv[1] if len(sys.argv) > 1 else "BRIVELA"
    culture = sys.argv[2] if len(sys.argv) > 2 else ""
    payer = x402Client()
    payer.register("eip155:8453", ExactEvmClientScheme(
        EthAccountSigner(Account.from_key(os.environ["PRIVATE_KEY"]))))

    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            mcp = x402MCPSession(session, payer)
            await mcp.initialize()
            result = await mcp.call_tool("phyto_lookup", {"produits": produits, "culture": culture})
            text = result.content[0].text if result.content else ""
            if result.is_error:
                print("Call refused (payment or input):", text[:400])
                return
            print("Settlement:", result.payment_response)
            print(text)


asyncio.run(main())
