-- OtoHesap veri modeli (PostgreSQL 16). Sahibi: Murat. Değişiklik = PR + WhatsApp duyurusu.
-- Uygulama: psql "$DATABASE_URL" -f docs/schema.sql

CREATE TABLE IF NOT EXISTS suppliers (
  id              SERIAL PRIMARY KEY,
  name            TEXT NOT NULL,
  contact_channel TEXT NOT NULL CHECK (contact_channel IN ('telegram', 'email')),
  contact_address TEXT NOT NULL,          -- Telegram chat_id veya e-posta
  lead_time_days  INT  NOT NULL DEFAULT 3
);

CREATE TABLE IF NOT EXISTS products (
  id            SERIAL PRIMARY KEY,
  name          TEXT NOT NULL,
  category      TEXT NOT NULL,
  unit_cost     NUMERIC(12,2) NOT NULL,
  sale_price    NUMERIC(12,2) NOT NULL,
  stock_qty     INT NOT NULL DEFAULT 0,
  reorder_point INT NOT NULL,             -- kritik eşik
  target_stock  INT NOT NULL,             -- sipariş sonrası hedef
  supplier_id   INT REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS sales (
  id         SERIAL PRIMARY KEY,
  sold_at    TIMESTAMPTZ NOT NULL,
  product_id INT NOT NULL REFERENCES products(id),
  qty        INT NOT NULL CHECK (qty > 0),
  unit_price NUMERIC(12,2) NOT NULL,
  total      NUMERIC(12,2) NOT NULL,
  channel    TEXT NOT NULL DEFAULT 'magaza' CHECK (channel IN ('magaza', 'online'))
);

CREATE TABLE IF NOT EXISTS expenses (
  id       SERIAL PRIMARY KEY,
  spent_at TIMESTAMPTZ NOT NULL,
  category TEXT NOT NULL,                  -- kira, maas, elektrik, kargo, reklam, tedarik
  amount   NUMERIC(12,2) NOT NULL CHECK (amount > 0),
  vendor   TEXT,
  note     TEXT
);

CREATE TABLE IF NOT EXISTS purchase_orders (
  id           SERIAL PRIMARY KEY,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  product_id   INT NOT NULL REFERENCES products(id),
  supplier_id  INT NOT NULL REFERENCES suppliers(id),
  qty          INT NOT NULL CHECK (qty > 0),
  est_amount   NUMERIC(12,2),
  status       TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'sent', 'rejected')),
  message_text TEXT,
  sent_at      TIMESTAMPTZ,
  notify_ref   TEXT                     -- Telegram message_id, 'dry-run' vb.; gönderim izi
);

-- Mevcut veritabanları için (idempotent)
ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS notify_ref TEXT;

-- Ürün başına yalnız BİR açık sipariş: DB düzeyinde mükerrerlik koruması (çift tıklama, çift zamanlayıcı)
CREATE UNIQUE INDEX IF NOT EXISTS ux_open_order_per_product
  ON purchase_orders (product_id) WHERE status IN ('draft', 'approved', 'sent');

CREATE TABLE IF NOT EXISTS chat_log (
  id       SERIAL PRIMARY KEY,
  asked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  question TEXT NOT NULL,
  sql_text TEXT,
  answer   TEXT,
  ok       BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX IF NOT EXISTS ix_sales_sold_at     ON sales (sold_at);
CREATE INDEX IF NOT EXISTS ix_sales_product     ON sales (product_id);
CREATE INDEX IF NOT EXISTS ix_expenses_spent_at ON expenses (spent_at);
CREATE INDEX IF NOT EXISTS ix_orders_status     ON purchase_orders (status);

CREATE OR REPLACE VIEW v_monthly_cashflow AS
WITH months AS (
  SELECT date_trunc('month', sold_at)  AS month FROM sales
  UNION
  SELECT date_trunc('month', spent_at) AS month FROM expenses
),
inc AS (SELECT date_trunc('month', sold_at)  AS month, SUM(total)  AS income  FROM sales    GROUP BY 1),
exp AS (SELECT date_trunc('month', spent_at) AS month, SUM(amount) AS expense FROM expenses GROUP BY 1)
SELECT m.month,
       COALESCE(inc.income, 0)  AS income,
       COALESCE(exp.expense, 0) AS expense,
       COALESCE(inc.income, 0) - COALESCE(exp.expense, 0) AS net
FROM months m
LEFT JOIN inc ON inc.month = m.month
LEFT JOIN exp ON exp.month = m.month
ORDER BY m.month;

-- Asistan için salt-okur rol (Neon SQL editöründe bir kez; parolayı .env'e koy, depoya koyma)
-- CREATE ROLE otohesap_ro LOGIN PASSWORD '<parola>';
-- GRANT CONNECT ON DATABASE neondb TO otohesap_ro;
-- GRANT USAGE ON SCHEMA public TO otohesap_ro;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO otohesap_ro;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO otohesap_ro;
-- ALTER ROLE otohesap_ro SET statement_timeout = '5s';
-- Gizli iletişim alanı asistana kapalı (sütun düzeyi):
-- REVOKE SELECT ON suppliers FROM otohesap_ro;
-- GRANT SELECT (id, name, contact_channel, lead_time_days) ON suppliers TO otohesap_ro;
