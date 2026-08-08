#!/usr/bin/env python3
"""Medlit search: NCBI E-utilities (PubMed) + Europe PMC REST API.

Commands:
  search pubmed|epmc QUERY [--max N]
  abstract PMID
  fetch PMID [PMID ...]

NCBI API key resolution (never printed):
  1. env NCBI_API_KEY
  2. 1Password via: op read "op://Private/NCBI E-utilities API Key/password"
  3. keyless mode (3 req/s)
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
OP_REFERENCE = "op://Private/NCBI E-utilities API Key/password"


def resolve_ncbi_key():
    key = os.environ.get("NCBI_API_KEY")
    if key:
        return key
    try:
        out = subprocess.run(
            ["op", "read", OP_REFERENCE],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def http_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def ncbi_params(params, key):
    if key:
        params["api_key"] = key
    return params


def ncbi_search(term, max_records=10):
    key = resolve_ncbi_key()
    p = ncbi_params({"db": "pubmed", "term": term, "retmax": str(max_records), "retmode": "json"}, key)
    data = http_json(f"{NCBI_EUTILS}/esearch.fcgi?" + urllib.parse.urlencode(p))["esearchresult"]
    ids = data.get("idlist", [])
    if not ids:
        return []
    p = ncbi_params({"db": "pubmed", "id": ",".join(ids), "retmode": "json"}, key)
    summ = http_json(f"{NCBI_EUTILS}/esummary.fcgi?" + urllib.parse.urlencode(p))["result"]
    out = []
    for pid in ids:
        r = summ.get(pid, {})
        out.append({
            "pmid": pid,
            "year": (r.get("pubdate") or "")[:4],
            "journal": r.get("fulljournalname", ""),
            "title": r.get("title", ""),
            "authors": [a["name"] for a in r.get("authors", [])],
        })
    return out


def epmc_search(term, max_records=10):
    p = {"query": term, "format": "json", "resultType": "core", "pageSize": str(max_records)}
    data = http_json(f"{EUROPE_PMC}/search?" + urllib.parse.urlencode(p))
    out = []
    for r in data.get("resultList", {}).get("result", []):
        out.append({
            "id": r.get("id"),
            "source": r.get("source"),
            "pmcid": r.get("pmcid"),
            "doi": r.get("doi"),
            "year": r.get("pubYear"),
            "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title", ""),
            "title": r.get("title", ""),
            "authors": r.get("authorString", ""),
        })
    return out


def ncbi_abstract(pmid):
    key = resolve_ncbi_key()
    p = ncbi_params({"db": "pubmed", "id": pmid, "retmode": "xml"}, key)
    with urllib.request.urlopen(f"{NCBI_EUTILS}/efetch.fcgi?" + urllib.parse.urlencode(p), timeout=30) as resp:
        root = ET.fromstring(resp.read())
    art = root.find(".//PubmedArticle")
    if art is None:
        return None
    abs_node = art.find(".//Abstract")
    abstract = None
    if abs_node is not None:
        abstract = " ".join("".join(seg.itertext()) for seg in abs_node.iter("AbstractText"))
    return {
        "pmid": pmid,
        "title": art.findtext(".//ArticleTitle"),
        "journal": art.findtext(".//Journal/Title"),
        "year": art.findtext(".//PubDate/Year") or art.findtext(".//PubDate/MedlineDate", ""),
        "authors": [
            f"{a.findtext('LastName')} {a.findtext('Initials')}"
            for a in art.iter("Author") if a.find("LastName") is not None
        ],
        "abstract": abstract,
    }


def ncbi_fetch(pmids):
    key = resolve_ncbi_key()
    p = ncbi_params({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}, key)
    with urllib.request.urlopen(f"{NCBI_EUTILS}/efetch.fcgi?" + urllib.parse.urlencode(p), timeout=30) as resp:
        root = ET.fromstring(resp.read())
    records = []
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//PMID")
        abs_node = art.find(".//Abstract")
        abstract = None
        if abs_node is not None:
            abstract = " ".join("".join(seg.itertext()) for seg in abs_node.iter("AbstractText"))
        authors = []
        for i, a in enumerate(art.iter("Author"), 1):
            if a.find("LastName") is None:
                continue
            authors.append({
                "position": i,
                "name": f"{a.findtext('LastName')} {a.findtext('Initials')}",
                "forename": a.findtext("ForeName") or "",
                "affiliations": [x.text for x in a.iter("Affiliation")],
            })
        doi = None
        for aid in art.iter("ArticleId"):
            if aid.get("IdType") == "doi":
                doi = aid.text
        records.append({
            "pmid": pmid,
            "title": art.findtext(".//ArticleTitle"),
            "journal": art.findtext(".//Journal/Title"),
            "year": art.findtext(".//PubDate/Year") or art.findtext(".//PubDate/MedlineDate", ""),
            "doi": doi,
            "authors": authors,
            "abstract": abstract,
        })
    return records


def main():
    p = argparse.ArgumentParser(description="Medlit search (PubMed + Europe PMC).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search", help="search a database")
    sp.add_argument("db", choices=["pubmed", "epmc"])
    sp.add_argument("term")
    sp.add_argument("--max", type=int, default=10)

    sp = sub.add_parser("abstract", help="fetch PubMed abstract by PMID")
    sp.add_argument("pmid")

    sp = sub.add_parser("fetch", help="fetch full PubMed records (authors/affiliations/abstract)")
    sp.add_argument("pmids", nargs="+")

    args = p.parse_args()

    if args.cmd == "search":
        rows = ncbi_search(args.term, args.max) if args.db == "pubmed" else epmc_search(args.term, args.max)
        for r in rows:
            print(f"{r.get('pmid') or r.get('id')} | {r.get('year')} | {r.get('journal')} | {r['title']}")
    elif args.cmd == "abstract":
        rec = ncbi_abstract(args.pmid)
        if not rec:
            print("not found")
            sys.exit(1)
        print(f"{rec['title']}\n{rec['journal']} ({rec['year']}) | PMID {rec['pmid']}")
        print("Authors:", ", ".join(rec["authors"]))
        print("\nAbstract:\n" + (rec["abstract"] or "(none)"))
    elif args.cmd == "fetch":
        for rec in ncbi_fetch(args.pmids):
            print(f"PMID {rec['pmid']} | {rec['year']} | {rec['journal']} | DOI: {rec.get('doi')}")
            print(f"  Title: {rec['title']}")
            for a in rec["authors"]:
                aff = "; ".join(a["affiliations"][:2])
                print(f"  {a['position']}. {a['name']} ({a['forename']}) | {aff}")
            print(f"  Abstract: {(rec['abstract'] or '(none)')[:500]}")
            print()


if __name__ == "__main__":
    main()
