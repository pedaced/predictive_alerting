# Predictive Alerting for Cloud Telemetry

## 🚀 Introduction
In high-availability cloud environments, traditional monitoring relies on static thresholds (e.g., "Alert if CPU > 90%"), which are inherently reactive. This project implements a **Predictive Alerting** prototype that identifies behavioral "signatures" of failure before they occur, providing the lead time necessary for proactive mitigation.

## 📝 Problem Formulation
We convert a raw time-series telemetry stream into a **Supervised Binary Classification** problem using a sliding-window approach.

* **Window ($W=30$):** We utilize 30 minutes of historical data to provide enough context.
* **Horizon ($H=15$):** We predict the probability of an incident occurring within the next 15 minutes.
* **Labels:** 1 (Positive) for imminent incidents; 0 (Negative) for normal operation.

## 🤖 Model Selection: Random Forest
The **Random Forest Classifier** was selected for its balance of performance and explainability, particularly its robustness to heavy-tailed noise.

## 🧬 Synthetic Data Generation
The model is validated against known "Ground Truth" failure modes: Memory Leaks, Traffic Surges, and Stuck Threads.

![CPU Usage and Incident Windows](https://raw.githubusercontent.com/pedaced/predictive_alerting/main/images/cpu_usage_incidents.png)

## 🛠️ Feature Engineering: First Principles
Features were designed to capture the "physics" of a failing server:
* **`cpu_rolling_mean`**: Sustained high load.
* **`cpu_rolling_std`**: Jitter and instability.
* **`cpu_trend`**: Gradual resource exhaustion.
* **`cpu_rolling_max`**: Aggressive saturation.

## 📈 Results and Analysis
The system was evaluated on a **chronological held-out period** (the final 25% of the data).

![Precision-Recall Curve](https://raw.githubusercontent.com/pedaced/predictive_alerting/main/images/precision_recall_curve.png)

### Interpretation
The model achieved an **Average Precision (AP) of 0.79**. The resulting Precision-Recall curve shows the model's capacity to identify incident signatures across varying confidence levels. At standard operating points, the model effectively separates anomalous "turbulent" signals from baseline seasonal noise.

## ⚠️ Limitations and Future Direction
To transition this prototype into a production-ready system:
* **Threshold Optimization:** Future work will focus on lowering the decision threshold to **0.18**. Initial testing suggests this can achieve a precision of **0.96** for a **0.8 recall**, optimizing the system for high-stakes mission-critical alerting.
* **Multivariate Input:** Incorporating Memory, Disk I/O, and Network latency to catch non-CPU-bound failures.
* **Online Learning:** Implementing a feedback loop to prevent model drift as system baselines evolve.