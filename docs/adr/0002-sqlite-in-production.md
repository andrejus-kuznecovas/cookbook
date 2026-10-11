# SQLite in production on PythonAnywhere's persistent disk

Production hosting is PythonAnywhere's free tier with the same SQLite file
used in development, living on the host's persistent filesystem. We rejected
managed Postgres (Render free Postgres expires after 90 days; paid tiers
cost money) and rejected Render's free web tier outright because its
ephemeral filesystem wipes SQLite on every redeploy. Two concurrent users
is far below SQLite's limits. Consequence: backups are "download the
db.sqlite3 file"; if the app ever outgrows two users, revisit this ADR
before scaling.
