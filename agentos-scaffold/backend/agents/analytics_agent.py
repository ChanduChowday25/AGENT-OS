"""
Analytics Agent for AgentOS.

Responsibilities:
- Receive an AgentState.
- Validate that an analytical file is available.
- Read CSV/XLS/XLSX files using AnalyticsService.
- Identify simple analytical operations deterministically.
- Use the Analytics Planner only for complex analytical requests.
- Execute all actual calculations locally using Pandas.
- Identify requested columns.
- Identify simple filters.
- Perform calculations locally using Pandas.
- Support sorting.
- Support GroupBy + Sum.
- Support advanced GroupBy aggregations through AnalysisPlan.
- Support dataset information questions.
- Store the result in AgentState.analytics_output.

Important:
- The complete dataset is never sent to the LLM.
- Only a compact dataset schema is sent to the Analytics Planner.
- Simple queries do not use the LLM.
- Complex queries use at most one LLM planning call.
- The LLM only creates an AnalysisPlan.
- All actual data processing is performed locally using Pandas.
"""

import logging
import re

import pandas as pd

from agents.base_agent import BaseAgent
from schemas.agent_state import AgentState
from schemas.analysis_plan import AnalysisPlan
from services.analytics_service import analytics_service
from services.analytics_planner_service import analytics_planner_service
from services.file_service import resolve_file_path

logger = logging.getLogger(__name__)


