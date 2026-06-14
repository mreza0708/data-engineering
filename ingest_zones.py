import pandas as pd
from sqlalchemy import create_engine
import click

@click.command()
@click.option('--pg-user', default='root', help='Postgres username')
@click.option('--pg-pass', default='root', help='Postgres password')
@click.option('--pg-host', default='localhost', help='Postgres host')
@click.option('--pg-port', default=5433, type=int, help='Postgres port')
@click.option('--pg-db', default='ny_taxi', help='Postgres database name')
def main(pg_user, pg_pass, pg_host, pg_port, pg_db):
    """
    Download NYC taxi zones CSV and load it into Postgres.
    """

    url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"
    table_name = "zones"

    print("Step 1: Creating database connection...")
    engine = create_engine(
        f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )

    print("Step 2: Reading CSV from URL...")
    df_zones = pd.read_csv(url)

    print(f"Step 3: Loaded {len(df_zones)} rows.")
    print("Step 4: Writing data into Postgres table...")

    df_zones.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',
        index=False
    )

    print("Step 5: Done.")

if __name__ == '__main__':
    main()
