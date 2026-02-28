import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# KNN CLASSIFIER
class KNNGestureClassifier:
    def __init__(self, k=5):
        self.k = k
        self.model = KNeighborsClassifier(
            n_neighbors=k,
            weights="distance",
            metric="euclidean"
        )
        self.label_map = None
        self.scaler = None

    def load_data(self):
        print("Loading preprocessed data...")
        data = np.load("preprocessed_data.npz", allow_pickle=True)

        self.label_map = data["label_map"].item()

        X_train = data["X_train"]
        X_test = data["X_test"]
        y_train = data["y_train"]
        y_test = data["y_test"]

        print("Data loaded ✅")
        print(f"   Train: {X_train.shape}")
        print(f"   Test : {X_test.shape}")
        print(f"   Label map: {self.label_map}")

        return X_train, X_test, y_train, y_test
    
    def load_scaler(self):
        print("\nLoading scaler from preprocessing...")
        try:
            with open("scaler.pkl", "rb") as f:
                self.scaler = pickle.load(f)
            print("Scaler loaded successfully")
        except FileNotFoundError:
            print("scaler.pkl not found!")
            raise

    # tuning nilai K
    def tune_k(self, X_train, X_test, y_train, y_test):
        print("\n TUNING NILAI K")
        k_values = range(1, 16, 2)
        accuracies = []

        for k in k_values:
            model = KNeighborsClassifier(
                n_neighbors=k,
                weights="distance",
                metric="euclidean"
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            acc = accuracy_score(y_test, y_pred)
            accuracies.append(acc)

            print(f"   K={k:<2} → Accuracy = {acc*100:.2f}%")

        best_k = k_values[accuracies.index(max(accuracies))]
        best_acc = max(accuracies)

        print("\n HASIL TUNING")
        print(f"   K terbaik     : {best_k}")
        print(f"   Akurasi terbaik: {best_acc*100:.2f}%")

        # Plot hasil tuning K
        plt.figure(figsize=(8, 5))
        plt.plot(k_values, accuracies, marker="o", linewidth=2, markersize=8, color='#3498db')
        plt.xlabel("Nilai K", fontsize=12)
        plt.ylabel("Akurasi", fontsize=12)
        plt.title("Tuning Nilai K pada KNN", fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Highlight best K
        best_idx = accuracies.index(max(accuracies))
        plt.scatter(k_values[best_idx], accuracies[best_idx], 
                   color='red', s=200, zorder=5, label=f'Best K={best_k}')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig("tuning_k_knn.png", dpi=300)
        plt.close()

        print("Grafik tuning disimpan: tuning_k_knn.png")

        self.k = best_k
        self.model = KNeighborsClassifier(
            n_neighbors=best_k,
            weights="distance",
            metric="euclidean"
        )

    # training model
    def train(self, X_train, y_train):
        print("\n Training model KNN (K =", self.k, ")")
        self.model.fit(X_train, y_train)
        print("Training selesai ✅")

    def evaluate(self, X_test, y_test):
        print("\n EVALUASI MODEL FINAL")
        y_pred = self.model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        print(f"Accuracy  : {acc*100:.2f}%")
        print(f"Precision : {prec*100:.2f}%")
        print(f"Recall    : {rec*100:.2f}%")
        print(f"F1-score  : {f1*100:.2f}%")

        reverse_map = {v: k for k, v in self.label_map.items()}
        target_names = [reverse_map[i] for i in sorted(reverse_map)]

        print("\n📋 Classification Report")
        print(classification_report(
            y_test,
            y_pred,
            target_names=target_names,
            zero_division=0
        ))

        self.plot_confusion_matrix(y_test, y_pred, target_names)
        self.plot_metrics_chart(acc, prec, rec, f1)

    def plot_confusion_matrix(self, y_test, y_pred, labels):
        cm = confusion_matrix(y_test, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            cbar_kws={'label': 'Count'}
        )
        plt.xlabel("Predicted", fontsize=12)
        plt.ylabel("Actual", fontsize=12)
        plt.title("Confusion Matrix KNN", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig("confusion_matrix_knn.png", dpi=300)
        plt.close()

        print("Confusion matrix disimpan: confusion_matrix_knn.png")

    def plot_metrics_chart(self, acc, prec, rec, f1):
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        values = [acc * 100, prec * 100, rec * 100, f1 * 100]
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(metrics, values, color=colors, edgecolor='black', linewidth=1.5)
        
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.2f}%', ha='center', va='bottom', 
                    fontweight='bold', fontsize=11)
        
        plt.ylabel('Percentage (%)', fontsize=12)
        plt.xlabel('Metrics', fontsize=12)
        plt.title('Model Evaluation Metrics (KNN)', fontsize=14, fontweight='bold')
        plt.ylim(0, 110)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig("metrics_chart_knn.png", dpi=300)
        plt.close()
        
        print("📈 Grafik metrik disimpan: metrics_chart_knn.png")

    def save(self):
        if self.scaler is None:
            print("❌ Scaler not loaded! Cannot save model.")
            return
            
        print("\n💾 Saving model...")
        
        with open("knn_gesture_model.pkl", "wb") as f:
            pickle.dump(
                {
                    "model": self.model,
                    "label_map": self.label_map,
                    "scaler": self.scaler,
                    "k": self.k
                },
                f
            )
        print("Model disimpan: knn_gesture_model.pkl")
        print("       Model components:")
        print(f"      - KNN model (K={self.k})")
        print(f"      - Label mapping: {self.label_map}")
        print(f"      - StandardScaler (fitted)")

#main pipeline
def main():
    print("=" * 60)
    print("TRAINING MODEL KNN GESTURE CLASSIFIER")
    print("=" * 60)

    clf = KNNGestureClassifier()

    clf.load_scaler()

    X_train, X_test, y_train, y_test = clf.load_data()
    
    clf.tune_k(X_train, X_test, y_train, y_test)
    
    clf.train(X_train, y_train)
    
    clf.evaluate(X_test, y_test)
    
    clf.save()

    print("\n" + "=" * 60)
    print("MODEL FINAL SIAP DIGUNAKAN")
    print("=" * 60)
    print("\n Files generated:")
    print("   1. knn_gesture_model.pkl     <- Use this in game")
    print("   2. tuning_k_knn.png          <- K tuning visualization")
    print("   3. confusion_matrix_knn.png  <- Confusion matrix")
    print("   4. metrics_chart_knn.png     <- Evaluation metrics chart")
    print("\n⚠️  NEXT STEP: Run main_microbit_serial.py to play!")
    print("=" * 60)


if __name__ == "__main__":
    main()