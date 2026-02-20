# Predictive Alerting for Cloud Telemetry

## 🚀 Introduction
In high-availability cloud environments, traditional monitoring relies on static thresholds (e.g., "Alert if CPU > 90%"), which are inherently reactive. By the time a threshold is breached, the service has likely already degraded. This project implements a **Predictive Alerting** prototype that identifies behavioral "signatures" of failure before they occur, providing the lead time necessary for proactive mitigation.

## 📝 Problem Formulation
We convert a raw time-series telemetry stream into a **Supervised Binary Classification** problem using a sliding-window approach.

* **Window ($W=30$):** We utilize 30 minutes of historical data to provide the model with enough context to calculate momentum and stability.
* **Horizon ($H=15$):** We predict the probability of an incident occurring within the next 15 minutes. 
    * *Justification:* $H < 15$ provides insufficient lead time for intervention; $H > 30$ becomes too vague for operational clarity.
* **Labels:** * **1 (Positive):** An incident is imminent within the $H$ horizon.
    * **0 (Negative):** The system is operating within normal seasonal parameters.

The core philosophy is to keep the system simple, justifiable, and iterative: **Target → Data → Features.**

## 🤖 Model Selection: Random Forest
The **Random Forest Classifier** was selected for its balance of performance and explainability:
* **Non-Linearity:** It captures complex patterns (e.g., seasonal CPU fluctuations) that linear models miss.
* **Explainability:** Through **Feature Importance**, it moves beyond "black box" logic, allowing engineers to see if an alert was triggered by a specific trend or a spike.
* **Robustness:** It is naturally resistant to the heavy-tailed noise common in cloud telemetry.

## 🧬 Synthetic Data Generation: The "Dying Server" Models
The model is validated against synthetic telemetry mimicking a 2-day production cycle. To ensure the system is operationally relevant, we modeled three specific failure signatures based on real-world system degradation:

1.  **Memory Leak (Trend):** A slow, linear increase in usage. In production, as memory exhausts, increased garbage collection overhead creates a consistent upward CPU slope.
2.  **Traffic Surge (Spike):** Exponential growth in demand, simulating a sudden surge in requests where the rate of change outpaces normal traffic growth.
3.  **Stuck Thread (Jitter):** High-variance, erratic fluctuations (turbulent regime). Rapid jumping between utilization levels is a signature of thread contention and system instability.



## 🛠️ Feature Engineering: First Principles
Instead of arbitrary mathematical transformations, features were designed by asking: *"What does a server look like when it's dying?"*

| Feature | Logic | Detects |
| :--- | :--- | :--- |
| **`cpu_rolling_mean`** | "It's working harder than usual" | Sustained high load |
| **`cpu_rolling_std`** | "It's struggling and becoming erratic" | Jitter/Stuck threads |
| **`cpu_trend`** | "It's gradually losing resources" | Memory leaks |
| **`cpu_rolling_max`** | "It's hitting its ceiling" | Traffic surges |

## 📈 Results and Analysis
The system was evaluated on a **chronological held-out period** (the final 25% of the data) to simulate real-world inference. 

![Precision-Recall Curve](https://raw.githubusercontent.com/pedaced/predictive_alerting/main/images/precision_recall_curve.png)

### Interpretation
The model achieved an **Average Precision (AP) of 0.79**. The results indicate that the model effectively distinguishes pre-failure signatures from normal seasonal noise. At the default 0.5 threshold, the model successfully captures the majority of injected failure signatures (Leaks, Surges, and Jitter) within the 15-minute horizon.

## ⚠️ Limitations and Future Direction
To transition this prototype into a production-ready system:
* **Threshold Optimization:** Initial testing suggests that lowering the decision threshold to **0.18** can achieve a precision of **0.96** for **0.8 recall**, further reducing false alarms while maintaining high coverage.
* **Multivariate Input:** Incorporating Memory, Disk I/O, and Network latency to catch non-CPU-bound failures.
* **Online Learning:** Implementing a feedback loop to retrain the model as system baselines evolve.