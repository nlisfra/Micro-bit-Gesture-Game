import pandas as pd
import numpy as np
import glob
import os
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings('ignore')


class PreprocessingData:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_map = {"tilt_left": 0, "up": 1, "tilt_right": 2}
        self.reverse_label_map = {0: "tilt_left", 1: "up", 2: "tilt_right"}
        self.colors = {
            "tilt_left": "#FF4B4B",
            "tilt_right": "#4CAF50", 
            "up": "#2196F3"
        }
        self.N_FEATURES = 15

    def load_all_data(self, data_folder="./"):
        csv_files = glob.glob(os.path.join(data_folder, "data_*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"Tidak ada file data_*.csv ditemukan")

        print(f"\n{'='*50}")
        print("LOAD DATA")
        print('='*50)
        print(f"File ditemukan: {len(csv_files)}")

        df_list = []
        stats = {"tilt_left": 0, "up": 0, "tilt_right": 0}

        for file in csv_files:
            fname = os.path.basename(file)
            df = None

            # Coba separator berbeda untuk membaca CSV
            for sep in ["\t", ";", ","]:
                try:
                    tmp = pd.read_csv(file, sep=sep, on_bad_lines='skip')
                    if len(tmp.columns) >= 3:
                        df = tmp
                        break
                except:
                    continue

            if df is None or len(df.columns) < 3:
                print(f"  ✗ {fname} - format salah")
                continue

            if "data.0" in df.columns:
                df = df.rename(columns={"data.0": "ax", "data.1": "ay", "data.2": "az"})
                df = df[["ax", "ay", "az"]]
            elif all(col in df.columns for col in ["ax", "ay", "az"]):
                df = df[["ax", "ay", "az"]]
            else:
                df = df.iloc[:, -3:]
                df.columns = ["ax", "ay", "az"]

            for col in ["ax", "ay", "az"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna()
            
            if len(df) < 10:
                print(f"  ✗ {fname} - data terlalu sedikit ({len(df)} baris)")
                continue

            name = fname.lower()
            if "left" in name:
                label = "tilt_left"
            elif "right" in name:
                label = "tilt_right"
            elif "up" in name or "atas" in name:
                label = "up"
            else:
                print(f"  ✗ {fname} - label tidak dikenal")
                continue

            df["label"] = label
            stats[label] += len(df)
            print(f"  ✓ {fname:<20} {len(df):4d} baris ({label})")
            df_list.append(df)

        if not df_list:
            raise ValueError("Tidak ada data valid!")

        combined = pd.concat(df_list, ignore_index=True)
        
        print("-"*50)
        print(f"Total data: {len(combined)} baris")
        for label, count in stats.items():
            print(f"  {label:<11}: {count} baris ({count/len(combined)*100:.1f}%)")

        return combined

    def clean_data(self, df):
        print("\n" + "="*50)
        print("CLEANING DATA")
        print("="*50)
        
        awal = len(df)
        df = df.drop_duplicates(subset=["ax", "ay", "az"])
        print(f"Duplikat: {awal - len(df)} dihapus")
        
        for col in ["ax", "ay", "az"]:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df = df[(df[col] >= Q1 - 1.5*IQR) & (df[col] <= Q3 + 1.5*IQR)]
        
        print(f"Data akhir: {len(df)} baris")
        return df.reset_index(drop=True)

    def extract_features(self, window):
        features = []
        for axis in range(3):
            col = window[:, axis]
            features.extend([
                np.mean(col), np.std(col), 
                np.min(col), np.max(col),
                np.max(col) - np.min(col)
            ])
        return np.array(features)

    def create_windows(self, df, window_size=50, step_size=25):
        print("\n" + "="*50)
        print("WINDOWING")
        print("="*50)
        print(f"Window size: {window_size}, Step: {step_size}")
        
        X, y = [], []
        
        for label in df["label"].unique():
            sub = df[df["label"] == label].reset_index(drop=True)
            data = sub[["ax", "ay", "az"]].values
            label_code = self.label_map[label]
            
            for start in range(0, len(data) - window_size + 1, step_size):
                window = data[start:start+window_size]
                X.append(self.extract_features(window))
                y.append(label_code)
            
            print(f"  {label:<11}: {len(X) - len(y) + 1} windows")

        X = np.array(X)
        y = np.array(y)
        print(f"\nTotal windows: {len(X)}")
        return X, y

    def normalize_features(self, X_train, X_test):
        print("\n" + "="*50)
        print("NORMALISASI")
        print("="*50)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"Mean setelah normalisasi: {np.mean(X_train_scaled):.3f}")
        print(f"Std setelah normalisasi : {np.std(X_train_scaled):.3f}")
        return X_train_scaled, X_test_scaled

    def plot_bar_distribution(self, df, filename="bar_distribution.png"):
        counts = df["label"].value_counts()
        
        plt.figure(figsize=(8, 5))
        bars = plt.bar(counts.index, counts.values, 
                      color=[self.colors[l] for l in counts.index])
        
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{int(bar.get_height())}', ha='center', va='bottom')
        
        plt.xlabel('Gestur')
        plt.ylabel('Jumlah Sampel')
        plt.title('Distribusi Data per Gestur')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()
        print(f"✓ {filename} saved")

    # Plot 2D scatter
    def plot_2d_distribution(self, df, filename="scatter_2d.png"):
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        pairs = [("ax", "ay"), ("ax", "az"), ("ay", "az")]

        for idx, (x, y) in enumerate(pairs):
            for label, color in self.colors.items():
                subset = df[df["label"] == label]
                axes[idx].scatter(subset[x], subset[y], c=color, alpha=0.5, s=5)
            
            axes[idx].set_xlabel(f'{x} (g)')
            axes[idx].set_ylabel(f'{y} (g)')
            axes[idx].set_title(f'{x} vs {y}')
            axes[idx].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()
        print(f"✓ {filename} saved")

    # Plot 3D scatter
    def plot_3d_distribution(self, df, filename="scatter_3d.png"):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        for label, color in self.colors.items():
            subset = df[df["label"] == label]
            ax.scatter(subset["ax"], subset["ay"], subset["az"],
                      c=color, label=label, alpha=0.4, s=3)

        ax.set_xlabel('AX (g)')
        ax.set_ylabel('AY (g)')
        ax.set_zlabel('AZ (g)')
        ax.set_title('Distribusi Data 3D')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()
        print(f"✓ {filename} saved")

    def process_pipeline(self, data_folder="./", test_size=0.2, 
                        window_size=50, step_size=25, random_state=42):
        print("\n" + "="*50)
        print("PREPROCESSING DATA")
        print("="*50)

        # Load data
        df = self.load_all_data(data_folder)
        
        # Clean data
        df = self.clean_data(df)
        
        # Windowing
        X_all, y_all = self.create_windows(df, window_size, step_size)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_all, y_all, test_size=test_size, 
            random_state=random_state, stratify=y_all
        )
        
        print("\n" + "="*50)
        print("SPLIT DATA")
        print("="*50)
        print(f"Train: {len(X_train)} windows ({len(X_train)/len(X_all)*100:.1f}%)")
        print(f"Test : {len(X_test)} windows ({len(X_test)/len(X_all)*100:.1f}%)")
        
        # Normalisasi
        X_train_scaled, X_test_scaled = self.normalize_features(X_train, X_test)
        
        # Visualisasi
        print("\n" + "="*50)
        print("VISUALISASI")
        print("="*50)
        self.plot_bar_distribution(df)
        self.plot_2d_distribution(df)
        self.plot_3d_distribution(df)
        
        np.savez_compressed("preprocessed_data.npz",
            X_train=X_train_scaled, X_test=X_test_scaled,
            y_train=y_train, y_test=y_test,
            label_map=self.label_map
        )
        
        with open("scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)
        
        print("\n" + "="*50)
        print("PREPROCESSING SELESAI")
        print("="*50)
        print("\nFile output:")
        print("  - preprocessed_data.npz")
        print("  - scaler.pkl")
        print("  - bar_distribution.png")
        print("  - scatter_2d.png")
        print("  - scatter_3d.png")

        return X_train_scaled, X_test_scaled, y_train, y_test, self.label_map


if __name__ == "__main__":
    processor = PreprocessingData()
    
    X_train, X_test, y_train, y_test, label_map = processor.process_pipeline(
        data_folder="./",
        test_size=0.2,
        window_size=50,
        step_size=25,
        random_state=42
    )
    
    print("\n" + "="*50)
    print("RINGKASAN")
    print("="*50)
    print(f"Fitur per sampel: {X_train.shape[1]} (15)")
    print(f"Train samples   : {len(X_train)}")
    print(f"Test samples    : {len(X_test)}")
    print(f"Kelas           : {label_map}")
    print("="*50)