class AnalyticsAgent(BaseAgent):

    name = "analytics_agent"

    # ============================================================
    # Validate
    # ============================================================

    def validate(
        self,
        state: AgentState,
    ) -> bool:

        if not state.uploaded_files:
            return False

        return True

    # ============================================================
    # Text Normalization
    # ============================================================

    def normalize_text(
        self,
        value: str,
    ) -> str:
        """
        Normalize text for column matching.

        Examples:

            Customer_Age
            customer-age
            Customer Age

        all become:

            customer age
        """

        value = str(value).lower().strip()

        value = value.replace(
            "_",
            " ",
        )

        value = value.replace(
            "-",
            " ",
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    # ============================================================
    # Find analytical column
    # ============================================================

    def find_column(
        self,
        dataframe: pd.DataFrame,
        query: str,
    ) -> str:
        """
        Identify the column the user wants to analyze.

        Supports:

        - Exact column names
        - Column names with spaces
        - Column names with underscores
        - Column names with hyphens
        - Case-insensitive matching
        - Currency columns cleaned by AnalyticsService
        - Natural language column references

        Examples:

            "What is the total income?"
                -> Income

            "What is the average age?"
                -> Age

            "What is the average customer age?"
                -> Customer Age

            "What is the total annual_salary?"
                -> annual_salary
        """

        if len(dataframe.columns) == 0:

            raise ValueError(
                "The dataset does not contain any columns."
            )

        query_normalized = self.normalize_text(
            query
        )

        # ========================================================
        # Get numeric columns
        # ========================================================

        numeric_columns = []

        for column in dataframe.columns:

            if pd.api.types.is_numeric_dtype(
                dataframe[column]
            ):

                numeric_columns.append(
                    str(column)
                )

        # ========================================================
        # If no numeric columns exist
        # ========================================================

        if not numeric_columns:

            raise ValueError(
                "The dataset does not contain any "
                "numeric columns that can be analyzed."
            )

        # ========================================================
        # 1. Exact column match
        # ========================================================

        for column in numeric_columns:

            normalized_column = (
                self.normalize_text(column)
            )

            if normalized_column == query_normalized:

                return column

        # ========================================================
        # 2. Direct column-name matching
        # ========================================================

        numeric_columns_sorted = sorted(
            numeric_columns,
            key=lambda column: len(
                self.normalize_text(column)
            ),
            reverse=True,
        )

        for column in numeric_columns_sorted:

            normalized_column = (
                self.normalize_text(column)
            )

            pattern = (
                r"\b"
                + re.escape(normalized_column)
                + r"\b"
            )

            if re.search(
                pattern,
                query_normalized,
            ):

                return column

        # ========================================================
        # 3. Token-based matching
        # ========================================================

        query_tokens = set(
            query_normalized.split()
        )

        best_column = None
        best_score = 0

        for column in numeric_columns:

            column_tokens = set(
                self.normalize_text(column).split()
            )

            if not column_tokens:
                continue

            matched_tokens = (
                column_tokens
                & query_tokens
            )

            score = len(
                matched_tokens
            )

            if (
                score == len(column_tokens)
                and score > best_score
            ):

                best_column = column
                best_score = score

        if best_column is not None:

            return best_column

        # ========================================================
        # 4. Common analytical word matching
        # ========================================================

        keyword_groups = {

            "income": {
                "income",
                "earnings",
                "salary",
                "wage",
                "revenue",
                "pay",
            },

            "salary": {
                "salary",
                "income",
                "earnings",
                "wage",
                "pay",
            },

            "revenue": {
                "revenue",
                "sales",
                "income",
                "earnings",
                "amount",
            },

            "sales": {
                "sales",
                "revenue",
                "income",
                "amount",
            },

            "age": {
                "age",
            },

            "profit": {
                "profit",
                "earnings",
                "gain",
            },

            "amount": {
                "amount",
                "price",
                "cost",
                "value",
                "revenue",
                "sales",
            },

            "price": {
                "price",
                "amount",
                "cost",
                "value",
            },

            "cost": {
                "cost",
                "price",
                "amount",
                "expense",
            },
        }

        query_words = set(
            query_normalized.split()
        )

        matched_keyword_groups = []

        for keyword, related_words in (
            keyword_groups.items()
        ):

            if keyword in query_words:

                matched_keyword_groups.append(
                    related_words
                )

        for column in numeric_columns:

            normalized_column = (
                self.normalize_text(column)
            )

            column_words = set(
                normalized_column.split()
            )

            for related_words in (
                matched_keyword_groups
            ):

                if column_words & related_words:

                    return column

        # ========================================================
        # 5. If only one numeric column exists
        # ========================================================

        if len(numeric_columns) == 1:

            return numeric_columns[0]

        # ========================================================
        # 6. Multiple numeric columns
        # ========================================================

        raise ValueError(
            "Please specify which column you want "
            "to analyze. Available numeric columns: "
            + ", ".join(
                numeric_columns
            )
        )

    # ============================================================
    # Find GroupBy column
    # ============================================================

    def find_group_column(
        self,
        dataframe,
        query: str,
    ) -> str:
        """
        Identify the column the user wants to group by.

        Example:

            "What are the total sales for each product?"

        -> Product
        """

        query_normalized = self.normalize_text(
            query
        )

        # --------------------------------------------------------
        # Prefer explicitly mentioned non-numeric columns
        # --------------------------------------------------------

        for column in dataframe.columns:

            normalized_column = (
                self.normalize_text(column)
            )

            pattern = (
                r"\b"
                + re.escape(normalized_column)
                + r"\b"
            )

            if re.search(
                pattern,
                query_normalized,
            ):

                if not pd.api.types.is_numeric_dtype(
                    dataframe[column]
                ):

                    return str(column)

        # --------------------------------------------------------
        # Check all explicitly mentioned columns
        # --------------------------------------------------------

        for column in dataframe.columns:

            normalized_column = (
                self.normalize_text(column)
            )

            pattern = (
                r"\b"
                + re.escape(normalized_column)
                + r"\b"
            )

            if re.search(
                pattern,
                query_normalized,
            ):

                return str(column)

        raise ValueError(
            "Please specify which column you want "
            "to group the data by."
        )

    # ============================================================
    # Extract filters
    # ============================================================

    def extract_filters(
        self,
        dataframe,
        query: str,
    ) -> dict:
        """
        Identify simple column/value filters.

        Example:

            "What are the sales of Laptop in 2026?"

        returns:

            {
                "Product": "Laptop",
                "Year": 2026
            }
        """

        filters = {}

        query_lower = query.lower()

        for column in dataframe.columns:

            column_name = str(column)

            unique_values = (
                dataframe[column]
                .dropna()
                .unique()
            )

            for value in unique_values:

                value_text = str(
                    value
                ).strip()

                if not value_text:
                    continue

                if value_text.lower() in query_lower:

                    filters[column_name] = value

                    break

        return filters

    # ============================================================
    # Dataset Questions
    # ============================================================

    def is_dataset_question(
        self,
        query: str,
    ) -> bool:
        """
        Detect questions asking for basic dataset information.
        """

        return (
            "how many columns" in query
            or "number of columns" in query
            or "what columns" in query
            or "which columns" in query
            or "column names" in query
            or "how many rows" in query
            or "number of rows" in query
            or "how many records" in query
            or "number of records" in query
        )

    # ============================================================
    # Determine whether LLM planning is required
    # ============================================================

    def requires_planner(
        self,
        query: str,
    ) -> bool:
        """
        Determine whether the query is complex enough to require
        the Analytics Planner.

        The goal is to keep simple queries completely
        deterministic and avoid unnecessary LLM calls.

        Examples that should NOT use the planner:

            "What is the average salary?"
            "What is the total revenue?"
            "What is the highest salary?"
            "How many rows are there?"
            "What are the column names?"

        Examples that SHOULD use the planner:

            "Which department has the highest average salary?"

            "What is the average salary of employees in Hyderabad?"

            "Give me the top 3 departments by average salary,
             excluding interns."

            "Compare the average salary between Hyderabad
             and Bangalore."
        """

        query = self.normalize_text(
            query
        )

        # --------------------------------------------------------
        # Dataset information questions are already deterministic.
        # --------------------------------------------------------

        if self.is_dataset_question(query):
            return False

        # --------------------------------------------------------
        # Detect basic analytical concepts.
        # --------------------------------------------------------

        has_calculation = bool(
            re.search(
                r"\b(total|sum|average|avg|mean|minimum|"
                r"lowest|smallest|maximum|highest|largest)\b",
                query,
            )
        )

        has_ranking = bool(
            re.search(
                r"\b(top\s+\d+|highest|largest|maximum|"
                r"lowest|smallest|minimum)\b",
                query,
            )
        )

        # --------------------------------------------------------
        # Grouping language.
        #
        # We intentionally don't treat every GroupBy + Sum query
        # as complex because the existing deterministic GroupBy
        # implementation already handles simple cases.
        # --------------------------------------------------------

        has_grouping = bool(
            re.search(
                r"\b(for each|for every|group by|grouped by|"
                r"by product|by category)\b",
                query,
            )
        )

        # --------------------------------------------------------
        # "Which department has the highest..." style questions.
        #
        # These don't necessarily contain "group by", but they
        # clearly require grouping.
        # --------------------------------------------------------

        has_which_group_comparison = bool(
            re.search(
                r"\bwhich\s+\w+(?:\s+\w+){0,2}\s+"
                r"(?:has|have|with)\b",
                query,
            )
        )

        # --------------------------------------------------------
        # Filtering language.
        # --------------------------------------------------------

        has_filter_language = bool(
            re.search(
                r"\b(where|with|excluding|excluding|"
                r"exclude|including|between|after|before|"
                r"greater than|less than|more than|"
                r"under|over|in)\b",
                query,
            )
        )

        # --------------------------------------------------------
        # Comparison language.
        # --------------------------------------------------------

        has_comparison = bool(
            re.search(
                r"\b(compare|compared|versus|vs)\b",
                query,
            )
        )

        # --------------------------------------------------------
        # Explicit Top-N request.
        # --------------------------------------------------------

        has_top_n = bool(
            re.search(
                r"\btop\s+\d+\b",
                query,
            )
        )

        # --------------------------------------------------------
        # Complex combinations.
        # --------------------------------------------------------

        if has_comparison:
            return True

        if has_top_n:
            return True

        if has_which_group_comparison and has_calculation:
            return True

        if has_grouping and has_ranking:
            return True

        if has_calculation and has_filter_language:
            return True

        return False

    # ============================================================
    # Build compact dataset schema
    # ============================================================

    def build_dataset_schema(
        self,
        dataframe: pd.DataFrame,
    ) -> dict:
        """
        Build a compact schema for the Analytics Planner.

        Only column names and data types are sent to the LLM.

        The actual dataset values are never sent.
        """

        schema = {}

        for column in dataframe.columns:

            schema[str(column)] = str(
                dataframe[column].dtype
            )

        return schema

    # ============================================================
    # Execute AnalysisPlan
    # ============================================================

    def execute_analysis_plan(
        self,
        dataframe: pd.DataFrame,
        plan: AnalysisPlan,
    ) -> dict:
        """
        Execute an AnalysisPlan using Pandas.

        The LLM creates the plan.
        Pandas performs the actual computation.
        """

        operation = plan.operation

        # ========================================================
        # Validate operation
        # ========================================================

        supported_operations = {
            "aggregate",
            "groupby",
            "filter",
            "sort",
            "count",
            "info",
        }

        if operation not in supported_operations:

            raise ValueError(
                f"Unsupported analytics operation: {operation}"
            )

        # ========================================================
        # Validate requested columns
        # ========================================================

        if (
            plan.value_column
            and plan.value_column not in dataframe.columns
        ):

            raise ValueError(
                f"Column '{plan.value_column}' "
                f"does not exist in the dataset."
            )

        if (
            plan.group_column
            and plan.group_column not in dataframe.columns
        ):

            raise ValueError(
                f"Column '{plan.group_column}' "
                f"does not exist in the dataset."
            )

        # ========================================================
        # Apply filters first
        # ========================================================

        filtered_dataframe = dataframe.copy()

        for condition in plan.filters:

            if condition.column not in dataframe.columns:

                raise ValueError(
                    f"Filter column '{condition.column}' "
                    f"does not exist in the dataset."
                )

            column = condition.column
            operator = condition.operator
            value = condition.value

            if operator == "equals":

                filtered_dataframe = (
                    filtered_dataframe[
                        filtered_dataframe[column] == value
                    ]
                )

            elif operator == "not_equals":

                filtered_dataframe = (
                    filtered_dataframe[
                        filtered_dataframe[column] != value
                    ]
                )

            elif operator == "greater_than":

                filtered_dataframe = (
                    filtered_dataframe[
                        filtered_dataframe[column] > value
                    ]
                )

            elif operator == "greater_than_or_equal":

                filtered_dataframe = (
                    filtered_dataframe[
                        filtered_dataframe[column] >= value
                    ]
                )

            elif operator == "less_than":

                filtered_dataframe = (
                    filtered_dataframe[
                        filtered_dataframe[column] < value
                    ]
                )

            elif operator == "less_than_or_equal":

                filtered_dataframe = (
                    filtered_dataframe[
                        filtered_dataframe[column] <= value
                    ]
                )

            else:

                raise ValueError(
                    f"Unsupported filter operator: {operator}"
                )

        # ========================================================
        # AGGREGATE
        # ========================================================

        if operation == "aggregate":

            if not plan.value_column:

                raise ValueError(
                    "An aggregation requires a value column."
                )

            column = plan.value_column

            if not pd.api.types.is_numeric_dtype(
                filtered_dataframe[column]
            ) and plan.aggregation != "count":

                raise ValueError(
                    f"Column '{column}' is not numeric and "
                    f"cannot be used with aggregation "
                    f"'{plan.aggregation}'."
                )

            if plan.aggregation == "sum":

                result = analytics_service.calculate_sum(
                    filtered_dataframe,
                    column,
                )

            elif plan.aggregation == "average":

                result = analytics_service.calculate_average(
                    filtered_dataframe,
                    column,
                )

            elif plan.aggregation == "minimum":

                result = analytics_service.calculate_minimum(
                    filtered_dataframe,
                    column,
                )

            elif plan.aggregation == "maximum":

                result = analytics_service.calculate_maximum(
                    filtered_dataframe,
                    column,
                )

            elif plan.aggregation == "count":

                result = filtered_dataframe[column].count()

            else:

                raise ValueError(
                    f"Unsupported aggregation: "
                    f"{plan.aggregation}"
                )

            if hasattr(result, "item"):
                result = result.item()

            return {
                "status": "completed",
                "operation": "aggregate",
                "aggregation": plan.aggregation,
                "column": column,
                "result": result,
                "matched_rows": len(
                    filtered_dataframe
                ),
                "answer": (
                    f"The {plan.aggregation} of {column} "
                    f"is {result}."
                ),
            }

        # ========================================================
        # GROUPBY
        # ========================================================

        if operation == "groupby":

            if not plan.group_column:

                raise ValueError(
                    "GroupBy requires a group column."
                )

            if not plan.value_column:

                raise ValueError(
                    "GroupBy requires a value column."
                )

            group_column = plan.group_column
            value_column = plan.value_column

            if (
                plan.aggregation != "count"
                and not pd.api.types.is_numeric_dtype(
                    filtered_dataframe[value_column]
                )
            ):

                raise ValueError(
                    f"Column '{value_column}' is not numeric "
                    f"and cannot be used with aggregation "
                    f"'{plan.aggregation}'."
                )

            if plan.aggregation == "sum":

                result_dataframe = (
                    filtered_dataframe
                    .groupby(
                        group_column,
                        as_index=False,
                    )[value_column]
                    .sum()
                )

            elif plan.aggregation == "average":

                result_dataframe = (
                    filtered_dataframe
                    .groupby(
                        group_column,
                        as_index=False,
                    )[value_column]
                    .mean()
                )

            elif plan.aggregation == "minimum":

                result_dataframe = (
                    filtered_dataframe
                    .groupby(
                        group_column,
                        as_index=False,
                    )[value_column]
                    .min()
                )

            elif plan.aggregation == "maximum":

                result_dataframe = (
                    filtered_dataframe
                    .groupby(
                        group_column,
                        as_index=False,
                    )[value_column]
                    .max()
                )

            elif plan.aggregation == "count":

                result_dataframe = (
                    filtered_dataframe
                    .groupby(
                        group_column,
                        as_index=False,
                    )[value_column]
                    .count()
                )

            else:

                raise ValueError(
                    f"Unsupported aggregation: "
                    f"{plan.aggregation}"
                )

            # ----------------------------------------------------
            # Sorting
            # ----------------------------------------------------

            if plan.sort:

                sort_column = (
                    plan.sort.column
                    or value_column
                )

                if sort_column not in result_dataframe.columns:

                    raise ValueError(
                        f"Sort column '{sort_column}' "
                        f"does not exist in the result."
                    )

                result_dataframe = (
                    result_dataframe.sort_values(
                        by=sort_column,
                        ascending=(
                            plan.sort.direction == "asc"
                        ),
                    )
                )

            # ----------------------------------------------------
            # Limit
            # ----------------------------------------------------

            if plan.limit is not None:

                if plan.limit <= 0:

                    raise ValueError(
                        "Limit must be greater than zero."
                    )

                result_dataframe = (
                    result_dataframe.head(
                        plan.limit
                    )
                )

            grouped_records = (
                result_dataframe
                .to_dict(
                    orient="records"
                )
            )

            # ----------------------------------------------------
            # Build deterministic answer
            # ----------------------------------------------------

            if grouped_records:

                answer = (
                    f"Grouped {value_column} by "
                    f"{group_column} using "
                    f"{plan.aggregation} aggregation. "
                    f"Top result: "
                    f"{grouped_records[0]}."
                )

            else:

                answer = (
                    "The analysis completed, but no matching "
                    "records were found."
                )

            return {
                "status": "completed",
                "operation": "groupby",
                "group_column": group_column,
                "value_column": value_column,
                "aggregation": plan.aggregation,
                "grouped_rows": grouped_records,
                "answer": answer,
            }

        # ========================================================
        # FILTER
        # ========================================================

        if operation == "filter":

            records = (
                filtered_dataframe
                .to_dict(
                    orient="records"
                )
            )

            return {
                "status": "completed",
                "operation": "filter",
                "filtered_rows": records,
                "matched_rows": len(
                    filtered_dataframe
                ),
                "answer": (
                    f"{len(filtered_dataframe)} "
                    f"matching rows were found."
                ),
            }

        # ========================================================
        # SORT
        # ========================================================

        if operation == "sort":

            if not plan.value_column:

                raise ValueError(
                    "Sorting requires a value column."
                )

            column = plan.value_column

            direction = "asc"

            if plan.sort:

                direction = plan.sort.direction

            result_dataframe = (
                filtered_dataframe.sort_values(
                    by=column,
                    ascending=(
                        direction == "asc"
                    ),
                )
            )

            if plan.limit is not None:

                if plan.limit <= 0:

                    raise ValueError(
                        "Limit must be greater than zero."
                    )

                result_dataframe = (
                    result_dataframe.head(
                        plan.limit
                    )
                )

            sorted_records = (
                result_dataframe
                .to_dict(
                    orient="records"
                )
            )

            return {
                "status": "completed",
                "operation": "sort",
                "column": column,
                "sorted_rows": sorted_records,
                "answer": (
                    f"The data was sorted by {column} "
                    f"in {direction}ending order."
                ),
            }

        # ========================================================
        # COUNT
        # ========================================================

        if operation == "count":

            result = len(
                filtered_dataframe
            )

            return {
                "status": "completed",
                "operation": "count",
                "result": result,
                "answer": (
                    f"The result contains {result} rows."
                ),
            }

        # ========================================================
        # INFO
        # ========================================================

        if operation == "info":

            columns = [
                str(column)
                for column
                in filtered_dataframe.columns
            ]

            return {
                "status": "completed",
                "operation": "info",
                "rows": len(
                    filtered_dataframe
                ),
                "columns": columns,
                "answer": (
                    f"The dataset contains "
                    f"{len(filtered_dataframe)} rows "
                    f"and {len(columns)} columns."
                ),
            }

        raise ValueError(
            f"Unable to execute operation: {operation}"
        )

    # ============================================================
    # Execute
    # ============================================================

    def execute(
        self,
        state: AgentState,
    ) -> AgentState:

        state.status = "running"

        try:

            # ====================================================
            # Validate
            # ====================================================

            if not self.validate(state):

                state.analytics_output = {
                    "status": "failed",
                    "answer": (
                        "No analytical file was provided."
                    ),
                }

                state.status = "failed"

                return state

            # ====================================================
            # Get File
            # ====================================================

            file_path = resolve_file_path(
                state.uploaded_files[0]
            )

            logger.info(
                "Analytics Agent processing file | file=%s",
                file_path.name,
            )

            # ====================================================
            # Read File
            # ====================================================

            dataframe = analytics_service.read_file(
                str(file_path)
            )

            # ====================================================
            # Dataset Information
            # ====================================================

            dataset_info = (
                analytics_service.get_dataset_info(
                    dataframe
                )
            )

            # ====================================================
            # COMPLEX QUERY → LLM PLANNER
            # ====================================================

            if self.requires_planner(
                state.query
            ):

                logger.info(
                    "Complex analytics query detected. "
                    "Using Analytics Planner."
                )

                schema = self.build_dataset_schema(
                    dataframe
                )

                plan = (
                    analytics_planner_service.create_plan(
                        query=state.query,
                        schema=schema,
                    )
                )

                logger.info(
                    "Analytics plan created | operation=%s",
                    plan.operation,
                )

                result = self.execute_analysis_plan(
                    dataframe,
                    plan,
                )

                state.analytics_output = {
                    **result,
                    "plan": plan.model_dump(),
                    "dataset_info": dataset_info,
                }

                state.status = "completed"

                return state

            # ====================================================
            # Existing deterministic logic
            # ====================================================

            query = state.query.lower()

            # ====================================================
            # DATASET QUESTIONS
            # ====================================================

            if self.is_dataset_question(query):

                # ------------------------------------------------
                # Number of columns
                # ------------------------------------------------

                if (
                    "how many columns" in query
                    or "number of columns" in query
                ):

                    result = len(
                        dataframe.columns
                    )

                    state.analytics_output = {
                        "status": "completed",
                        "operation": "count_columns",
                        "result": result,
                        "answer": (
                            f"The dataset contains "
                            f"{result} columns."
                        ),
                    }

                    state.status = "completed"

                    return state

                # ------------------------------------------------
                # Column names
                # ------------------------------------------------

                if (
                    "what columns" in query
                    or "which columns" in query
                    or "column names" in query
                ):

                    columns = [
                        str(column)
                        for column
                        in dataframe.columns
                    ]

                    state.analytics_output = {
                        "status": "completed",
                        "operation": "list_columns",
                        "columns": columns,
                        "answer": (
                            "The columns are: "
                            + ", ".join(columns)
                            + "."
                        ),
                    }

                    state.status = "completed"

                    return state

                # ------------------------------------------------
                # Number of rows
                # ------------------------------------------------

                if (
                    "how many rows" in query
                    or "number of rows" in query
                    or "how many records" in query
                    or "number of records" in query
                ):

                    result = len(dataframe)

                    state.analytics_output = {
                        "status": "completed",
                        "operation": "count_rows",
                        "result": result,
                        "answer": (
                            f"The dataset contains "
                            f"{result} rows."
                        ),
                    }

                    state.status = "completed"

                    return state

            # ====================================================
            # GROUP BY
            # ====================================================

            groupby_requested = (
                "for each" in query
                or "for every" in query
                or "group by" in query
                or "grouped by" in query
                or "by product" in query
                or "by category" in query
            )

            if groupby_requested:

                group_column = (
                    self.find_group_column(
                        dataframe,
                        query,
                    )
                )

                value_column = self.find_column(
                    dataframe,
                    query,
                )

                grouped_dataframe = (
                    analytics_service.group_by_sum(
                        dataframe,
                        group_column,
                        value_column,
                    )
                )

                grouped_records = (
                    grouped_dataframe
                    .to_dict(
                        orient="records"
                    )
                )

                state.analytics_output = {
                    "status": "completed",
                    "operation": "groupby_sum",
                    "group_column": group_column,
                    "value_column": value_column,
                    "grouped_rows": grouped_records,
                    "dataset_info": dataset_info,
                }

                state.status = "completed"

                return state

            # ====================================================
            # SORTING
            # ====================================================

            sort_requested = (
                "highest" in query
                or "largest" in query
                or "maximum" in query
                or "max" in query
                or "top" in query
                or "lowest" in query
                or "smallest" in query
                or "minimum" in query
                or "min" in query
            )

            if sort_requested:

                column = self.find_column(
                    dataframe,
                    query,
                )

                descending = (
                    "highest" in query
                    or "largest" in query
                    or "maximum" in query
                    or "max" in query
                    or "top" in query
                )

                sorted_dataframe = (
                    analytics_service.sort_dataframe(
                        dataframe,
                        column,
                        ascending=not descending,
                    )
                )

                sorted_records = (
                    sorted_dataframe
                    .to_dict(
                        orient="records"
                    )
                )

                state.analytics_output = {
                    "status": "completed",
                    "operation": (
                        "sort_descending"
                        if descending
                        else "sort_ascending"
                    ),
                    "column": column,
                    "sorted_rows": sorted_records,
                    "dataset_info": dataset_info,
                }

                state.status = "completed"

                return state

            # ====================================================
            # CALCULATIONS
            # ====================================================

            calculation_requested = (
                "total" in query
                or "sum" in query
                or "average" in query
                or "avg" in query
                or "mean" in query
                or "minimum" in query
                or "lowest" in query
                or "smallest" in query
                or "maximum" in query
                or "highest" in query
                or "largest" in query
            )

            if calculation_requested:

                column = self.find_column(
                    dataframe,
                    query,
                )

                # ------------------------------------------------
                # SUM
                # ------------------------------------------------

                if (
                    "total" in query
                    or "sum" in query
                ):

                    result = (
                        analytics_service.calculate_sum(
                            dataframe,
                            column,
                        )
                    )

                    answer = (
                        f"The total of {column} "
                        f"is {result}."
                    )

                    operation = "sum"

                # ------------------------------------------------
                # AVERAGE
                # ------------------------------------------------

                elif (
                    "average" in query
                    or "avg" in query
                    or "mean" in query
                ):

                    result = (
                        analytics_service.calculate_average(
                            dataframe,
                            column,
                        )
                    )

                    answer = (
                        f"The average of {column} "
                        f"is {result}."
                    )

                    operation = "average"

                # ------------------------------------------------
                # MINIMUM
                # ------------------------------------------------

                elif (
                    "minimum" in query
                    or "lowest" in query
                    or "smallest" in query
                ):

                    result = (
                        analytics_service.calculate_minimum(
                            dataframe,
                            column,
                        )
                    )

                    answer = (
                        f"The minimum value of "
                        f"{column} is {result}."
                    )

                    operation = "minimum"

                # ------------------------------------------------
                # MAXIMUM
                # ------------------------------------------------

                else:

                    result = (
                        analytics_service.calculate_maximum(
                            dataframe,
                            column,
                        )
                    )

                    answer = (
                        f"The maximum value of "
                        f"{column} is {result}."
                    )

                    operation = "maximum"

                state.analytics_output = {
                    "status": "completed",
                    "answer": answer,
                    "operation": operation,
                    "column": column,
                    "result": (
                        result.item()
                        if hasattr(result, "item")
                        else result
                    ),
                    "dataset_info": dataset_info,
                }

                state.status = "completed"

                return state

            # ====================================================
            # FILTERING
            # ====================================================

            filters = self.extract_filters(
                dataframe,
                state.query,
            )

            filtered_dataframe = (
                analytics_service.filter_dataframe(
                    dataframe,
                    filters,
                )
            )

            filtered_records = (
                filtered_dataframe
                .to_dict(
                    orient="records"
                )
            )

            state.analytics_output = {
                "status": "completed",

                "operation": "filter",

                "filters": {
                    key: value.item()
                    if hasattr(value, "item")
                    else value
                    for key, value in filters.items()
                },

                "filtered_rows": filtered_records,

                "matched_rows": len(
                    filtered_dataframe
                ),

                "dataset_info": dataset_info,
            }

            state.status = "completed"

            return state

        # ========================================================
        # ERROR HANDLING
        # ========================================================

        except Exception as e:

            logger.exception(
                "Analytics Agent execution failed."
            )

            state.analytics_output = {
                "status": "failed",
                "answer": (
                    "I was unable to process "
                    "the analytical request."
                ),
                "error": str(e),
            }

            state.errors.append(
                str(e)
            )

            state.status = "failed"

            return state


# ================================================================
# Singleton
# ================================================================

analytics_agent = AnalyticsAgent()