# Predictive Alerting for Cloud Telemetry

## 🚀 Introduction
This project implements a predictive alerting system that identifies server failure signatures before they occur. By analyzing CPU telemetry for shifts into "turbulent regimes," the model provides a 15-minute lead time ($H=15$) to prevent outages, moving beyond the limitations of reactive, static thresholds.

---

## 🛠️ Modeling Choices
* **Algorithm:** **Random Forest Classifier** was selected for its ability to capture non-linear relationships and its native resistance to the "heavy-tailed" noise common in cloud metrics.
* **Feature Engineering:** Instead of raw values, the model relies on **Statistical Signatures**:
    * `cpu_rolling_std`: Detects "jitter" or instability (Stuck Threads).
    * `cpu_trend`: Captures directional momentum (Memory Leaks).
    * `cpu_rolling_max`: Identifies aggressive resource saturation (Traffic Surges).
* **Logic:** The model is trained to recognize the *behavioral transition* from a stable seasonal baseline to an anomalous state.

---

## 🧪 Evaluation Setup
To ensure the system is production-ready, the following validation framework was used:
* **Chronological Split:** The dataset (2 days of telemetry) was split 75/25 without shuffling. This prevents "data leakage" and ensures the model is tested on its ability to predict a future it has never seen.
* **The Target:** An "Incident" is defined as a failure window occurring within the next 15 minutes ($H=15$).
* **Metric Selection:** We prioritize **Recall** and **Average Precision (AP)** over Accuracy, as the dataset is highly imbalanced (incidents represent <10% of total uptime).

---

## 📈 Results & Threshold Optimization
The model achieved the **80% Recall target** by optimizing the decision threshold using the Precision-Recall curve.

| Metric | Result | Interpretation |
| :--- | :--- | :--- |
| **Recall (Class 1)** | **0.80** | Successfully caught 80% of all injected failure windows. |
| **Precision (Class 1)** | **~0.60** | For every 10 alerts, 6 are true positives. |
| **Optimal Threshold** | **~0.18** | The system alerts when the incident probability exceeds 18%. |

### Analysis of the Precision-Recall Trade-off

While the default model threshold (0.5) yielded high precision but low recall (~0.40), we intentionally shifted the threshold to **0.18**. In a mission-critical alerting system, a **60% Precision / 80% Recall** balance is optimal: it provides high coverage for outages while maintaining a manageable signal-to-noise ratio for SRE teams.

---

## ⚠️ Limitations & Real-World Adaptation
* **Seasonality Shifts:** The current model assumes a consistent daily cycle. A production version would require a "Seasonality Decomposition" layer (e.g., Fourier Transforms) to handle holidays or daylight savings.
* **Cold Start:** As a supervised model, it requires labeled historical failures. In a new environment, an unsupervised "Anomaly Detection" layer would be needed initially to gather training labels.
* **Adaptation:** To deploy this in a real system, the model would be served via a microservice consuming a live Kafka/Prometheus stream, triggering PagerDuty alerts when the probability threshold is breached.