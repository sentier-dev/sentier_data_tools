import pandas as pd
import pandas_flavor as pf

from sentier_data_tools.logs import stdout_feedback_logger as logger


@pf.register_dataframe_method
def add_column_metadata(df: pd.DataFrame, metadata: list[dict]) -> pd.DataFrame:
    """
    Create new values in `df.attrs` with column metadata. The resulting `attrs` looks like:

    ```python
    attrs['sdt']['columns'][<column_label>] = <dict>
    ```

    We apply this function whenever we retrieve a dataframe from the datastore, and use
    `Dataset.columns` as the metadata.

    """
    if not len(df.columns) == len(metadata):
        raise AttributeError("`metadata` length doesn't match dataframe columns")

    if "sdt" not in df.attrs:
        df.attrs["sdt"] = {}

    df.attrs["sdt"]["columns"] = {
        column: obj for column, obj in zip(df.columns, metadata)
    }

    return df


@pf.register_dataframe_method
def apply_aliases(df: pd.DataFrame, aliases: dict[str, str]) -> pd.DataFrame:
    if "sdt" not in df.attrs:
        df.attrs["sdt"] = {}

    aliases = {str(key): value for key, value in aliases.items()}
    reverse_mapping = {
        value: key for key, value in aliases.items() if key in df.columns
    }
    df.rename(columns=aliases, inplace=True)
    df.attrs["sdt"]["aliased"] = True
    df.attrs["sdt"]["mapping"] = reverse_mapping
    return df


@pf.register_dataframe_method
def restore_column_iris(df: pd.DataFrame) -> pd.DataFrame:
    """Restore original dataframe columns labels"""
    if "sdt" in df.attrs and df.attrs["sdt"].get("aliased"):
        logger.debug(
            "Restoring %s columns names for dataframe %s",
            len(df.attrs["sdt"]["mapping"]),
            id(df),
        )
        df.rename(columns=df.attrs["mapping"], inplace=True)
    return df
