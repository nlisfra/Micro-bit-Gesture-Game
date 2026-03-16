import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score, learning_curve
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                           f1_score, classification_report, confusion_matrix)
import warnings
warnings.filterwarnings('ignore')


class KNNGestureTrainer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_map = None
        self.reverse_label_map = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.best_k = None
        self.training_history = {}
        
    def load_data(self, data_path="preprocessed_data.npz", scaler_path="scaler.pkl"):
        print("\n" + "="*50)
        print("LOADING DATA")
        print("="*50)
        
        try:
            data = np.load(data_path, allow_pickle=True)
            self.X_train = data["X_train"]
            self.X_test = data["X_test"]
            self.y_train = data["y_train"]
            self.y_test = data["y_test"]
            self.label_map = data["label_map"].item()
            self.reverse_label_map = {v: k for k, v in self.label_map.items()}
            
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            
            print(f"✓ Data loaded: Train={len(self.X_train)}, Test={len(self.X_test)}")
            print(f"✓ Features: {self.X_train.shape[1]} per sample")
            print(f"✓ Classes: {len(self.label_map)} {list(self.label_map.keys())}")
            
            if self.X_train.shape[1] != 15:
                print(f"⚠️  Warning: Jumlah fitur={self.X_train.shape[1]}, harusnya 15")
            
        except FileNotFoundError as e:
            print(f"✗ Error: {e}")
            print("  Jalankan preprocessing_data.py dulu")
            raise
    
    def find_best_k(self):
        print("\n" + "="*50)
        print("MENCARI NILAI K TERBAIK")
        print("="*50)
        print("Metric: Euclidean | Weight: Distance")
        
        k_values = list(range(1, 16, 2))
        print(f"\nNilai K yang diuji: {k_values}")
        print("-"*40)
        print("K     Akurasi CV")
        print("-"*40)
        
        mean_scores = []
        
        for k in k_values:
            knn = KNeighborsClassifier(
                n_neighbors=k,
                weights='distance',
                metric='euclidean'
            )
            
            cv_scores = cross_val_score(knn, self.X_train, self.y_train, cv=5)
            mean_acc = np.mean(cv_scores)
            mean_scores.append(mean_acc)
            
            print(f"{k:<4}  {mean_acc*100:>6.2f}%")
        
        best_idx = np.argmax(mean_scores)
        self.best_k = k_values[best_idx]
        best_acc = mean_scores[best_idx]
        
        print("-"*40)
        print(f"✓ K terbaik: {self.best_k} (Akurasi: {best_acc*100:.2f}%)")
        
        # Override K=1
        if self.best_k == 1:
            print("\n⚠️  K=1 terlalu sensitif, menggunakan K=3")
            self.best_k = 3
        
        self.model = KNeighborsClassifier(
            n_neighbors=self.best_k,
            weights='distance',
            metric='euclidean'
        )
        
        self._plot_k_tuning(k_values, mean_scores)
        
    def _plot_k_tuning(self, k_values, mean_scores):
        """Plot hasil tuning K"""
        scores_percent = [s*100 for s in mean_scores]
        
        plt.figure(figsize=(10, 5))
        
        plt.plot(k_values, scores_percent, 'bo-', linewidth=2, markersize=8)
        plt.scatter([self.best_k], [scores_percent[k_values.index(self.best_k)]], 
                   color='red', s=200, zorder=5, label=f'K={self.best_k}')
        
        plt.xlabel('Nilai K')
        plt.ylabel('Akurasi CV (%)')
        plt.title('Optimasi Nilai K')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('tuning_k.png', dpi=300)
        plt.close()
        print("✓ Plot tuning_k.png saved")
    
    def train(self):
        """Training model"""
        print("\n" + "="*50)
        print("TRAINING MODEL")
        print("="*50)
        print(f"K={self.best_k} | Weight=distance | Metric=euclidean")
        
        self.model.fit(self.X_train, self.y_train)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, self.X_train, self.y_train, cv=5)
        
        print(f"\n✓ Training selesai")
        print(f"✓ CV Score: {np.mean(cv_scores)*100:.2f}% (±{np.std(cv_scores)*100:.2f}%)")
        
        self.training_history['cv_mean'] = np.mean(cv_scores)
    
    def evaluate(self):
        """Evaluasi model"""
        print("\n" + "="*50)
        print("EVALUASI MODEL")
        print("="*50)
        
        y_pred = self.model.predict(self.X_test)
        
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, average='weighted')
        recall = recall_score(self.y_test, y_pred, average='weighted')
        f1 = f1_score(self.y_test, y_pred, average='weighted')
        
        print(f"\nAccuracy : {accuracy*100:.2f}%")
        print(f"Precision: {precision*100:.2f}%")
        print(f"Recall   : {recall*100:.2f}%")
        print(f"F1-Score : {f1*100:.2f}%")
        
        target_names = [self.reverse_label_map[i] for i in sorted(self.reverse_label_map)]
        print("\nClassification Report:")
        print(classification_report(self.y_test, y_pred, target_names=target_names, zero_division=0))
        
        self.training_history['test_accuracy'] = accuracy
        self.training_history['test_precision'] = precision
        self.training_history['test_recall'] = recall
        self.training_history['test_f1'] = f1
        
        self._plot_confusion_matrix(y_pred, target_names)
        self._plot_metrics(accuracy, precision, recall, f1)
        
    def _plot_confusion_matrix(self, y_pred, target_names):
        cm = confusion_matrix(self.y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=target_names, yticklabels=target_names)
        
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        
        plt.tight_layout()
        plt.savefig('confusion_matrix.png', dpi=300)
        plt.close()
        print("✓ confusion_matrix.png saved")
    
    def _plot_metrics(self, acc, prec, rec, f1):
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        values = [acc*100, prec*100, rec*100, f1*100]
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
        
        plt.figure(figsize=(8, 5))
        bars = plt.bar(metrics, values, color=colors)
        
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{val:.2f}%', ha='center', va='bottom')
        
        plt.ylabel('Percentage (%)')
        plt.title('Model Performance')
        plt.ylim(0, 110)
        plt.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('metrics.png', dpi=300)
        plt.close()
        print("✓ metrics.png saved")
    
    def plot_learning_curve(self):
        print("\n" + "="*50)
        print("LEARNING CURVE")
        print("="*50)
        
        train_sizes, train_scores, test_scores = learning_curve(
            self.model, self.X_train, self.y_train,
            train_sizes=np.linspace(0.1, 1.0, 10),
            cv=5, scoring='accuracy'
        )
        
        train_mean = np.mean(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        
        plt.figure(figsize=(8, 5))
        plt.plot(train_sizes, train_mean, 'o-', label='Training', color='blue')
        plt.plot(train_sizes, test_mean, 'o-', label='Validation', color='orange')
        
        plt.xlabel('Training Examples')
        plt.ylabel('Accuracy')
        plt.title('Learning Curve')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('learning_curve.png', dpi=300)
        plt.close()
        print("✓ learning_curve.png saved")
    
    def save_model(self):
        print("\n" + "="*50)
        print("MENYIMPAN MODEL FINAL")
        print("="*50)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_map': self.label_map,
            'reverse_label_map': self.reverse_label_map,
            'best_k': self.best_k,
            'metric': 'euclidean',
            'weight': 'distance',
            'n_features': 15,
            'training_history': self.training_history,
            'X_train_shape': self.X_train.shape,
            'X_test_shape': self.X_test.shape,
            'classes': list(self.label_map.keys())
        }
        
        with open('knn_gesture_model.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ knn_gesture_model.pkl")
        print(f"\nModel Info:")
        print(f"  K={self.best_k} | Euclidean | Distance Weight")
        print(f"  Train: {self.X_train.shape[0]} samples")
        print(f"  Test : {self.X_test.shape[0]} samples")
        print(f"  Features: {self.X_train.shape[1]}")
        print(f"  Classes: {list(self.label_map.keys())}")
        print(f"  Test Accuracy: {self.training_history['test_accuracy']*100:.2f}%")
    
    def print_summary(self):
        """Ringkasan hasil"""
        print("\n" + "="*50)
        print("RINGKASAN HASIL TRAINING")
        print("="*50)
        
        print(f"\nDataset:")
        print(f"  - Training : {self.X_train.shape[0]} samples")
        print(f"  - Testing  : {self.X_test.shape[0]} samples")
        print(f"  - Features : {self.X_train.shape[1]}")
        print(f"  - Classes  : {len(self.label_map)} {list(self.label_map.keys())}")
        
        print(f"\nModel Parameter:")
        print(f"  - K         : {self.best_k}")
        print(f"  - Weight    : distance")
        print(f"  - Metric    : euclidean")
        
        print(f"\nPerformance:")
        print(f"  - CV Accuracy : {self.training_history['cv_mean']*100:.2f}%")
        print(f"  - Test Accuracy: {self.training_history['test_accuracy']*100:.2f}%")
        print(f"  - Test Precision: {self.training_history['test_precision']*100:.2f}%")
        print(f"  - Test Recall   : {self.training_history['test_recall']*100:.2f}%")
        print(f"  - Test F1-Score : {self.training_history['test_f1']*100:.2f}%")


def main():
    print("\n" + "="*50)
    print("TRAINING MODEL KNN")
    print("="*50)
    
    trainer = KNNGestureTrainer()
    
    try:
        trainer.load_data()
        trainer.find_best_k()
        trainer.train()
        trainer.evaluate()
        trainer.plot_learning_curve()
        trainer.save_model()
        trainer.print_summary()
        
        print("\n" + "="*50)
        print("TRAINING SELESAI")
        print("="*50)
        print("\nOutput files:")
        print("  - tuning_k.png")
        print("  - confusion_matrix.png")
        print("  - metrics.png")
        print("  - learning_curve.png")
        print("  - knn_gesture_model.pkl")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()