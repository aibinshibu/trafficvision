# TrafficVision AI — Integration Guide (`integration.md`)

Welcome! This guide explains exactly how all the different pieces of the **TrafficVision AI** project were connected together. If you are a beginner wondering how 5 different microservices and a frontend communicate without breaking, you are in the right place!

---

## 🏗️ 1. The Big Picture: Microservices Architecture

Instead of building one massive application (a "monolith"), we built **Microservices**. This means different team members (interns) built separate, specialized applications that run on their own ports.

Here is the breakdown of the services:
- **Anmol's Data Service (Port 8000)**: Handles live traffic sensor data and analytics.
- **Saksham's AI Engine (Port 8001)**: Runs machine learning models to predict congestion and delays.
- **Route Analysis Service (Port 8002)**: Calculates the fastest driving routes.
- **Alert Service (Port 8003)**: Manages notifications and warnings for commuters and operators.
- **Hariom's Frontend (Port 3000)**: The beautiful web dashboard you see in your browser.

But wait... if there are so many backend services, how does the frontend know which port to talk to? 
**The answer is the API Gateway!**

---

## 🚪 2. The API Gateway (Port 8080)

We created a central **API Gateway** inside the `aibin-backend` folder. The Gateway runs on **Port 8080**.

### How it works:
1. The Frontend (`hariom-frontend`) **only** talks to the Gateway (`:8080`). It doesn't need to know that Ports 8000, 8001, 8002, or 8003 even exist!
2. When the Gateway receives a request (e.g., "Give me live traffic"), it looks at the URL.
3. Using **Proxy Routers** (like `traffic_proxy.py` or `prediction_proxy.py`), the Gateway secretly forwards the request to the correct microservice in the background.
4. The microservice replies to the Gateway, and the Gateway passes the reply back to the Frontend.

### Example Flow:
`Frontend (:3000)` ➡️ `GET /api/v1/predict/congestion` ➡️ `Gateway (:8080)` ➡️ `AI Engine (:8001)`

---

## 🔐 3. Security & Authentication (JWT & RBAC)

Since multiple services are running, we need a way to keep the data secure.

- **JWT Tokens:** When a user logs in via the Gateway (`/api/v1/auth/login`), they are given a secure "ticket" called a **JSON Web Token (JWT)**. The Frontend attaches this ticket to every subsequent request.
- **Role-Based Access Control (RBAC):** We created different user roles (`admin`, `operator`, `planner`, `commuter`). The Gateway inspects the user's token before forwarding their request. If a `commuter` tries to access a restricted `admin` dashboard (like active system alerts), the Gateway immediately blocks them with a `403 Forbidden` error!

---

## 🧩 4. How Each Repository Was Integrated

Here is a simple breakdown of the integration challenges we solved for each team member's repository:

### A. Anmol's Data Service (`anmol-data`)
- **Integration:** Proxied via `traffic_proxy.py` and `analytics_proxy.py`.
- **Challenge:** Anmol's code attempts to connect to a Redis caching server on Windows, which causes a 15-second timeout delay on the very first request. 
- **Solution:** We increased the Gateway's proxy timeout for Anmol's routes to `40.0` seconds so the Gateway wouldn't crash or return a `502 Bad Gateway` while waiting for his service to respond.

### B. Saksham's AI Engine (`saksham-aiml`)
- **Integration:** Proxied via `prediction_proxy.py` for congestion, delays, peak hours, and route ranking.
- **Challenge:** Saksham recently added new endpoints (`/anomalies` and `/recommendations`) which imported a library called `requests`. Because this library wasn't installed in the shared virtual environment, his entire service crashed, resulting in a `502 Bad Gateway`.
- **Solution:** We ran `pip install requests` in the virtual environment to satisfy the dependency, updated the Gateway to proxy the two new routes, and updated the Swagger documentation.

### C. Alert Service & Internal Triggers (`aibin-backend`)
- **Integration:** Proxied via `alert_proxy.py`.
- **Challenge:** The Alert Service needs to be triggered when traffic is too high (Anmol's repo) or an anomaly is detected (Saksham's repo). However, those features were not fully sending alerts yet.
- **Solution:** We created internal "poller scripts" (like `anomaly_poller.py` and `closure_delay_trigger.py`) in the `scripts/` folder. These scripts act as a "TEMP STOPGAP", constantly checking the other services and creating alerts manually until the true integrations are finalized. We also updated `dependencies.md` to track these blockages.

### D. Hariom's Frontend (`hariom-frontend`)
- **Integration:** We added **CORS Middleware** (Cross-Origin Resource Sharing) to the API Gateway (`main.py`).
- **Challenge:** By default, web browsers block a website on Port 3000 from fetching data from an API on Port 8080 for security reasons.
- **Solution:** We configured the Gateway to explicitly allow traffic from external origins, allowing the React/Vite frontend to fetch and display the data seamlessly.

---

## 🚦 5. Summary of the Unified System

Because of this integration:
1. Developers can test the **entire system** from a single Swagger UI page (`http://127.0.0.1:8080/docs`).
2. The Frontend only has to communicate with one reliable endpoint.
3. Security is centralized—if a token is invalid, the Gateway stops the request before it ever reaches the fragile internal microservices.
4. If one service goes offline, the Gateway gracefully returns a descriptive `502 Bad Gateway` instead of crashing the whole application.

*Integration successfully completed by Intern 1 (Team Lead / Backend & Integration).*
