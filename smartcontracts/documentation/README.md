## Fund Wallet

```bash
stellar keys fund alice
```

## Upload Smartcontract

```bash
# TOKEN
stellar contract upload --source-account=alice --wasm=target/wasm32-unknown-unknown/release/token.wasm
# 0108c762ca6f8441564b0ef032dbb6a600f7f4de3df65f844e51d875979c51e2
```

```bash
# PAYGO
stellar contract upload --source-account=alice --wasm=target/wasm32-unknown-unknown/release/paygo.wasm
# 6c535215a9cdc9e153aab95927b3ed22f9a17c4f257797501fef6dfc8f64a940
```

```bash
# COMPANY
stellar contract upload --source-account=alice --wasm=target/wasm32-unknown-unknown/release/company.wasm
# 342ff79cc9f6e4ef0cf477b35e5ee2ee8c087f650981f9bfda785dbe83fafee9
```

## Deploy Smartcontract

```bash
stellar contract deploy --source-account=alice --wasm-hash=0108c762ca6f8441564b0ef032dbb6a600f7f4de3df65f844e51d875979c51e2 -- --admin alice --name "lucas" --symbol "LLS" --decimal 2
TOKEN=CBJEYHPGXBLRKDDBRXTHEIZSXD5MIYS2F6CE6JR2VEWGO6KR2BLA2N4Q
```

```bash
stellar contract deploy --source-account=alice --wasm-hash=6c535215a9cdc9e153aab95927b3ed22f9a17c4f257797501fef6dfc8f64a940 -- --usdc CDDI52L55NPFXATLGMCMFMDWD4ALM5BNAZLOHPML53IF3BRPKDI4SXOV --company_wasm_hash 342ff79cc9f6e4ef0cf477b35e5ee2ee8c087f650981f9bfda785dbe83fafee9
PAYGO=CAN33EOBS3E7AAIX4BLDZ7EF3LY7HD2GTYCE453HDTHFB6JISX3C2XNY
```

## Invoke Paygo

```bash
# PAYGO: buy my new company
stellar contract invoke \
  --source-account=alice \
  --id=CAN33EOBS3E7AAIX4BLDZ7EF3LY7HD2GTYCE453HDTHFB6JISX3C2XNY \
  -- create_company \
  --owner alice \
  --company_name "Petrobras" \
  --company_description "Oil and gas exploring" \
  --employees '[{"name": "Funcionario1", "account_id": "GABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", "budget": 1000}, {"name": "Funcionario2", "account_id": "GB1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", "budget": 1500}]'
```
