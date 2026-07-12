# MaSoVa Order Lifecycle

## Order Statuses

Every order moves through these statuses:

### Delivery orders
RECEIVED → PREPARING → OVEN → BAKED → READY → DISPATCHED → OUT_FOR_DELIVERY → DELIVERED

### Takeaway orders
RECEIVED → PREPARING → OVEN → BAKED → READY → COMPLETED

### Dine-in orders
RECEIVED → PREPARING → READY → SERVED

### Cancelled orders
Any order can be CANCELLED — requires manager approval. A cancellation request does NOT
immediately cancel — the kitchen continues until a manager approves.

## Status Descriptions

- **RECEIVED** — Order placed and confirmed, awaiting kitchen
- **PREPARING** — Kitchen has started work on the order
- **OVEN** — Items are in the oven (baked items only)
- **BAKED** — Baking complete
- **READY** — Order is ready for pickup, dispatch, or serving
- **DISPATCHED** — Awaiting driver pickup at restaurant
- **OUT_FOR_DELIVERY** — Driver assigned and en route to customer
- **DELIVERED** — Successfully delivered to customer
- **SERVED** — Served to table (dine-in)
- **COMPLETED** — Picked up by customer (takeaway)
- **CANCELLED** — Order cancelled (manager approved)

## Order Types
- DELIVERY — delivered to customer address
- TAKEAWAY — customer collects from restaurant
- DINE_IN — served at table

## Payment Statuses
- PENDING, PAID, FAILED, REFUNDED

## Payment Methods
- CARD (Stripe, SCA/3D Secure), CASH, UPI, WALLET, AGGREGATOR_COLLECTED
