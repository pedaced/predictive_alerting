# Predictive Alerting for Cloud Telemetry

## 🚀 Introduction
In high-availability cloud environments, traditional monitoring relies on static thresholds (e.g., "Alert if CPU > 90%"), which are inherently reactive. By the time a threshold is breached, the service has likely already degraded. This project implements a **Predictive Alerting** prototype that identifies behavioral "signatures" of failure before they occur, providing the lead time necessary for proactive mitigation.

## 📝 Problem Formulation
We convert a raw time-series telemetry stream into a **Supervised Binary Classification** problem using a sliding-window approach.

* **Window ($W=30$):** We utilize 30 minutes of historical data to provide the model with enough context to calculate momentum and stability.
* **Horizon ($H=15$):** We predict the probability of an incident occurring within the next 15 minutes.
    * *Justification:* $H < 15$ provides insufficient lead time for intervention; $H > 30$ becomes too vague for operational clarity.
* **Labels:**
    * **1 (Positive):** An incident is imminent within the $H$ horizon.
    * **0 (Negative):** The system is operating within normal seasonal parameters.

The core philosophy is to keep the system simple, justifiable, and iterative: **Target → Data → Features.**

## 🤖 Model Selection: Random Forest
The **Random Forest Classifier** was selected for its balance of performance and explainability:
* **Non-Linearity:** It captures complex patterns (e.g., different "normal" CPU levels at different times of the day) that linear models miss.
* **Explainability:** Through **Feature Importance**, it moves beyond "black box" logic, allowing engineers to see if an alert was triggered by a trend, a spike, or jitter.
* **Robustness:** It is naturally resistant to the heavy-tailed noise common in cloud telemetry.

## 🧬 Synthetic Data Generation
The model is validated against synthetic telemetry mimicking a 2-day production cycle. This allows us to test against known "Ground Truth" failure modes.

![CPU Usage and Incident Windows](https://raw.githubusercontent.com/pedaced/predictive_alerting/main/cpu_usage_incidents.png)

### Incident Modeling: "Dying Server" Signatures
We model three specific failure modes to ensure the system recognizes different "physics" of degradation:
1.  **Memory Leak (Trend):** Slow, linear increase in usage.
2.  **Traffic Surge (Spike):** Exponential growth in demand.
3.  **Stuck Thread (Jitter):** High-variance, erratic fluctuations (turbulent regime).

## 🛠️ Feature Engineering: First Principles
Features were designed based on the question: *"What does a server look like when it's dying?"*

| Feature | Logic | Detects |
| :--- | :--- | :--- |
| **`cpu_rolling_mean`** | "It's working harder than usual" | Sustained high load |
| **`cpu_rolling_std`** | "It's struggling and becoming erratic" | Jitter/Stuck threads |
| **`cpu_trend`** | "It's gradually losing resources" | Memory leaks |
| **`cpu_rolling_max`** | "It's hitting its ceiling" | Traffic surges |

## 📈 Results and Analysis
The system was evaluated on a **chronological held-out period** (the final 25% of the data) to simulate real-world inference.

![Precision-Recall Curve](https://raw.githubusercontent.com/pedaced/predictive_alerting/main/precision_recall_curve.png)

### Interpretation and Insights
* **Threshold Optimization:** By default, models use a 0.5 probability threshold. However, for mission-critical alerting, we prioritize **Recall** (coverage) over **Precision** (avoiding false alarms).
* **The 80/60 Balance:** We intentionally lowered the "bar of evidence" (decision threshold) to approximately **0.18**.
* **Outcome:** The model raises at least one alert before the start of an incident for **80% of incident intervals**, while keeping the precision at a reasonable level (~60%). This ensures that even subtle early-warning signs trigger an alert, prioritizing system reliability.



## ⚠️ Limitations and Future Direction
To transition this prototype into a production-ready system:
* **Multivariate Input:** Incorporating Memory, Disk I/O, and Network latency to catch failures that do not manifest in CPU usage.
* **Online Learning:** Implementing a feedback loop to retrain the model as the "normal" baseline evolves, preventing model drift.
* **Deployment:** The system should be served via a microservice consuming a live stream (e.g., Kafka/Prometheus), triggering PagerDuty notifications when the 0.18 probability threshold is breached.