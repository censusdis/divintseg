import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
from typing import Any, Iterable, Optional, Union


def _diversity_of_df(
        df: pd.DataFrame,
) -> pd.Series:
    """
    Compute the diversity of each row of a dataframe.
    
    Parameters
    ----------
    df
        The DataFrame
    Returns
    -------
        A tuple of a series containing the diversity metric for each
        row and a series of the total population of each row.

    """

    # Compute the total population of each row, as
    # a series.
    s_total_population = df.sum(axis='columns', numeric_only=True)

    # Compute the fraction of the population in each
    # group. This is also known as p.
    df_frac = df.div(s_total_population, axis="rows")

    # Now let q = 1 - p and compute pq.
    df_pq = df_frac * (1 - df_frac)

    s_diversity = df_pq.sum(axis=1)
    s_diversity.name = 'diversity'

    return s_diversity, s_total_population


def diversity(
        population: Union[pd.DataFrame, Iterable[float]]
) -> Union[pd.Series, float]:
    if isinstance(population, pd.DataFrame):
        return _diversity_of_df(population)[0]
    else:
        return _diversity_of_df(
            pd.DataFrame([population])
        )[0][0]


def _drop_non_numeric_except(
        df: pd.DataFrame,
        by: Optional[Any],
        over: Optional[Any],
) -> pd.DataFrame:
    drop_cols = [
        col for col in df.columns
        if (
            not is_numeric_dtype(df[col]) and
            col != by and col != over
        )
    ]

    if len(drop_cols) > 0:
        return df.drop(drop_cols, axis='columns')

    return df


def integration(
        df: pd.DataFrame,
        by=None,
        over=None,
        *,
        drop_non_numeric: bool = False,
) -> pd.DataFrame:
    def integration_of_group(df_group: pd.DataFrame) -> float:
        if over is not None:
            df_group = df_group.groupby(over).sum()

        s_div, s_total = _diversity_of_df(df_group)

        return np.average(s_div, weights=s_total)

    if drop_non_numeric:
        df = _drop_non_numeric_except(df, by, over)

    df_integration = pd.DataFrame(
        df.groupby(by=by).apply(integration_of_group),
        columns=['integration']
    )

    return df_integration


def segregation(
        df: pd.DataFrame,
        by=None,
        over=None,
        *,
        drop_non_numeric: bool = False,
) -> pd.DataFrame:
    df_segregation = 1.0 - integration(df, by=by, over=over, drop_non_numeric=drop_non_numeric)
    df_segregation.columns = ['segregation']

    return df_segregation


def di(
        df: pd.DataFrame,
        by=None,
        over=None,
        *,
        add_segregation: bool = False,
        drop_non_numeric: bool = False,
) -> pd.DataFrame:
    if drop_non_numeric:
        df = _drop_non_numeric_except(df, by, over)

    if over is not None:
        df_sum_by = df.drop(over, axis='columns').groupby(by=by).sum()
    else:
        df_sum_by = df.groupby(by=by).sum()

    df_diversity = diversity(df_sum_by)

    df_integration = integration(df, by=by, over=over)

    df_di = pd.concat([df_diversity, df_integration], axis=1)

    if add_segregation:
        df_di['segregation'] = 1.0 - df_di['integration']

    return df_di
