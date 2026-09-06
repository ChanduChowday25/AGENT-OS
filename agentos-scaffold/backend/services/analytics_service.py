"""
Analytics Service for AgentOS.

Responsibilities:
- Read CSV files using Pandas.
- Read XLSX/XLS files using Pandas.
- Validate supported file types.
- Clean numeric/currency columns.
- Detect numeric-like columns reliably.
- Convert numeric-like columns into numeric Series.
- Provide dataset information.
- Perform analytical calculations locally.
- Keep dataframe processing separate from the LLM.

Important:
The complete dataset is NEVER sent to the LLM.
Pandas performs all data processing locally.
"""

import logging
from pathlib import Path
from typing import Any, Dict

import pandas as pd


logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Handles local data processing for CSV and XLS/XLSX files.

    The LLM is not used here.
    """

    SUPPORTED_EXTENSIONS = {
        ".csv",
        ".xlsx",
        ".xls",
    }

    # ============================================================
    # Read file
    # ============================================================

    def read_file(
        self,
        file_path: str,
    ) -> pd.DataFrame:
        """
        Read a CSV/XLS/XLSX file.

        Numeric-looking text values such as:

            $50,000
            $75,500
            50,000
            1,250.50

        are automatically converted into numeric values.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: CSV, XLS, XLSX."
            )

        logger.info(
            "Reading analytical file | file=%s",
            path.name,
        )

        try:

            # ----------------------------------------------------
            # Read CSV
            # ----------------------------------------------------

            if extension == ".csv":

                dataframe = pd.read_csv(path)

            # ----------------------------------------------------
            # Read Excel
            # ----------------------------------------------------

            else:

                dataframe = pd.read_excel(path)

            # ----------------------------------------------------
            # Clean column names
            # ----------------------------------------------------

            dataframe.columns = [
                str(column).strip()
                for column in dataframe.columns
            ]

            # ----------------------------------------------------
            # Convert numeric-looking columns
            # ----------------------------------------------------

            dataframe = self.clean_numeric_columns(
                dataframe
            )

            logger.info(
                "File loaded | file=%s | rows=%d | columns=%d",
                path.name,
                len(dataframe),
                len(dataframe.columns),
            )

            logger.info(
                "Detected columns: %s",
                list(dataframe.columns),
            )

            logger.info(
                "Detected numeric columns: %s",
                self.get_numeric_columns(dataframe),
            )

            return dataframe

        except Exception as e:

            logger.exception(
                "Failed to read analytical file | file=%s",
                path.name,
            )

            raise Exception(
                f"Unable to read file '{path.name}': {e}"
            ) from e

    # ============================================================
    # Clean numeric columns
    # ============================================================

    def clean_numeric_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert numeric-looking text columns into numeric columns.

        Handles:

            "$50,000"
            "$75,500"
            "50,000"
            "1000"
            "1,250.50"

        Existing numeric columns remain unchanged.

        Normal text columns remain text.
        """

        dataframe = dataframe.copy()

        for column in dataframe.columns:

            # ----------------------------------------------------
            # Already numeric
            # ----------------------------------------------------

            if pd.api.types.is_numeric_dtype(
                dataframe[column]
            ):
                continue

            original = dataframe[column]

            # ----------------------------------------------------
            # Convert temporarily to string
            # ----------------------------------------------------

            cleaned = (
                original
                .astype("string")
                .str.strip()
            )

            # ----------------------------------------------------
            # Remove common formatting
            # ----------------------------------------------------

            cleaned = (
                cleaned
                .str.replace(
                    "$",
                    "",
                    regex=False,
                )
                .str.replace(
                    "€",
                    "",
                    regex=False,
                )
                .str.replace(
                    "£",
                    "",
                    regex=False,
                )
                .str.replace(
                    ",",
                    "",
                    regex=False,
                )
                .str.replace(
                    "%",
                    "",
                    regex=False,
                )
                .str.strip()
            )

            # ----------------------------------------------------
            # Convert to numeric
            # ----------------------------------------------------

            converted = pd.to_numeric(
                cleaned,
                errors="coerce",
            )

            # ----------------------------------------------------
            # Determine whether conversion is reliable
            # ----------------------------------------------------

            non_empty = (
                cleaned.notna()
                & cleaned.ne("")
            ).sum()

            successfully_converted = (
                converted.notna().sum()
            )

            if (
                non_empty > 0
                and (
                    successfully_converted
                    / non_empty
                ) >= 0.80
            ):

                dataframe[column] = converted

                logger.info(
                    "Converted column to numeric | column=%s",
                    column,
                )

        return dataframe

    # ============================================================
    # Get numeric columns
    # ============================================================

    def get_numeric_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> list[str]:
        """
        Return all columns that contain numeric data.

        This is the central method that the Analytics Agent
        will use when resolving analytical requests.
        """

        numeric_columns = []

        for column in dataframe.columns:

            if self.is_numeric_column(
                dataframe,
                str(column),
            ):

                numeric_columns.append(
                    str(column)
                )

        return numeric_columns

    # ============================================================
    # Detect numeric column
    # ============================================================

    def is_numeric_column(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ) -> bool:
        """
        Determine whether a column contains numeric data.

        Supports:

        - Normal numeric columns
        - Currency values
        - Comma-formatted values
        - Numeric values stored as strings
        """

        if column not in dataframe.columns:
            return False

        series = dataframe[column]

        # --------------------------------------------------------
        # Already numeric
        # --------------------------------------------------------

        if pd.api.types.is_numeric_dtype(series):
            return True

        # --------------------------------------------------------
        # Clean string representation
        # --------------------------------------------------------

        cleaned = (
            series
            .astype("string")
            .str.strip()
            .str.replace(
                "$",
                "",
                regex=False,
            )
            .str.replace(
                "€",
                "",
                regex=False,
            )
            .str.replace(
                "£",
                "",
                regex=False,
            )
            .str.replace(
                ",",
                "",
                regex=False,
            )
            .str.replace(
                "%",
                "",
                regex=False,
            )
        )

        converted = pd.to_numeric(
            cleaned,
            errors="coerce",
        )

        # --------------------------------------------------------
        # Ignore empty columns
        # --------------------------------------------------------

        non_empty = (
            cleaned.notna()
            & cleaned.ne("")
        ).sum()

        if non_empty == 0:
            return False

        valid_numeric = (
            converted.notna().sum()
        )

        # --------------------------------------------------------
        # Require at least 80% valid numeric values
        # --------------------------------------------------------

        return (
            valid_numeric / non_empty
        ) >= 0.80

    # ============================================================
    # Get numeric series
    # ============================================================

    def get_numeric_series(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ) -> pd.Series:
        """
        Return a numeric Pandas Series.

        Handles:

        - Normal numeric values
        - Currency values
        - Comma-formatted numbers
        - Numeric values stored as strings
        """

        if column not in dataframe.columns:
            raise ValueError(
                f"Column '{column}' does not exist."
            )

        series = dataframe[column]

        # --------------------------------------------------------
        # Already numeric
        # --------------------------------------------------------

        if pd.api.types.is_numeric_dtype(series):
            return series

        # --------------------------------------------------------
        # Clean numeric formatting
        # --------------------------------------------------------

        cleaned = (
            series
            .astype("string")
            .str.strip()
            .str.replace(
                "$",
                "",
                regex=False,
            )
            .str.replace(
                "€",
                "",
                regex=False,
            )
            .str.replace(
                "£",
                "",
                regex=False,
            )
            .str.replace(
                ",",
                "",
                regex=False,
            )
            .str.replace(
                "%",
                "",
                regex=False,
            )
        )

        converted = pd.to_numeric(
            cleaned,
            errors="coerce",
        )

        if converted.notna().sum() == 0:
            raise ValueError(
                f"Column '{column}' does not contain "
                f"numeric values."
            )

        return converted

    # ============================================================
    # Dataset information
    # ============================================================

    def get_dataset_info(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Return lightweight information about the dataset.
        """

        columns = []

        numeric_columns = self.get_numeric_columns(
            dataframe
        )

        for column in dataframe.columns:

            columns.append(
                {
                    "name": str(column),
                    "dtype": str(
                        dataframe[column].dtype
                    ),
                    "is_numeric": (
                        str(column)
                        in numeric_columns
                    ),
                    "missing_values": int(
                        dataframe[column]
                        .isna()
                        .sum()
                    ),
                    "unique_values": int(
                        dataframe[column]
                        .nunique(
                            dropna=True
                        )
                    ),
                }
            )

        return {
            "rows": int(
                len(dataframe)
            ),
            "columns": int(
                len(dataframe.columns)
            ),
            "column_details": columns,
            "numeric_columns": numeric_columns,
        }

    # ============================================================
    # Calculate Sum
    # ============================================================

    def calculate_sum(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ) -> float:
        """
        Calculate the sum of a numeric column.
        """

        series = self.get_numeric_series(
            dataframe,
            column,
        )

        return float(
            series.sum()
        )

    # ============================================================
    # Calculate Average
    # ============================================================

    def calculate_average(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ) -> float:
        """
        Calculate the average of a numeric column.
        """

        series = self.get_numeric_series(
            dataframe,
            column,
        )

        return float(
            series.mean()
        )

    # ============================================================
    # Calculate Minimum
    # ============================================================

    def calculate_minimum(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ) -> float:
        """
        Find the minimum value of a numeric column.
        """

        series = self.get_numeric_series(
            dataframe,
            column,
        )

        return float(
            series.min()
        )

    # ============================================================
    # Calculate Maximum
    # ============================================================

    def calculate_maximum(
        self,
        dataframe: pd.DataFrame,
        column: str,
    ) -> float:
        """
        Find the maximum value of a numeric column.
        """

        series = self.get_numeric_series(
            dataframe,
            column,
        )

        return float(
            series.max()
        )

    # ============================================================
    # Count Rows
    # ============================================================

    def count_rows(
        self,
        dataframe: pd.DataFrame,
    ) -> int:
        """
        Return the number of rows.
        """

        return int(
            len(dataframe)
        )

    # ============================================================
    # Filter DataFrame
    # ============================================================

    def filter_dataframe(
        self,
        dataframe: pd.DataFrame,
        filters: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Filter a dataframe using column/value conditions.
        """

        filtered_dataframe = dataframe.copy()

        for column, value in filters.items():

            if column not in filtered_dataframe.columns:
                raise ValueError(
                    f"Column '{column}' does not exist "
                    f"in the dataset."
                )

            if pd.api.types.is_numeric_dtype(
                filtered_dataframe[column]
            ):

                filtered_dataframe = (
                    filtered_dataframe[
                        filtered_dataframe[column]
                        == value
                    ]
                )

            else:

                filtered_dataframe = (
                    filtered_dataframe[
                        filtered_dataframe[column]
                        .astype(str)
                        .str.lower()
                        == str(value).lower()
                    ]
                )

        return filtered_dataframe

    # ============================================================
    # Sort DataFrame
    # ============================================================

    def sort_dataframe(
        self,
        dataframe: pd.DataFrame,
        column: str,
        ascending: bool = True,
    ) -> pd.DataFrame:
        """
        Sort dataframe by a column.
        """

        if column not in dataframe.columns:
            raise ValueError(
                f"Column '{column}' does not exist "
                f"in the dataset."
            )

        return dataframe.sort_values(
            by=column,
            ascending=ascending,
        )

    # ============================================================
    # Group By Sum
    # ============================================================

    def group_by_sum(
        self,
        dataframe: pd.DataFrame,
        group_column: str,
        value_column: str,
    ) -> pd.DataFrame:
        """
        Group by one column and calculate the sum
        of another column.
        """

        if group_column not in dataframe.columns:
            raise ValueError(
                f"Column '{group_column}' does not exist."
            )

        if value_column not in dataframe.columns:
            raise ValueError(
                f"Column '{value_column}' does not exist."
            )

        series = self.get_numeric_series(
            dataframe,
            value_column,
        )

        temporary_dataframe = dataframe.copy()

        temporary_dataframe[
            value_column
        ] = series

        result = (
            temporary_dataframe
            .groupby(group_column)[value_column]
            .sum()
            .reset_index()
        )

        return result


# ================================================================
# Singleton
# ================================================================

analytics_service = AnalyticsService()