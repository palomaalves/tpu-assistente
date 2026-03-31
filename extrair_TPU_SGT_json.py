"""
Extrator de Tabelas Processuais Unificadas (TPU) - SGT/CNJ
Fonte: https://www.cnj.jus.br/sgt/sgt_ws.php

Gera arquivos JSON para uso no Assistente TPU (Artifact no Claude).

Dependências:
    pip install requests

Uso:
    python extrair_TPU_SGT_json.py

Saída em Documentos:
    classes_sgt_cnj.json       <- faz upload deste no Artifact
    assuntos_sgt_cnj.json      <- faz upload deste no Artifact
    movimentos_sgt_cnj.json    <- faz upload deste no Artifact
"""

import time, json, requests, xml.etree.ElementTree as ET
from pathlib import Path

SOAP_URL  = "https://www.cnj.jus.br/sgt/sgt_ws.php"
NAMESPACE = "https://www.cnj.jus.br/sgt/sgt_ws.php"
DELAY     = 0.20
TIMEOUT   = 30

DOCS = Path.home() / "Documents"
DOCS.mkdir(exist_ok=True)

TABELAS = {
    "C": ("Classes",    DOCS / "classes_sgt_cnj"),
    "A": ("Assuntos",   DOCS / "assuntos_sgt_cnj"),
    "M": ("Movimentos", DOCS / "movimentos_sgt_cnj"),
}

TIPO_ITEM = "C"


def _envelope(action, corpo):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<SOAP-ENV:Envelope '
        '  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" '
        f' xmlns:ns1="{NAMESPACE}">'
        '<SOAP-ENV:Body>'
        f'<ns1:{action}>{corpo}</ns1:{action}>'
        '</SOAP-ENV:Body>'
        '</SOAP-ENV:Envelope>'
    )


def _chamar(action, corpo):
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction":   f"{NAMESPACE}#{action}",
    }
    try:
        resp = requests.post(SOAP_URL,
            data=_envelope(action, corpo).encode("utf-8"),
            headers=headers, timeout=TIMEOUT)
        time.sleep(DELAY)
        return resp.text
    except requests.RequestException as e:
        print(f"  Erro: {e}")
        return None


def _texto(el):
    return (el.text or "").strip() if el is not None else ""


def get_filhos(seq_item):
    xml_resp = _chamar(
        "getArrayFilhosItemPublicoWS",
        f"<seqItem>{seq_item}</seqItem><tipoItem>{TIPO_ITEM}</tipoItem>",
    )
    if not xml_resp:
        return []
    try:
        root = ET.fromstring(xml_resp)
    except ET.ParseError as e:
        print(f"  XML inválido (seq={seq_item}): {e}")
        return []
    itens, vistos = [], set()
    for item in root.iter(f"{{{NAMESPACE}}}ArvoreGenerica"):
        seq  = _texto(item.find("seq_elemento"))
        nome = _texto(item.find("dsc_elemento"))
        if seq and nome and seq not in vistos:
            vistos.add(seq)
            itens.append({
                "seq":        seq,
                "nome":       nome,
                "ativo":      _texto(item.find("situacao")) or "S",
                "glossario":  _texto(item.find("glossario")) or "",
                "tem_filhos": _texto(item.find("temFilhos")) == "1",
            })
    return itens


def percorrer_arvore(seq_item, nivel, nomes, codigos, registros, total):
    for filho in get_filhos(seq_item):
        cod   = filho["seq"]
        nome  = filho["nome"]
        ativo = filho["ativo"]
        gloss = filho["glossario"]

        registros.append({
            "codigo":     cod,
            "nome":       nome,
            "nivel":      nivel,
            "hierarquia": " > ".join(nomes + [nome]),
            "codigo_pai": codigos[-1] if codigos else "0",
            "nome_pai":   nomes[-1]   if nomes   else "RAIZ",
            "ativo":      "Sim" if ativo.upper() in ("S", "SIM", "1", "TRUE", "A") else "Nao",
            "glossario":  (gloss or "")[:500],
        })
        total[0] += 1
        if total[0] % 50 == 0:
            print(f"  {total[0]} itens... nivel {nivel}: {nome[:50]}", flush=True)

        if filho["tem_filhos"] and cod.isdigit():
            percorrer_arvore(int(cod), nivel + 1,
                             nomes + [nome], codigos + [cod],
                             registros, total)


def salvar_json(registros, caminho_base):
    arquivo = Path(str(caminho_base) + ".json")
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, separators=(",", ":"))
    kb = arquivo.stat().st_size // 1024
    print(f"  JSON: {arquivo}  ({kb} KB)")


def main():
    print("=" * 60)
    print("Extrator TPU — SGT/CNJ  (apenas JSON)")
    print("=" * 60)

    xml_v = _chamar("getDataUltimaVersao", "")
    if xml_v:
        try:
            for el in ET.fromstring(xml_v).iter("return"):
                print(f"Versao das tabelas: {_texto(el)}")
                break
        except ET.ParseError:
            pass

    for tipo, (nome, caminho) in TABELAS.items():
        global TIPO_ITEM
        TIPO_ITEM = tipo
        print(f"\n{'=' * 60}\nExtraindo: {nome} (tipo='{tipo}')\n{'=' * 60}", flush=True)

        registros, total = [], [0]
        percorrer_arvore(0, 1, [], [], registros, total)

        if not registros:
            print(f"  Nenhum registro encontrado.")
            continue

        print(f"\n  Total {nome.lower()}: {len(registros)}")
        salvar_json(registros, caminho)

    print(f"\n{'=' * 60}")
    print(f"Concluido! JSONs em: {DOCS}")
    print("=" * 60)
    print("\nProximo passo — no Assistente TPU (Artifact):")
    print("  Aba 'Carregar Tabelas' > Upload manual")
    print("  Selecione os 3 arquivos .json gerados")


if __name__ == "__main__":
    main()
