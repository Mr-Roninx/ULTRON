# ULTRON-SWU-1.5 Gateway Externalities

## 1. Shared Infrastructure Congestion
Payment gateways are finite, shared resources. Traffic switched by ULTRON into a secondary gateway:
$$\text{Overload} = \frac{\text{Current Load} - \text{Capacity}}{\text{Capacity}}$$
$$\text{Degraded Auth Rate} = \text{Base Auth Rate} - (0.22 \times \text{Overload})$$

Overloading Gateway B imposes latency delays and payment failure spillover on all other merchants on that rail.
