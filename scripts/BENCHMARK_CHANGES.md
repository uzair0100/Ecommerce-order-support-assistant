# Benchmark Script Robustness Changes

## Summary of Changes to `benchmark_models.py`

Made minimal robustness improvements to handle Phi-3 3.8B timeout on P07 without crashing the benchmark.

---

## Changes Made

### 1. **Wrapped HTTP request in try-except block**
- **Location:** `benchmark_model()` function
- **Change:** Added try-except around the entire requests.post() block
- **Why:** Prevents timeout or network errors from crashing the entire benchmark run

### 2. **Changed timeout from single value to tuple**
- **Old:** `timeout=300` (300 seconds total)
- **New:** `timeout=(30, 60)` (30s connection, 60s read inactivity)
- **Why:** More appropriate for streaming - allows 30s to connect, then fails if no data received for 60s

### 3. **Added Timeout exception handler**
- **Returns:**
  ```python
  {
    "response": "[TIMEOUT]",
    "ttft_seconds": None,
    "total_seconds": None,
    "tokens": 0,
    "tokens_per_second": 0
  }
  ```
- **Why:** Marks timed-out prompts clearly and allows benchmark to continue

### 4. **Added generic RequestException handler**
- **Returns:**
  ```python
  {
    "response": "[ERROR: {exception_type}]",
    "ttft_seconds": None,
    "total_seconds": None,
    "tokens": 0,
    "tokens_per_second": 0
  }
  ```
- **Why:** Catches other network/HTTP errors without crashing

### 5. **Incremental save already present**
- The script already saves `benchmark_results.json` after every completed prompt
- No change needed - this was already working

### 6. **Progress message already present**
- The script already prints "Running benchmark... please wait." before each prompt
- No change needed - this was already working

### 7. **Updated summary calculation to ignore None values**
- **Changed:** `print_summary()` function
- **TTFT calculation:** Filters out `None` values before calling `statistics.mean()`
- **Tokens/sec calculation:** Filters out zero/failed results
- **Added:** Displays "N/A" if all prompts failed
- **Added:** Shows count of failed/timed-out prompts per model
- **Why:** Prevents crash when calculating averages with None values; provides visibility into failures

---

## What Stayed the Same (Preserved)

✅ Same 2 models: qwen2.5:1.5b-instruct, phi3:3.8b  
✅ Same 12 prompts from benchmark_prompts.json  
✅ Same GadgetMart system prompt (complete, unchanged)  
✅ Same temperature=0  
✅ Same Ollama endpoint  
✅ Same output fields in results  
✅ Same JSON output location (scripts/benchmark_results.json)  
✅ All existing benchmark functionality preserved  

---

## How to Use

Run the benchmark as before:

```powershell
cd scripts
python benchmark_models.py
```

**New behavior when timeout occurs:**
- Prints: `[TIMEOUT: Request exceeded 60 seconds of inactivity]`
- Saves result with `[TIMEOUT]` marker
- Continues to next prompt instead of crashing
- Final summary excludes timed-out results from averages

**New behavior when other error occurs:**
- Prints: `[ERROR: {ExceptionType}: {message}]`
- Saves result with `[ERROR: ...]` marker
- Continues to next prompt
- Final summary excludes failed results from averages

---

## Expected Outcome for Your Case

When you rerun the benchmark:
- Qwen2.5 should complete all 12 prompts successfully (as before)
- Phi-3 will now timeout on P07 after 60 seconds of inactivity
- The timeout will be recorded in the results JSON
- The benchmark will continue to P08-P12 for Phi-3
- Final summary will show Phi-3 statistics excluding P07
- All results (including the timeout) will be saved

---

## Verification

✅ Python syntax check passed: `python -m py_compile benchmark_models.py`  
✅ No changes to other project files  
✅ Minimal changes to existing script (only error handling and summary calculation)  
✅ All original functionality preserved  

---

## Next Steps

1. Rerun the benchmark: `python scripts/benchmark_models.py`
2. Check `scripts/benchmark_results.json` for results
3. Note which prompts timed out for Phi-3
4. Use successful results for model selection decision
5. Document findings in `docs/model-benchmark.md`
