CREATE TYPE orderstatus AS ENUM ('UNPAID', 'PARTIALLY_PAID', 'PAID', 'ARCHIVED');
CREATE TYPE paymenttype AS ENUM ('CASH', 'ACQUIRING');
CREATE TYPE paymentstatus AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED');
CREATE TABLE orders (
    id SERIAL NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    status orderstatus NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX ix_orders_id ON orders (id);
CREATE TABLE payments (
    id SERIAL NOT NULL,
    order_id INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    payment_type paymenttype NOT NULL,
    status paymentstatus NOT NULL,
    external_id VARCHAR(100),
    error_message VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(order_id) REFERENCES orders (id)
);
CREATE UNIQUE INDEX ix_payments_external_id ON payments (external_id);
CREATE INDEX ix_payments_id ON payments (id);
CREATE INDEX ix_payments_payment_type ON payments (payment_type);
CREATE INDEX ix_payments_status ON payments (status);