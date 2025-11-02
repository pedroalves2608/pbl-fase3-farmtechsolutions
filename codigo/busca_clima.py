#!/usr/bin/env python3
"""
Phase 1 — Step 1: Fetch weather data from OpenWeather and save JSON + CSV.

Usage examples:
  # Using env var
  export OPENWEATHER_API_KEY="YOUR_KEY"
  python python/fetch_weather.py --cities-file data/cities.csv --out data

  # Using CLI
  python python/fetch_weather.py --api-key YOUR_KEY --cities "Ribeirao Preto,BR;Curitiba,BR" --out data

It writes raw JSON into data/raw/*.json and a normalized CSV at data/weather.csv
"""
import os, sys, json, argparse, time, csv, pathlib
from datetime import datetime, timezone
import urllib.request
import urllib.parse

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


OW_BASE = "https://api.openweathermap.org/data/2.5"
DEFAULT_UNITS = "metric"  # Celsius
DEFAULT_LANG  = "pt_br"

def get_api_key(cli_key: str | None) -> str:
    if cli_key:
        return cli_key
    env_key = os.getenv("OPENWEATHER_API_KEY")
    if env_key:
        return env_key
    # Try config.local.json near the script
    here = pathlib.Path(__file__).resolve().parent
    cfg = here / "config.local.json"
    if cfg.exists():
        with cfg.open("r", encoding="utf-8") as f:
            key = json.load(f).get("OPENWEATHER_API_KEY")
            if key:
                return key
    sys.exit("Missing API key. Provide --api-key, set OPENWEATHER_API_KEY, or create python/config.local.json.")

def parse_cities(cities: str | None, cities_file: str | None) -> list[dict]:
    out = []
    if cities:
        # format: "City,CC;Another City,CC"
        for chunk in [c.strip() for c in cities.split(";") if c.strip()]:
            out.append({"q": chunk})
    if cities_file:
        with open(cities_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # expects columns: name,country (optional state)
            for row in reader:
                name = row.get("name","").strip()
                state = row.get("state","").strip()
                country = row.get("country","").strip()
                q = ",".join([x for x in [name, state or None, country or None] if x])
                if q:
                    out.append({"q": q})
    if not out:
        sys.exit("No cities provided. Use --cities or --cities-file.")
    return out

def http_get(url: str) -> bytes:
    with urllib.request.urlopen(url) as resp:
        return resp.read()

def fetch_city(api_key: str, query: str, units: str, lang: str) -> dict:
    # Combined: current + 5-day/3h forecast (two requests). You may adapt to OneCall if preferred.
    params = dict(q=query, appid=api_key, units=units, lang=lang)
    cur_url = f"{OW_BASE}/weather?{urllib.parse.urlencode(params)}"
    fct_url = f"{OW_BASE}/forecast?{urllib.parse.urlencode(params)}"
    cur_raw = json.loads(http_get(cur_url).decode("utf-8"))
    time.sleep(0.25)  # be nice
    fct_raw = json.loads(http_get(fct_url).decode("utf-8"))
    return {"query": query, "fetched_at": datetime.now(timezone.utc).isoformat(), "current": cur_raw, "forecast": fct_raw}

def ensure_dirs(out_dir: pathlib.Path):
    (out_dir / "raw").mkdir(parents=True, exist_ok=True)

def append_to_csv(out_dir: pathlib.Path, city_pack: dict):
    # Normalize both current and forecast into a single flat CSV
    csv_path = out_dir / "weather.csv"
    import pandas as pd  # local import to keep top clean

    rows = []
    q = city_pack["query"]
    fetched_at = city_pack["fetched_at"]

    # Current
    cur = city_pack.get("current", {}) or {}
    if cur:
        rows.append({
            "ts": datetime.utcfromtimestamp(cur.get("dt", 0)).isoformat(),
            "city_query": q,
            "fetched_at": fetched_at,
            "kind": "current",
            "name": cur.get("name"),
            "lat": cur.get("coord",{}).get("lat"),
            "lon": cur.get("coord",{}).get("lon"),
            "temp_c": (cur.get("main",{}) or {}).get("temp"),
            "humidity": (cur.get("main",{}) or {}).get("humidity"),
            "pressure": (cur.get("main",{}) or {}).get("pressure"),
            "wind_speed": (cur.get("wind",{}) or {}).get("speed"),
            "rain_1h": (cur.get("rain",{}) or {}).get("1h"),
            "weather": (cur.get("weather",[{}]) or [{}])[0].get("main"),
            "weather_desc": (cur.get("weather",[{}]) or [{}])[0].get("description"),
        })

    # Forecast list
    fct = city_pack.get("forecast", {}) or {}
    for item in (fct.get("list") or []):
        rows.append({
            "ts": datetime.utcfromtimestamp(item.get("dt", 0)).isoformat(),
            "city_query": q,
            "fetched_at": fetched_at,
            "kind": "forecast",
            "name": (fct.get("city",{}) or {}).get("name"),
            "lat": (fct.get("city",{}) or {}).get("coord",{}).get("lat"),
            "lon": (fct.get("city",{}) or {}).get("coord",{}).get("lon"),
            "temp_c": (item.get("main",{}) or {}).get("temp"),
            "humidity": (item.get("main",{}) or {}).get("humidity"),
            "pressure": (item.get("main",{}) or {}).get("pressure"),
            "wind_speed": (item.get("wind",{}) or {}).get("speed"),
            "rain_3h": (item.get("rain",{}) or {}).get("3h"),
            "pop": item.get("pop"),
            "weather": (item.get("weather",[{}]) or [{}])[0].get("main"),
            "weather_desc": (item.get("weather",[{}]) or [{}])[0].get("description"),
        })

    df = pd.DataFrame(rows)
    if csv_path.exists():
        # append without headers
        df.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8")
    else:
        df.to_csv(csv_path, index=False, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="Fetch OpenWeather data and save JSON + CSV.")
    ap.add_argument("--api-key", type=str, default=None, help="OpenWeather API key (or set OPENWEATHER_API_KEY env var)")
    ap.add_argument("--cities", type=str, default=None, help='City list like "Ribeirao Preto,BR;Curitiba,BR"')
    ap.add_argument("--cities-file", type=str, default=None, help="CSV with columns: name,state(optional),country(optional)")
    ap.add_argument("--out", type=str, default="data", help="Output folder (default: data)")
    ap.add_argument("--units", type=str, default=DEFAULT_UNITS, choices=["standard","metric","imperial"])
    ap.add_argument("--lang", type=str, default=DEFAULT_LANG)
    args = ap.parse_args()

    api_key = get_api_key(args.api_key)
    cities = parse_cities(args.cities, args.cities_file)

    out_dir = pathlib.Path(args.out)
    ensure_dirs(out_dir)

    for entry in cities:
        q = entry["q"]
        print(f"[+] Fetching {q} ...", flush=True)
        pack = fetch_city(api_key, q, args.units, args.lang)

        # Save raw JSON
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        raw_path = out_dir / "raw" / f"{q.replace(',','_')}_{stamp}.json"
        with raw_path.open("w", encoding="utf-8") as f:
            json.dump(pack, f, ensure_ascii=False, indent=2)

        # Append to CSV
        append_to_csv(out_dir, pack)

    print(f"[✓] Done. See {out_dir}/raw/*.json and {out_dir}/weather.csv")

if __name__ == "__main__":
    main()