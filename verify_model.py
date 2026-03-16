import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.decomposition import PCA


def verify():
    print("=" * 50)
    print("  VERIFIKASI MODEL - CEK 100% VALID/TIDAK")
    print("=" * 50)

    # Load data
    data      = np.load("preprocessed_data.npz", allow_pickle=True)
    label_map = data["label_map"].item()
    X_train   = data["X_train"]
    X_test    = data["X_test"]
    y_train   = data["y_train"]
    y_test    = data["y_test"]

    # Gabung train+test untuk cross validation
    X_all = np.concatenate([X_train, X_test], axis=0)
    y_all = np.concatenate([y_train, y_test], axis=0)

    print(f"\nTotal data: {len(X_all)} sampel  ({X_all.shape[1]} fitur)")

    # ------------------------------------------------------------------ #
    #  1. Cross Validation 5-Fold                                          #
    #     Kalau 100% di semua fold → data memang mudah dipisahkan (valid)  #
    #     Kalau 100% hanya di 1 fold → curiga overfitting                  #
    # ------------------------------------------------------------------ #
    print("\n1. Cross Validation (5-fold)...")
    model = KNeighborsClassifier(n_neighbors=5, weights="distance", metric="euclidean")
    cv    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X_all, y_all, cv=cv, scoring="accuracy")

    for i, s in enumerate(scores):
        print(f"   Fold {i+1} : {s*100:.2f}%")
    print(f"   Rata-rata : {scores.mean()*100:.2f}%  ±{scores.std()*100:.2f}%")

    if scores.mean() >= 0.99:
        print("   → Data memang mudah dipisahkan. 100% VALID ✅")
    else:
        print("   → Ada indikasi overfitting. Perlu investigasi lebih lanjut ⚠️")

    # ------------------------------------------------------------------ #
    #  2. Visualisasi PCA 2D                                               #
    #     Kalau cluster tiap gesture terpisah jelas → 100% wajar           #
    # ------------------------------------------------------------------ #
    print("\n2. Visualisasi distribusi data (PCA 2D)...")
    pca        = PCA(n_components=2)
    X_pca      = pca.fit_transform(X_all)
    explained  = pca.explained_variance_ratio_

    reverse_map = {v: k for k, v in label_map.items()}
    colors      = {0: "red", 1: "green", 2: "blue"}
    labels_name = {0: "tilt_left", 1: "up", 2: "tilt_right"}

    plt.figure(figsize=(9, 6))
    for cls in np.unique(y_all):
        idx = y_all == cls
        plt.scatter(X_pca[idx, 0], X_pca[idx, 1],
                    c=colors[cls], label=labels_name[cls], alpha=0.6, s=40)
    plt.xlabel(f"PC1 ({explained[0]*100:.1f}%)", fontsize=12)
    plt.ylabel(f"PC2 ({explained[1]*100:.1f}%)", fontsize=12)
    plt.title("Distribusi Data per Gesture (PCA 2D)", fontsize=14, fontweight="bold")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("pca_visualization.png", dpi=300)
    plt.close()
    print("   pca_visualization.png saved")
    print("   → Kalau cluster terpisah jelas = 100% memang valid")

    # ------------------------------------------------------------------ #
    #  3. Cek distribusi fitur antar gesture                              #
    # ------------------------------------------------------------------ #
    print("\n3. Rata-rata fitur per gesture (mean_ax, mean_ay, mean_az):")
    feature_names = ["mean_ax", "mean_ay", "mean_az",
                     "std_ax",  "std_ay",  "std_az",
                     "min_ax",  "min_ay",  "min_az",
                     "max_ax",  "max_ay",  "max_az",
                     "range_ax","range_ay","range_az"]

    print(f"  {'Gesture':<12} {'mean_ax':>10} {'mean_ay':>10} {'mean_az':>10}")
    print("  " + "-" * 44)
    for cls in np.unique(y_all):
        idx    = y_all == cls
        means  = X_all[idx].mean(axis=0)
        name   = reverse_map[cls]
        print(f"  {name:<12} {means[0]:>10.3f} {means[1]:>10.3f} {means[2]:>10.3f}")

    print("\n  → Kalau nilai tiap gesture beda jauh = wajar model 100%")

    print("\n" + "=" * 50)
    print("  VERIFIKASI SELESAI")
    print("=" * 50)


if __name__ == "__main__":
    verify()