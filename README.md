# Predictive Alerting for Cloud Telemetry

## 🚀 Introduction
In high-availability cloud environments, traditional monitoring relies on static thresholds (e.g., "Alert if CPU > 90%"), which are inherently reactive. This project implements a **Predictive Alerting** prototype that identifies behavioral "signatures" of failure before they occur, providing the lead time necessary for proactive mitigation.

## 📝 Problem Formulation
We convert a raw time-series telemetry stream into a **Supervised Binary Classification** problem using a sliding-window approach.

* **Window ($W=30$):** We utilize 30 minutes of historical data to provide enough context.
* **Horizon ($H=15$):** We predict the probability of an incident occurring within the next 15 minutes. 
* **Labels:** 1 (Positive) indicates the 15-minute "pre-terminal" window before a failure; 0 (Negative) indicates normal operation.

## 📊 Incident Definition & Synthetic Data
To validate the model, we simulate a 2-day production cycle and model three "Dying Server" signatures:
1.  **Memory Leak (Trend):** Linear CPU increase caused by garbage collection overhead.
2.  **Traffic Surge (Spike):** Exponential growth outpacing normal seasonal traffic.
3.  **Stuck Thread (Jitter):** High-variance "turbulent" regimes signaling thread contention.

## 🛠️ Feature Engineering: First Principles
![CPU Usage and Incident Windows](https://raw.githubusercontent.com/pedaced/predictive_alerting/main/images/cpu_usage_incidents.png)

Features were designed by asking: *"What does a server look like when it's dying?"*

| Feature | Logic | Detects |
| :--- | :--- | :--- |
| **`cpu_rolling_mean`** | "It's working harder than usual" | Sustained high load |
| **`cpu_rolling_std`** | "It's struggling and becoming erratic" | Jitter/Stuck threads |
| **`cpu_trend`** | "It's gradually losing resources" | Memory leaks |
| **`cpu_rolling_max`** | "It's hitting its ceiling" | Traffic surges |

## 📈 Results and Analysis
Evaluated on a **chronological held-out period** (the final 25% of the data). 

![Precision-Recall Curve](https://raw.githubusercontent.com/pedaced/predictive_alerting/main/images/precision_recall_curve.png)

### Interpretation & Feature Importance
The model achieved an **Average Precision (AP) of 0.79**. 

![Feature Importance](https://raw.githubusercontent.com/pedaced/predictive_alerting/main/images/feature_importance.png)

**The "Explainability" Factor:** The Random Forest's ability to rank feature importance is a key operational benefit. It allows the system to provide context alongside an alert (e.g., "High probability of incident due to rising `cpu_trend`"). This transparency helps SRE teams trust the model and distinguish between normal peak load and actual system degradation.

## ⚠️ Limitations and Future Direction
* **Threshold Optimization:** Lowering the threshold to **0.18** can potentially achieve **0.96 precision for 0.8 recall**, optimizing for mission-critical reliability.
* **Multivariate Input:** Incorporating Memory and Disk I/O to catch non-CPU-bound failures.
* **Online Learning:** Implementing a feedback loop to prevent model drift as system baselines evolve.