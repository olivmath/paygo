# ✅ DONE

ALICE
- SDXU6YQNO6QNZFG57PEBAXJGVD6H7XZYHXZNHA37JLZXISDT65R2ORFU
- GAVJVR4XMGIL2AGZ2RLGLPKFB3SRCUJA4TZPDWGCGDUIF5MBJC2RCQCM

OWNER
- SCI34MBIA7EIDM3VOIMNGMGWCGD7IZAJ76GHPSFBMDIXT4GIOPFGPAFL
- GDGHOLXLDKHP7IQCAY5L66MQIUMLTYOHKJV7SVFESW3BAE7YO3ZWCJJA

TOKEN [LLS]
- CA54TMK5MZEBBOIPIFFRGRECKMW5MANBNLR5OZIXG3C3CEXNE6ZGTSOK

PAYGO
- CDZ56RS5Z4MQH5S3VUTWWG6GHZ4KBCMMC6SO6WDSO5PNZL6EH6SBYRZP



## Fund Wallet

```bash
stellar keys fund alice --network testnet
```

## Upload Smartcontract

```bash
# TOKEN
stellar contract upload --source-account=alice --wasm=target/wasm32-unknown-unknown/release/token.wasm --network testnet
```

```bash
# PAYGO
stellar contract upload --source-account=alice --wasm=target/wasm32-unknown-unknown/release/paygo.wasm  --network testnet
```

```bash
# COMPANY
stellar contract upload --source-account=alice --wasm=target/wasm32-unknown-unknown/release/company.wasm  --network testnet
```

## Deploy Smartcontract

```bash
stellar contract deploy --source-account=alice --wasm-hash=0108c762ca6f8441564b0ef032dbb6a600f7f4de3df65f844e51d875979c51e2  --network testnet -- --admin alice --name "lucas" --symbol "LLS" --decimal 7
```

```bash
stellar contract deploy \
  --source-account=alice \
  --wasm-hash=9d1f5b4f76e6e45f2ce35d6888c75973b8c8b69d80ac3c75c72d27b9007a83fd \
  --network testnet \
  -- \
  --usdc=CA54TMK5MZEBBOIPIFFRGRECKMW5MANBNLR5OZIXG3C3CEXNE6ZGTSOK \
  --company_wasm_hash=79767805f76970e64d3cd32a1d26f8645d481ec3b9dc031e27217e8edcf17feb
```

## Invoke


```bash
stellar contract invoke \
  --source-account=alice \
  --id=CA54TMK5MZEBBOIPIFFRGRECKMW5MANBNLR5OZIXG3C3CEXNE6ZGTSOK \
  --network testnet \
  -- mint \
  --to owner \
  --amount 200000000000
```

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


