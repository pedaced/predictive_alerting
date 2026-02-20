import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, PrecisionRecallDisplay

# -----------------------------
# 1. Generate Synthetic Data
# -----------------------------
def generate_data(days=2, interval_min=1):
    periods = (24*60//interval_min) * days
    time_index = pd.date_range("2024-01-01", periods=periods, freq=f"{interval_min}min")
    
    # Base CPU usage: seasonality + noise
    hour = time_index.hour + time_index.minute/60
    seasonality = 15 * np.sin(2 * np.pi * (hour-6)/24) + 40
    noise = np.random.normal(0, 1.5, size=periods)
    cpu_usage = np.array(seasonality + noise, dtype=float)
    
    # -----------------------------
    # Inject Incidents
    # -----------------------------
    actual_incident = np.zeros(periods)
    
    for d in range(days):
        offset = d*1440  # minutes per day
        
        # 1. Memory Leak (Trend)
        leak_s = offset + 240
        for i in range(60): cpu_usage[leak_s+i] += i*0.7
        actual_incident[leak_s+50:leak_s+60] = 1
        
        # 2. Traffic Surge (Spike)
        surge_s = offset + 720
        for i in range(30): cpu_usage[surge_s+i] += (i**2)*0.06
        actual_incident[surge_s+25:surge_s+30] = 1
        
        # 3. Stuck Thread (Jitter)
        jitter_s = offset + 1200
        for i in range(40): cpu_usage[jitter_s+i] += np.random.normal(0,12)
        actual_incident[jitter_s+30:jitter_s+40] = 1
        
    cpu_usage = np.clip(cpu_usage, 0, 100)
    df = pd.DataFrame({'cpu_usage': cpu_usage, 'is_incident': actual_incident}, index=time_index)
    return df

# -----------------------------
# 2. Feature Engineering
# -----------------------------
def engineer_features(df, W=30, H=15):
    # Target: incident occurs within next H minutes
    df['target'] = df['is_incident'].rolling(window=H).max().shift(-H).fillna(0)
    
    # Features over past W minutes
    df['cpu_rolling_mean'] = df['cpu_usage'].rolling(window=W).mean()
    df['cpu_rolling_std'] = df['cpu_usage'].rolling(window=W).std()
    df['cpu_rolling_max'] = df['cpu_usage'].rolling(window=W).max()
    df['cpu_trend'] = df['cpu_usage'] - df['cpu_usage'].shift(W)
    
    df = df.dropna()
    return df

# -----------------------------
# 3. Train Random Forest Model
# -----------------------------
def train_model(df, features):
    X = df[features]
    y = df['target']
    
    # Chronological split (75% train)
    split = int(len(df)*0.75)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    
    model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred))
    
    # Precision-Recall display
    plt.figure(figsize=(6,5))
    PrecisionRecallDisplay.from_estimator(model, X_test, y_test)
    plt.title("Precision-Recall Curve")
    plt.tight_layout()
    plt.savefig("images/precision_recall_curve.png", dpi=300)
    plt.show()
    
    return model

# -----------------------------
# 4. Beautiful Seaborn Visualizations
# -----------------------------
def plot_results(df, model, features):
    sns.set_style("whitegrid")
    sns.set_context("talk")
    
    # CPU Usage + Incident Windows
    plt.figure(figsize=(16,5))
    plt.plot(df.index, df['cpu_usage'], color='gray', alpha=0.5, label='CPU Usage (%)')
    plt.fill_between(df.index, 0, 100, where=df['target']==1, color='red', alpha=0.2, label='Incident Window (H)')
    plt.title("CPU Usage with Incident Prediction Windows")
    plt.xlabel("Time")
    plt.ylabel("CPU Usage (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("images/cpu_usage_incidents.png", dpi=300)
    plt.show()
    
    # Feature Importance
    importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=True)
    plt.figure(figsize=(10,5))
    sns.barplot(x=importances.values, y=importances.index, palette="coolwarm")
    plt.title("Random Forest Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig("images/feature_importance.png", dpi=300)
    plt.show()
    
    # Trend vs Volatility
    plt.figure(figsize=(16,5))
    sns.lineplot(x=df.index, y=df['cpu_trend'], label='Trend (W)', color='green', linewidth=2)
    sns.lineplot(x=df.index, y=df['cpu_rolling_std'], label='Volatility (W)', color='orange', linewidth=2)
    plt.title("Behavioral Signatures: Trend vs Volatility")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    plt.savefig("images/trend_volatility.png", dpi=300)
    plt.show()

# -----------------------------
# 5. Full Pipeline
# -----------------------------
def run_full_pipeline(days=2, W=30, H=15):
    print(f"Running pipeline with W={W}, H={H}, Days={days}")
    df = generate_data(days=days)
    df = engineer_features(df, W=W, H=H)
    
    features = ['cpu_rolling_mean','cpu_rolling_std','cpu_rolling_max','cpu_trend']
    model = train_model(df, features)
    
    plot_results(df, model, features)

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    run_full_pipeline(days=2, W=30, H=15)