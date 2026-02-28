import pandas as pd
import numpy as np
import glob
import os
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def load_all_data(self, data_folder='./'):
        csv_files = glob.glob(os.path.join(data_folder, 'data_*.csv'))
        
        if not csv_files:
            raise FileNotFoundError("Tidak ada file data_*.csv ditemukan!")
        
        print(f"📂 Ditemukan {len(csv_files)} file data\n")
        
        df_list = []
        for file in csv_files:
            print(f"Processing: {os.path.basename(file)}")
            
            df = None
            
            # Try 1: Tab separator with skiprows
            try:
                df = pd.read_csv(file, sep='\t', skiprows=1, on_bad_lines='skip')
                if len(df.columns) >= 3:
                    print(f"      ✅ Read with tab separator")
            except:
                pass
            
            # Try 2: Semicolon separator
            if df is None or len(df.columns) < 3:
                try:
                    df = pd.read_csv(file, sep=';', on_bad_lines='skip')
                    if len(df.columns) >= 3:
                        print(f"      ✅ Read with semicolon separator")
                except:
                    pass
            
            # Try 3: Comma separator
            if df is None or len(df.columns) < 3:
                try:
                    df = pd.read_csv(file, sep=',', on_bad_lines='skip')
                    if len(df.columns) >= 3:
                        print(f"      ✅ Read with comma separator")
                except:
                    pass
            
            if df is None or len(df.columns) < 3:
                print(f"      ❌ Could not read file properly, skipping")
                continue
            
            if 'data.0' in df.columns:
                df = df.rename(columns={
                    'data.0': 'ax',
                    'data.1': 'ay', 
                    'data.2': 'az'
                })
            else:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if len(numeric_cols) >= 3:
                    df = df[numeric_cols[:3]]
                    df.columns = ['ax', 'ay', 'az']
                elif len(df.columns) >= 3:
                    df = df.iloc[:, :3]
                    df.columns = ['ax', 'ay', 'az']
                else:
                    print(f"      ❌ Not enough columns, skipping")
                    continue
            
            if 'ax' not in df.columns or 'ay' not in df.columns or 'az' not in df.columns:
                print(f"      ❌ Missing ax/ay/az after processing, skipping")
                continue
            
            filename = os.path.basename(file).lower()
            if 'tilt_left' in filename or '_left' in filename or 'left' in filename:
                label = 'tilt_left'
            elif 'tilt_right' in filename or '_right' in filename or 'right' in filename:
                label = 'tilt_right'
            elif 'up' in filename or 'atas' in filename:
                label = 'up'
            else:
                print(f"    Unknown gesture in filename: {filename}")
                continue
            
            df['label'] = label
            
            df = df[['ax', 'ay', 'az', 'label']].dropna()
            
            df['ax'] = pd.to_numeric(df['ax'], errors='coerce')
            df['ay'] = pd.to_numeric(df['ay'], errors='coerce')
            df['az'] = pd.to_numeric(df['az'], errors='coerce')
            df = df.dropna()
            
            print(f"Final: {len(df)} rows, label='{label}'\n")
            
            df_list.append(df)
        
        if not df_list:
            raise ValueError("No valid data loaded from any CSV file!")
        
        combined_df = pd.concat(df_list, ignore_index=True)
        print(f" Total data: {len(combined_df)} rows")
        print(f" Labels: {combined_df['label'].value_counts().to_dict()}\n")
        
        return combined_df
    
    def clean_data(self, df):
        print("\n Cleaning data...")
        
        before = len(df)
        df = df.dropna()
        print(f"   - Missing values removed: {before - len(df)} rows")
        
        before = len(df)
        df = df.drop_duplicates(subset=['ax', 'ay', 'az'])
        print(f"   - Duplicates removed: {before - len(df)} rows")
        
        numeric_cols = ['ax', 'ay', 'az']
        before = len(df)
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        print(f"   - Outliers removed: {before - len(df)} rows")
        print(f"   Clean data: {len(df)} rows\n")
        
        return df
    
    def visualize_data(self, df):
        print("Membuat visualisasi data...")
        
        #Scatter plot 2D dan box plot
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        df['label'].value_counts().plot(kind='bar', ax=axes[0, 0], color='skyblue')
        axes[0, 0].set_title('Distribusi Data per Gesture')
        axes[0, 0].set_ylabel('Jumlah Sampel')
        axes[0, 0].grid(True, alpha=0.3)
        
        for label in df['label'].unique():
            subset = df[df['label'] == label]
            axes[0, 1].scatter(subset['ax'], subset['ay'], label=label, alpha=0.5)
        axes[0, 1].set_xlabel('Acceleration X')
        axes[0, 1].set_ylabel('Acceleration Y')
        axes[0, 1].set_title('Scatter Plot: AX vs AY')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        for label in df['label'].unique():
            subset = df[df['label'] == label]
            axes[1, 0].scatter(subset['ax'], subset['az'], label=label, alpha=0.5)
        axes[1, 0].set_xlabel('Acceleration X')
        axes[1, 0].set_ylabel('Acceleration Z')
        axes[1, 0].set_title('Scatter Plot: AX vs AZ')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        df_melted = df.melt(id_vars='label', value_vars=['ax', 'ay', 'az'], 
                           var_name='axis', value_name='value')
        df_melted.boxplot(column='value', by=['label', 'axis'], ax=axes[1, 1])
        axes[1, 1].set_title('Box Plot Distribusi Nilai')
        axes[1, 1].set_xlabel('Gesture & Axis')
        axes[1, 1].set_ylabel('Acceleration Value')
        
        plt.tight_layout()
        plt.savefig('data_visualization.png', dpi=300)
        print("Visualisasi disimpan: data_visualization.png")
        plt.close()
        
        # Scatter plot 3D
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        colors = {'tilt_left': 'red', 'up': 'green', 'tilt_right': 'blue'}
        
        for label in df['label'].unique():
            subset = df[df['label'] == label]
            ax.scatter(subset['ax'], subset['ay'], subset['az'], 
                      c=colors.get(label, 'gray'), 
                      label=label, 
                      alpha=0.6, 
                      s=20)
        
        ax.set_xlabel('Acceleration X', fontsize=10)
        ax.set_ylabel('Acceleration Y', fontsize=10)
        ax.set_zlabel('Acceleration Z', fontsize=10)
        ax.set_title('Distribusi Scatter Plot Data Akselerometer 3D', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('data_visualization_3d.png', dpi=300)
        print("Visualisasi 3D disimpan: data_visualization_3d.png\n")
        plt.close()
    
    def prepare_features(self, df):
        print("Preparing features...")
        
        X = df[['ax', 'ay', 'az']].values
        y = df['label'].values
        
        label_map = {'tilt_left': 0, 'up': 1, 'tilt_right': 2}
        y_encoded = np.array([label_map[label] for label in y])
        
        print(f"   - Features shape: {X.shape}")
        print(f"   - Labels shape: {y_encoded.shape}")
        print(f"   - Label mapping: {label_map}\n")
        
        return X, y_encoded, label_map
    
    def normalize_features(self, X_train, X_test):
        print("🔄 Normalizing features...")
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"   ✅ Training set scaled: {X_train_scaled.shape}")
        print(f"   ✅ Test set scaled: {X_test_scaled.shape}\n")
        
        return X_train_scaled, X_test_scaled
    
    def process_pipeline(self, data_folder='./', test_size=0.2, visualize=True):
        print("\n" + "="*50)
        print(" PREPROCESSING DATA ")
        print("="*50 + "\n")
        
        df = self.load_all_data(data_folder)
        
        df_clean = self.clean_data(df)
        
        if visualize:
            self.visualize_data(df_clean)
        
        X, y, label_map = self.prepare_features(df_clean)
        
        # Split data
        print("Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        print(f"   - Train set: {len(X_train)} samples")
        print(f"   - Test set: {len(X_test)} samples\n")
        
        X_train_scaled, X_test_scaled = self.normalize_features(X_train, X_test)
        
        print("Menyimpan data hasil preprocessing...")
        np.savez('preprocessed_data.npz',
                X_train=X_train_scaled,
                X_test=X_test_scaled,
                y_train=y_train,
                y_test=y_test,
                label_map=label_map)
        print("Saved: preprocessed_data.npz")
        
        with open('scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        print("Saved: scaler.pkl \n")
        
        print("="*50)
        print("PREPROCESSING SELESAI!")
        print("="*50)
        
        return X_train_scaled, X_test_scaled, y_train, y_test, label_map

if __name__ == "__main__":
    processor = DataPreprocessor()
    X_train, X_test, y_train, y_test, label_map = processor.process_pipeline(
        data_folder='./',
        test_size=0.2,
        visualize=True
    )
    
    print("\n Summary:")
    print(f"   Training samples: {len(X_train)}")
    print(f"   Testing samples: {len(X_test)}")
    print(f"   Features: {X_train.shape[1]}")
    print(f"   Classes: {len(label_map)}")