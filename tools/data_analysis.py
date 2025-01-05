"""Data analysis tool for processing and analyzing data."""

import re
import statistics
from typing import List, Dict, Type
from pydantic import BaseModel, Field, validator
from langchain_core.tools import BaseTool
from utils.error_handlers import handle_tool_error, ToolError
from .python_repl import PythonREPLTool


class DataAnalysisInput(BaseModel):
    """Input schema for DataAnalysis tool."""
    query: str = Field(
        ...,
        description="[CRITICAL] Query MUST include a dataset. Examples:\n"
                    "- 'Calculate mean, median, std of dataset: [1, 2, 3]'\n"
                    "- 'Compare datasets: [10, 20, 30], [5, 15, 25]'\n"
                    "- 'Analyze dataset: [1, ..., 100]'\n"
    )

    @validator("query")
    def validate_query(cls, v: str) -> str:
        """Validate and classify the query."""
        v = v.strip('{}"\' ')
        v = v.lower()

        if '[' in v and ']' in v:
            return "dataset|statistics"

        numbers = re.findall(r'-?\d*\.?\d+', v)
        if len(numbers) > 1:
            return "dataset|statistics"

        return "dataset|general"


class DataAnalysisTool(BaseTool):
    """Tool for performing data analysis."""
    name: str = Field(default="data_analysis")
    description: str = Field(
        default="""
        [CRITICAL] This is the MANDATORY tool for ANY dataset analysis. ALWAYS use this tool for:
        1. Numbers in square brackets [1, 2, 3]
        2. Requests for mean, median, or std
        3. Multiple numbers in sequence
        4. Datasets with ellipsis [1, ..., 100]
        5. Dataset comparisons [1,2,3], [4,5,6]

        Examples:
        ✓ 'Calculate mean of [1, 2, 3]' -> Uses this tool
        ✓ 'Find statistics for [23, 45, 67]' -> Uses this tool
        ✓ 'Get mean of numbers: 1, 2, 3' -> Uses this tool
        ✓ 'Analyze dataset: [1, ..., 100]' -> Uses this tool
        ✓ 'Compare: [1,2,3], [4,5,6]' -> Uses this tool

        [IMPORTANT] If you see ANY of these patterns, you MUST use this tool.
        """
    )
    args_schema: Type[BaseModel] = DataAnalysisInput

    def _expand_ellipsis(self, numbers: str) -> List[float]:
        """Expand dataset with ellipsis notation."""
        try:
            parts = [x.strip() for x in numbers.split(',')]
            if '...' in parts:
                start_idx = parts.index('...')
                if start_idx > 0 and start_idx < len(parts) - 1:
                    start = float(parts[start_idx - 1])
                    end = float(parts[start_idx + 1])
                    step = 1 if end > start else -1
                    expanded = list(range(int(start) + step, int(end), step))
                    return [float(x) for x in parts[:start_idx]] + expanded + [float(x) for x in parts[start_idx + 1:]]
            return [float(x) for x in parts if x != '...']
        except Exception as e:
            raise ValueError(f"Invalid ellipsis format: {str(e)}")

    def _validate_dataset(self, dataset: List[float]) -> None:
        """Validate dataset for statistical analysis."""
        if not dataset:
            raise ValueError("Dataset is empty")
        if len(dataset) < 2:
            raise ValueError("Dataset must contain at least 2 values for statistical analysis")
        if not all(isinstance(x, (int, float)) for x in dataset):
            raise ValueError("Dataset contains non-numeric values")

    @handle_tool_error
    def _run(self, query: str) -> str:
        """Run the data analysis tool."""
        try:
            parsed_query = self.args_schema(query=query).query
            data_source, analysis_type = parsed_query.split("|")

            if analysis_type == "statistics":
                return self._handle_statistical_analysis(query)
            elif analysis_type == "trend":
                return "Trend analysis is not implemented yet."
            elif analysis_type == "comparison":
                return "Dataset comparison is not implemented yet."
            elif analysis_type == "financial":
                return "Financial analysis is not implemented yet."
            else:
                return "General analysis is not implemented yet."

        except Exception as e:
            raise ToolError(f"Analysis failed: {str(e)}")

    def _handle_statistical_analysis(self, query: str) -> str:
        """Handle statistical analysis requests."""
        try:
            numbers = re.findall(r'\[([^\]]+)\]', query)
            if numbers:
                all_datasets = []
                for dataset_str in numbers:
                    dataset = self._expand_ellipsis(dataset_str)
                    self._validate_dataset(dataset)
                    all_datasets.append(dataset)

                if len(all_datasets) > 1:
                    return self._compare_datasets(all_datasets)

                dataset = all_datasets[0]
            else:
                numbers = re.findall(r'-?\d*\.?\d+', query)
                if not numbers:
                    raise ValueError("No dataset found in query.")
                dataset = [float(x) for x in numbers]
                self._validate_dataset(dataset)

            repl = PythonREPLTool()
            code = f"""
import statistics
dataset = {dataset}
stats = {{
    'mean': statistics.mean(dataset),
    'median': statistics.median(dataset),
    'std_dev': statistics.stdev(dataset),
    'min': min(dataset),
    'max': max(dataset),
    'trend': 'increasing' if dataset[-1] > dataset[0] else 'decreasing'
}}
print(f"Dataset Analysis:")
print(f"Mean: {{stats['mean']:.2f}}")
print(f"Median: {{stats['median']:.2f}}")
print(f"Standard Deviation: {{stats['std_dev']:.2f}}")
print(f"Min: {{stats['min']:.2f}}")
print(f"Max: {{stats['max']:.2f}}")
print(f"Trend: {{stats['trend']}}")
"""
            return repl.run(code)
        except Exception as e:
            raise ToolError(f"Statistical analysis failed: {str(e)}")

    def _compare_datasets(self, datasets: List[List[float]]) -> str:
        """Compare multiple datasets."""
        try:
            # Validate datasets
            for dataset in datasets:
                self._validate_dataset(dataset)

            # Generate Python code for comparison
            stats_code = """
import statistics

datasets = {datasets}
comparisons = []

for dataset in datasets:
    stats = {{
        'mean': statistics.mean(dataset),
        'median': statistics.median(dataset),
        'std_dev': statistics.stdev(dataset) if len(dataset) > 1 else 0.0,
        'min': min(dataset),
        'max': max(dataset)
    }}
    comparisons.append(stats)

print("Dataset Comparisons:")
for i, stats in enumerate(comparisons):
    print(f"Dataset {{i+1}}:")
    print(f"  Mean: {{stats['mean']:.2f}}")
    print(f"  Median: {{stats['median']:.2f}}")
    print(f"  Standard Deviation: {{stats['std_dev']:.2f}}")
    print(f"  Min: {{stats['min']:.2f}}")
    print(f"  Max: {{stats['max']:.2f}}")
""".format(datasets=datasets)

            # Log generated code for debugging
            print("Generated Python Code for Comparison:\n", stats_code)

            # Execute the generated code
            repl = PythonREPLTool()
            return repl.run(stats_code)

        except Exception as e:
            raise ToolError(f"Dataset comparison failed: {str(e)}")

    async def _arun(self, query: str) -> str:
        """Run the data analysis tool asynchronously."""
        try:
            return self._run(query)
        except Exception as e:
            raise ToolError(f"Async analysis failed: {str(e)}")
