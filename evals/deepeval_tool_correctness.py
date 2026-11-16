"""DeepEval ToolCorrectnessMetric on the context agent's tool calls from completed live Claude runs (Nov 15).
Deterministic (no LLM judge): expected tools for a certificate task must all be called."""
import os, json
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")
from deepeval.test_case import LLMTestCase, ToolCall
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.models import DeepEvalBaseLLM

class NoLLM(DeepEvalBaseLLM):
    """Stub: ToolCorrectness without available_tools is deterministic; this model must never be called."""
    def __init__(self): pass
    def load_model(self): return None
    def generate(self, *a, **k): raise RuntimeError("LLM judge not used in this deterministic eval")
    async def a_generate(self, *a, **k): raise RuntimeError("LLM judge not used in this deterministic eval")
    def get_model_name(self): return "none (deterministic)"


FOUR = ["get_account", "get_holder_requirements", "get_policy", "get_policy"]
TWO = ["get_account", "get_holder_requirements"]
RUNS = [  # (run time, context prompt version, tools called) from the artifact database
 ("19:31", "context@v1", FOUR), ("19:32", "context@v1", FOUR), ("19:32b", "context@v1", FOUR), ("19:48", "context@v1", FOUR),
 ("19:55", "context@v2", TWO), ("19:56", "context@v2", TWO), ("19:57", "context@v2", FOUR),
 ("19:59", "context@v3", FOUR), ("20:00", "context@v3", FOUR), ("20:09", "context@v3", FOUR)]
EXPECTED = [ToolCall(name=n) for n in ["get_account", "get_policy", "get_holder_requirements"]]

results = []
for t, ver, tools in RUNS:
    tc = LLMTestCase(input="Certificate task B1-T1: COI for Crestline Distribution Center", actual_output="tool plan",
                     tools_called=[ToolCall(name=n) for n in tools], expected_tools=EXPECTED)
    m = ToolCorrectnessMetric(threshold=1.0, include_reason=False, model=NoLLM(), async_mode=False)
    m.measure(tc)
    results.append({"run": t, "version": ver, "score": round(m.score, 2), "pass": bool(m.is_successful())})

by = {}
for r in results: by.setdefault(r["version"], []).append(r["pass"])
print(json.dumps(results, indent=1))
for v, ps in by.items(): print(f"{v}: {sum(ps)}/{len(ps)} runs passed tool correctness")
json.dump({"metric": "deepeval.ToolCorrectnessMetric", "deepeval_version": __import__("deepeval").__version__, "results": results}, open(os.path.join(os.path.dirname(__file__), "deepeval_results.json"), "w"), indent=1)
