create table if not exists batteries (
    id text primary key,
    vehicle_type text not null,
    install_date date not null
);

create table if not exists telemetry (
    battery_id text not null references batteries(id) on delete cascade,
    day date not null,
    voltage double precision not null,
    temperature double precision not null,
    cycle_count integer not null,
    depth_of_discharge double precision not null,
    fast_charge_freq double precision not null,
    capacity_pct double precision not null,
    primary key (battery_id, day)
);

create table if not exists predictions (
    battery_id text not null references batteries(id) on delete cascade,
    bhi double precision not null,
    rul_days double precision not null,
    failure_risk_pct double precision not null,
    computed_at timestamptz not null default now()
);

create index if not exists idx_telemetry_battery_day on telemetry(battery_id, day);
create index if not exists idx_predictions_battery_computed_at on predictions(battery_id, computed_at desc);
