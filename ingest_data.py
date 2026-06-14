import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


@click.command()
@click.option("--pg-user", default="root", show_default=True)
@click.option("--pg-pass", default="root", show_default=True)
@click.option("--pg-host", default="localhost", show_default=True)
@click.option("--pg-port", default=5433, show_default=True)
@click.option("--pg-db", default="ny_taxi", show_default=True)
@click.option("--target-table", default="yellow_taxi_trips", show_default=True)
@click.option("--year", default=2021, show_default=True, type=int)
@click.option("--month", default=1, show_default=True, type=int)
@click.option("--chunksize", default=100000, show_default=True, type=int)
def main(
    pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, year, month, chunksize
):
    url = (
        f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/"
        f"yellow/yellow_tripdata_{year:04d}-{month:02d}.csv.gz"
    )

    print(f"Reading from: {url}")

    engine = create_engine(
        f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    )

    dtype = {
        "VendorID": "Int64",
        "passenger_count": "Int64",
        "trip_distance": "float64",
        "RatecodeID": "Int64",
        "store_and_fwd_flag": "string",
        "PULocationID": "Int64",
        "DOLocationID": "Int64",
        "payment_type": "Int64",
        "fare_amount": "float64",
        "extra": "float64",
        "mta_tax": "float64",
        "tip_amount": "float64",
        "tolls_amount": "float64",
        "improvement_surcharge": "float64",
        "total_amount": "float64",
        "congestion_surcharge": "float64",
        "airport_fee": "float64",
    }

    parse_dates = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]

    print("Opening CSV as chunked iterator...")
    df_iter = pd.read_csv(
        url,
        compression="gzip",
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    try:
        first_chunk = next(df_iter)
    except StopIteration:
        print("No data found in the source file.")
        return

    print("Creating table...")
    first_chunk.head(0).to_sql(name=target_table, con=engine, if_exists="replace")

    print("Inserting first chunk...")
    first_chunk.to_sql(
        name=target_table, con=engine, if_exists="append", index=False, method="multi"
    )

    print("Inserting remaining chunks...")
    for chunk in tqdm(df_iter, desc="Ingesting chunks"):
        chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append",
            index=False,
            method="multi",
        )

    print(f"Done! Data ingested into table: {target_table}")
    print(f"Database: {pg_db} | Host: {pg_host} | Port: {pg_port}")


if __name__ == "__main__":
    main()
