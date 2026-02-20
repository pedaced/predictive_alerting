# Cloud Predictive Alerting System

This repository contains a prototype for a **Predictive Alerting System** designed to anticipate cloud service incidents. Using a **Sliding-Window Supervised Learning** approach, the system transforms raw CPU telemetry into actionable early-warning signals.

---

## 🚀 Core Philosophy
> **"Keep it simple and justifiable."**
> 
> We prioritize features that an engineer can understand and a model can explain. Our design follows a first-principles approach: **Target → Data → Features.**

---

## 🛠️ Problem Formulation
We treat incident detection as a **Supervised Binary Classification** problem.

* **Window ($W=30$):** We look at the past 30 minutes of data to capture patterns.
* **Horizon ($H=15$):** We predict if an incident will occur in the *next* 15 minutes. This provides sufficient lead time for an engineer to intervene.
* **Labels:** * `1`: An incident is imminent (within 15 mins).
    * `0`: Normal operation.



---

## 📊 Synthetic Data Generation
Real-world incidents are sparse. To train the model, we simulate three classic "Dying Server" signatures:

1.  **Memory Leak:** A gradual, consistent upward trend in CPU.
2.  **Traffic Surge:** An exponential acceleration in load (spikes).
3.  **Stuck Thread:** High jitter and erratic fluctuations (instability).

---

## 🧠 Feature Engineering
Instead of complex "black-box" math, we use **Behavioral Signatures**:

| Feature | SRE Justification | Logic |
| :--- | :--- | :--- |
| **`cpu_rolling_mean`** | "Is it working harder than usual?" | Captures baseline shifts. |
| **`cpu_rolling_std`** | "Is it becoming erratic?" | Captures **Jitter** (Stuck threads). |
| **`cpu_trend`** | "Is it gradually losing resources?" | Captures **Leaks** (Gradual growth). |
| **`cpu_rolling_max`** | "Is it hitting its ceiling?" | Captures **Spikes** (Traffic surges). |



---

## 🤖 Model Selection
We selected a **Random Forest Classifier** for this task.
* **Explainability:** Unlike Deep Learning, Random Forest tells us *why* an alert was triggered (e.g., "The Trend was the deciding factor").
* **Non-Linearity:** It effectively handles specific thresholds and seasonal peaks.
* **Class Imbalance:** By using `class_weight='balanced'`, we ensure the model learns from rare incident events.

---

## 📈 Results & Analysis
The model is evaluated using a **chronological split** to prevent data leakage.

* **Recall:** Targeted at **~80%**. In mission-critical systems, missing an incident is more expensive than a false alarm.
* **Precision-Recall Curve:** Used instead of Accuracy because incidents are rare (class imbalance).
* **Insight:** When `cpu_trend` is the top feature, the model is successfully catching Leaks. When `cpu_rolling_std` spikes, it is detecting Jitter.



---

## ⚠️ Limitations
* **Overfitting:** With limited historical incidents, the model may memorize specific timestamps.
* **Lead Time Variance:** While $H=15$ is the goal, some rapid spikes may only be detectable 5 minutes in advance.
* **Seasonality:** High natural traffic (e.g., mid-day peaks) can occasionally be mistaken for surges.

---

## 💻 Implementation
To run the end-to-end pipeline:

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Run the full pipeline including data generation, 
# feature engineering, and model training.
if __name__ == "__main__":
    run_full_pipeline(days=2, W=30, H=15)