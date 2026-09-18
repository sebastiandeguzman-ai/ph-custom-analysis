import pandas as pd
import sys

def run_validations(raw_rows, raw_sum, selected_rows, grouped_row_sum, pivot_interior_sum):
    """Validates row counts and sums, exiting with an error if checks fail."""
    
    # Define the exact checks required by the project plan
    checks = [
        {"check": "raw_row_count", "expected": 2236612, "actual": raw_rows, "tolerance": 0},
        {"check": "raw_dutiablevaluephp_sum", "expected": 3587267375257.0, "actual": raw_sum, "tolerance": 1.0},
        {"check": "grouped_row_count_sum", "expected": selected_rows, "actual": grouped_row_sum, "tolerance": 0},
        {"check": "pivot_interior_sum", "expected": raw_sum, "actual": pivot_interior_sum, "tolerance": 1.0}
    ]
    
    results = []
    all_passed = True
    
    for c in checks:
        # Check if the difference between expected and actual is within tolerance
        diff = abs(c["expected"] - c["actual"])
        passed = diff <= c["tolerance"]
        c["pass"] = passed
        results.append(c)
        
        if not passed:
            all_passed = False
            print(f"FAILED CHECK: {c['check']} | Expected: {c['expected']} | Actual: {c['actual']}")

    # Save to CSV
    val_df = pd.DataFrame(results)
    val_df.to_csv('outputs/validation.csv', index=False)
    
    # Exit if any check failed
    if not all_passed:
        sys.exit(1)
        
    print("All validations passed!")