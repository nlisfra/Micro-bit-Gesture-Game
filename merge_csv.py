import pandas as pd
import glob
import os

# ================================
# CONFIG
# ================================
DATA_FOLDER = "./"

GESTURE_MAP = {
    "tilt_left":  ["kiri", "datakiri", "kirii", "kiri1"],
    "tilt_right": ["kanan", "datakanan", "kanann", "kanan1", "right", "data_right", "right1"],
    "up":         ["atas", "data_up", "atas1", "up1", "upp", "atass", "up_"],
}

OUTPUT_MAP = {
    "tilt_left":  "data_tilt_left.csv",
    "tilt_right": "data_tilt_right.csv",
    "up":         "data_up.csv",
}


# ================================
# READ CSV SAFE
# ================================
def read_csv_safe(filepath):
    for sep in ["\t", ";", ","]:
        try:
            df = pd.read_csv(
                filepath,
                sep=sep,
                skiprows=(1 if sep == "\t" else 0),
                on_bad_lines="skip"
            )
            if len(df.columns) >= 3:
                return df
        except Exception:
            pass
    return None


# ================================
# MERGE FUNCTION
# ================================
def merge():

    all_csv = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))

    # Jangan baca file output lama
    output_names = set(OUTPUT_MAP.values())
    all_csv = [f for f in all_csv if os.path.basename(f) not in output_names]

    print("=" * 50)
    print("MERGE CSV GESTURE")
    print("=" * 50)
    print(f"{len(all_csv)} file CSV ditemukan\n")

    for gesture, keywords in GESTURE_MAP.items():

        matched = []

        for f in all_csv:
            fname = os.path.basename(f).lower().replace(" ", "_")
            if any(kw in fname for kw in keywords):
                matched.append(f)

        if not matched:
            print(f"[{gesture}] Tidak ada file cocok\n")
            continue

        print(f"[{gesture}] {len(matched)} file ditemukan:")

        df_list = []

        for f in sorted(matched):
            df = read_csv_safe(f)

            if df is None:
                print(f"  Skip {os.path.basename(f)} — tidak bisa dibaca")
                continue

            # Rename kolom jadi konsisten
            if "data.0" in df.columns:
                rename_map = {}
                if "time (source1)" in df.columns:
                    rename_map["time (source1)"] = "time"
                rename_map["data.0"] = "ax"
                rename_map["data.1"] = "ay"
                rename_map["data.2"] = "az"
                df = df.rename(columns=rename_map)

                cols = [c for c in ["time", "ax", "ay", "az"] if c in df.columns]
                df = df[cols]
            else:
                # fallback ambil 4 kolom pertama
                df = df.iloc[:, :4]
                df.columns = ["time", "ax", "ay", "az"]

            df = df.dropna()

            print(f"  {os.path.basename(f)} → {len(df)} rows")
            df_list.append(df)

        if not df_list:
            print("  Tidak ada data valid\n")
            continue

        combined = pd.concat(df_list, ignore_index=True)

        out_path = os.path.join(DATA_FOLDER, OUTPUT_MAP[gesture])

        # Hapus file lama jika ada (hindari PermissionError)
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except PermissionError:
                print(f"\n❌ File {OUTPUT_MAP[gesture]} sedang terbuka!")
                print("   Tutup file di Excel / VSCode lalu jalankan ulang.\n")
                continue

        combined.to_csv(out_path, index=False)

        print(f"  ✔ Disimpan: {OUTPUT_MAP[gesture]} "
              f"({len(combined)} rows total)\n")

    print("=" * 50)
    print("SELESAI! File siap untuk preprocessing.")
    print("=" * 50)


# ================================
# RUN
# ================================
if __name__ == "__main__":
    merge()