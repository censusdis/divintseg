# Copyright (c) 2022 Darren Erik Vengroff

from typing import Any, Iterable, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pandas.api.types


def _diversity_of_df(
    df_communities: pd.DataFrame,
) -> Tuple[pd.Series, pd.Series]:
    """
    Compute the diversity of each row of a dataframe.

    Each row is assumed to be an independent community.

    Parameters
    ----------
    df_communities
        The DataFrame
    Returns
    -------
        A tuple of a series containing the diversity metric for each
        row and a series of the total population of each row.

    """

    # Compute the total population of each row, as
    # a series.
    s_total_population = df_communities.sum(axis="columns", numeric_only=True)

    # Compute the fraction of the population in each
    # group. This is also known as p.
    df_p = df_communities.div(s_total_population, axis="rows")

    # Now let q = 1 - p and compute pq.
    df_pq = df_p * (1 - df_p)

    s_diversity = df_pq.sum(axis=1)
    s_diversity.name = "diversity"

    return s_diversity, s_total_population


def diversity(
    communities: Union[pd.DataFrame, Iterable[float]]
) -> Union[pd.Series, float]:
    """
    Compute the diversity of one or more communities.

    Parameters
    ----------
    communities
        The communities. This is either an iterable over
        the population of each group in the community or,
        more commonly, a :py:class:`~pd.DataFrame` with
        each row representing a community and each column
        representing a group.
    Returns
    -------
        The diversity of the community or, if passed a
        :py:class:`~pd.DataFrame` then a :py:class:`~pd.Series`
        with one entry for the diversity of each community.
    """
    if isinstance(communities, pd.DataFrame):
        return _diversity_of_df(communities)[0]
    else:
        return _diversity_of_df(pd.DataFrame([communities]))[0][0]


def _drop_non_numeric_except(
    df: pd.DataFrame,
    by: Optional[Any],
    over: Optional[Any],
) -> pd.DataFrame:
    """
    A helper function to drop non-numeric columns that
    may be present, e.g. for different political boundaries
    that are not needed for the current diversity or integration
    calculation.

    Parameters
    ----------
    df
        The original dataframe
    by
        What we are grouping by. This column will not be removed.
    over
        What we are computing inner diversity over. This column
        will not be removed.

    Returns
    -------
        The data with non-numeric columns other than `by` and
        `over` removed.
    """
    drop_cols = [
        col
        for col in df.columns
        if (
            not pandas.api.types.is_numeric_dtype(df[col]) and col != by and col != over
        )
    ]

    if len(drop_cols) > 0:
        return df.drop(drop_cols, axis="columns")

    return df


def integration(
    df_communities: pd.DataFrame,
    by=None,
    over=None,
    *,
    drop_non_numeric: bool = False,
) -> pd.DataFrame:
    """
    Compute the integration of one of more communities
    over a nested level of population aggregation. For
    example, with US census data we might compute integration
    of block groups over blocks.

    Parameters
    ----------
    df_communities
        A :py:class:`pd.DataFrame` of communities.
    by
        The column or index to group by in order to
        partition the rows into communities.
    over
        The column to group by in order to partition
        the rows of each community into smaller
        aggregation units where the base diversity will
        be computed. If `None` then each row is assumed
        to represent a different community.
    drop_non_numeric
        If `True`, then any non-numeric column other than
        those specified by `by` and `over` will be
        implicitly dropped. This is useful if there are columns
        naming other levels of geographic aggregation that
        should be ignored.
    Returns
    -------
        A :py:class:`~pd.Series` containing the integration of
        each community.
    """

    def integration_of_group(df_group: pd.DataFrame) -> float:
        """
        A helper method to compute the integration of each group.
        """
        if over is not None:
            df_group = df_group.groupby(over).sum(numeric_only=True)

        s_div, s_total = _diversity_of_df(df_group)

        # If there is no population, then there is no integration.
        if s_total.sum() == 0:
            return 0.0

        return np.average(s_div, weights=s_total)

    if drop_non_numeric:
        df_communities = _drop_non_numeric_except(df_communities, by, over)

    df_integration = pd.DataFrame(
        df_communities.groupby(by=by).apply(integration_of_group),
        columns=["integration"],
    )

    return df_integration


def segregation(
    df_communities: pd.DataFrame,
    by=None,
    over=None,
    *,
    drop_non_numeric: bool = False,
) -> pd.DataFrame:
    """
    Compute the segregation of one of more communities
    over a nested level of population aggregation. For
    example, with US census data we might compute integration
    of block groups over blocks.

    Parameters
    ----------
    df_communities
        A :py:class:`pd.DataFrame` of communities.
    by
        The column or index to group by in order to
        partition the rows into communities.
    over
        The column to group by in order to partition
        the rows of each community into smaller
        aggregation units where the base diversity will
        be computed. If `None` then each row is assumed
        to represent a different community.
    drop_non_numeric
        If `True`, then any non-numeric column other than
        those specified by `by` and `over` will be
        implicitly dropped. This is useful if there are columns
        naming other levels of geographic aggregation that
        should be ignored.
    Returns
    -------
        A :py:class:`~pd.Series` containing the segregation of
        each community.
    """

    df_segregation = 1.0 - integration(
        df_communities, by=by, over=over, drop_non_numeric=drop_non_numeric
    )
    df_segregation.columns = ["segregation"]

    return df_segregation


def di(
    df_communities: pd.DataFrame,
    by=None,
    over=None,
    *,
    add_segregation: bool = False,
    drop_non_numeric: bool = False,
) -> pd.DataFrame:
    """
    Compute the diversity, integration, and optionally
    the segregation of each of a collection of communities.

    Parameters
    ----------
    df_communities
        A :py:class:`pd.DataFrame` of communities.
    by
        The column or index to group by in order to
        partition the rows into communities.
    over
        The column to group by in order to partition
        the rows of each community into smaller
        aggregation units where the base diversity will
        be computed. If `None` then each row is assumed
        to represent a different community.
    add_segregation
        if `True` add a column to the results for
        segregation.
    drop_non_numeric
        If `True`, then any non-numeric column other than
        those specified by `by` and `over` will be
        implicitly dropped. This is useful if there are columns
        naming other levels of geographic aggregation that
        should be ignored.
    Returns
    -------
        A :py:class:`~pd.Series` containing the diversity,
        integration, and optionally the segregation of
        each community.
    """
    if drop_non_numeric:
        df_communities = _drop_non_numeric_except(df_communities, by, over)

    if over is not None:
        df_sum_by = (
            df_communities.drop(over, axis="columns")
            .groupby(by=by)
            .sum(numeric_only=True)
        )
    else:
        df_sum_by = df_communities.groupby(by=by).sum(numeric_only=True)

    df_diversity = diversity(df_sum_by)

    df_integration = integration(df_communities, by=by, over=over)

    df_di = pd.concat([df_diversity, df_integration], axis=1)

    if add_segregation:
        df_di["segregation"] = 1.0 - df_di["integration"]

    return df_di
