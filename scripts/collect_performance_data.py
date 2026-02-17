#!/usr/bin/env python3
"""
Performance Data Collection Script

This script collects performance data from k6 load tests and service metrics,
providing structured output that can be used for data-driven optimization decisions.

Usage:
    python scripts/collect_performance_data.py --rps 10 --output results/perf_10rps.json
    python scripts/collect_performance_data.py --rps 50 --baseline results/baseline.json --output results/optimized.json
"""

import argparse
import json
import subprocess
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def run_k6_test(rps: int, output_file: str) -> Dict[str, Any]:
    """Run k6 load test and collect results"""
    print(f"Running k6 load test at {rps} RPS...")
    
    cmd = [
        "docker", "compose", "exec", "-T", "k6",
        "k6", "run",
        "-e", f"RAMPING_RATE={rps}",
        "--summary-export=/results/summary_temp.json",
        "/k6/load.js"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Read the summary file
        summary_path = Path("k6/results/summary_temp.json")
        if summary_path.exists():
            with open(summary_path) as f:
                summary = json.load(f)
            return summary
        else:
            print("Warning: Summary file not found, parsing stdout")
            return {"raw_output": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        print("Error: k6 test timed out")
        sys.exit(1)
    except Exception as e:
        print(f"Error running k6 test: {e}")
        sys.exit(1)


def collect_service_metrics(service: str, port: int) -> Dict[str, Any]:
    """Collect Prometheus metrics from a service"""
    try:
        response = requests.get(f"http://localhost:{port}/metrics", timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            metrics = {}
            
            # Parse key metrics from Prometheus format
            for line in metrics_text.split('\n'):
                if line.startswith('#') or not line.strip():
                    continue
                    
                # Simple parsing for histogram metrics
                if '_bucket{' in line or '_count{' in line or '_sum{' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        metric_name = parts[0].split('{')[0]
                        value = float(parts[-1])
                        if metric_name not in metrics:
                            metrics[metric_name] = []
                        metrics[metric_name].append(value)
            
            return metrics
    except Exception as e:
        print(f"Warning: Could not collect metrics from {service}: {e}")
        return {}


def analyze_k6_results(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from k6 summary"""
    metrics = summary.get("metrics", {})
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "request_metrics": {},
        "error_metrics": {},
        "performance_summary": {}
    }
    
    # HTTP request duration
    if "http_req_duration" in metrics:
        duration = metrics["http_req_duration"]
        analysis["request_metrics"]["duration"] = {
            "avg": duration.get("avg", 0),
            "min": duration.get("min", 0),
            "max": duration.get("max", 0),
            "p50": duration.get("med", 0),
            "p95": duration.get("p(95)", 0),
            "p99": duration.get("p(99)", 0)
        }
    
    # Request rate
    if "http_reqs" in metrics:
        reqs = metrics["http_reqs"]
        analysis["request_metrics"]["total_requests"] = reqs.get("count", 0)
        analysis["request_metrics"]["requests_per_second"] = reqs.get("rate", 0)
    
    # Error rate
    if "http_req_failed" in metrics:
        failed = metrics["http_req_failed"]
        analysis["error_metrics"]["failure_rate"] = failed.get("rate", 0)
        analysis["error_metrics"]["failed_requests"] = failed.get("fails", 0)
    
    # Check thresholds
    if "thresholds" in summary:
        analysis["performance_summary"]["threshold_results"] = summary["thresholds"]
    
    return analysis


def compare_results(baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    """Compare current results with baseline"""
    comparison = {
        "improvements": [],
        "regressions": [],
        "summary": {}
    }
    
    baseline_duration = baseline.get("request_metrics", {}).get("duration", {})
    current_duration = current.get("request_metrics", {}).get("duration", {})
    
    # Compare key metrics
    for metric in ["avg", "p95", "p99"]:
        baseline_val = baseline_duration.get(metric, 0)
        current_val = current_duration.get(metric, 0)
        
        if baseline_val > 0:
            change_pct = ((current_val - baseline_val) / baseline_val) * 100
            
            result = {
                "metric": f"http_req_duration_{metric}",
                "baseline": baseline_val,
                "current": current_val,
                "change_percent": round(change_pct, 2)
            }
            
            if change_pct < -5:  # 5% improvement
                comparison["improvements"].append(result)
            elif change_pct > 5:  # 5% regression
                comparison["regressions"].append(result)
    
    # Compare error rates
    baseline_errors = baseline.get("error_metrics", {}).get("failure_rate", 0)
    current_errors = current.get("error_metrics", {}).get("failure_rate", 0)
    
    if baseline_errors > 0 or current_errors > 0:
        if current_errors < baseline_errors:
            comparison["improvements"].append({
                "metric": "error_rate",
                "baseline": baseline_errors,
                "current": current_errors,
                "change_percent": round(((current_errors - baseline_errors) / max(baseline_errors, 0.0001)) * 100, 2)
            })
        elif current_errors > baseline_errors:
            comparison["regressions"].append({
                "metric": "error_rate",
                "baseline": baseline_errors,
                "current": current_errors,
                "change_percent": round(((current_errors - baseline_errors) / max(baseline_errors, 0.0001)) * 100, 2)
            })
    
    # Summary
    comparison["summary"] = {
        "total_improvements": len(comparison["improvements"]),
        "total_regressions": len(comparison["regressions"]),
        "net_change": "improved" if len(comparison["improvements"]) > len(comparison["regressions"]) else "regressed" if len(comparison["regressions"]) > 0 else "neutral"
    }
    
    return comparison


def generate_ai_report(analysis: Dict[str, Any], comparison: Optional[Dict[str, Any]] = None) -> str:
    """Generate a human-readable report for AI consumption"""
    report = ["# Performance Test Results", ""]
    report.append(f"**Timestamp:** {analysis.get('timestamp', 'unknown')}")
    report.append("")
    
    # Request metrics
    report.append("## Request Performance Metrics")
    duration = analysis.get("request_metrics", {}).get("duration", {})
    if duration:
        report.append(f"- **Average latency:** {duration.get('avg', 0):.2f}ms")
        report.append(f"- **P50 (median):** {duration.get('p50', 0):.2f}ms")
        report.append(f"- **P95:** {duration.get('p95', 0):.2f}ms")
        report.append(f"- **P99:** {duration.get('p99', 0):.2f}ms")
        report.append(f"- **Min:** {duration.get('min', 0):.2f}ms")
        report.append(f"- **Max:** {duration.get('max', 0):.2f}ms")
    report.append("")
    
    # Request rate
    req_metrics = analysis.get("request_metrics", {})
    if "total_requests" in req_metrics:
        report.append(f"- **Total requests:** {req_metrics['total_requests']}")
        report.append(f"- **Requests per second:** {req_metrics.get('requests_per_second', 0):.2f}")
    report.append("")
    
    # Error metrics
    report.append("## Error Metrics")
    error_metrics = analysis.get("error_metrics", {})
    if error_metrics:
        report.append(f"- **Failure rate:** {error_metrics.get('failure_rate', 0):.4f} ({error_metrics.get('failure_rate', 0)*100:.2f}%)")
        report.append(f"- **Failed requests:** {error_metrics.get('failed_requests', 0)}")
    report.append("")
    
    # Comparison with baseline
    if comparison:
        report.append("## Comparison with Baseline")
        report.append(f"**Net change:** {comparison['summary']['net_change']}")
        report.append("")
        
        if comparison["improvements"]:
            report.append("### Improvements ✓")
            for imp in comparison["improvements"]:
                report.append(f"- **{imp['metric']}:** {imp['baseline']:.2f} → {imp['current']:.2f} ({imp['change_percent']:+.2f}%)")
            report.append("")
        
        if comparison["regressions"]:
            report.append("### Regressions ✗")
            for reg in comparison["regressions"]:
                report.append(f"- **{reg['metric']}:** {reg['baseline']:.2f} → {reg['current']:.2f} ({reg['change_percent']:+.2f}%)")
            report.append("")
    
    # Performance summary
    report.append("## AI Optimization Guidance")
    
    # Analyze patterns
    if duration.get('p95', 0) > 500:
        report.append("⚠️ **High P95 latency** (>500ms): Consider optimizing slow requests")
    
    if duration.get('avg', 0) > 0 and duration.get('p95', 0) / duration.get('avg', 1) > 3:
        report.append("⚠️ **High latency variance**: Some requests are significantly slower than average")
    
    if error_metrics.get('failure_rate', 0) > 0.001:
        report.append("⚠️ **Elevated error rate** (>0.1%): Investigate connection issues or service failures")
    
    if duration.get('p95', 0) < 200 and error_metrics.get('failure_rate', 0) < 0.001:
        report.append("✓ **Good performance**: System is performing well under this load")
    
    report.append("")
    report.append("## Data-Driven Optimization Recommendations")
    
    # Specific recommendations based on data
    p95 = duration.get('p95', 0)
    avg = duration.get('avg', 0)
    
    if p95 > 500:
        report.append("1. **Focus on P95 latency reduction**")
        report.append("   - Profile slow requests using the instrumentation endpoints")
        report.append("   - Check database query performance (look for N+1 queries, missing indexes)")
        report.append("   - Review external service call patterns")
    
    if avg > 0 and (p95 / avg) > 2.5:
        report.append("2. **Reduce latency variance**")
        report.append("   - Investigate occasional slow requests")
        report.append("   - Check for database connection pool exhaustion")
        report.append("   - Look for cache misses or cold starts")
    
    if error_metrics.get('failure_rate', 0) > 0:
        report.append("3. **Reduce error rate**")
        report.append("   - Check logs for connection timeouts")
        report.append("   - Review HTTP client configuration (connection pooling, timeouts)")
        report.append("   - Ensure all services are healthy and responsive")
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Collect performance data for optimization")
    parser.add_argument("--rps", type=int, default=10, help="Requests per second for load test")
    parser.add_argument("--baseline", type=str, help="Path to baseline results for comparison")
    parser.add_argument("--output", type=str, required=True, help="Output file for results")
    parser.add_argument("--report", type=str, help="Output file for AI-readable report")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run k6 test
    k6_results = run_k6_test(args.rps, args.output)
    
    # Analyze results
    analysis = analyze_k6_results(k6_results)
    
    # Collect service metrics
    print("Collecting service metrics...")
    analysis["service_metrics"] = {
        "heroes": collect_service_metrics("heroes", 8001),
        "fights": collect_service_metrics("fights", 8004)
    }
    
    # Compare with baseline if provided
    comparison = None
    if args.baseline:
        baseline_path = Path(args.baseline)
        if baseline_path.exists():
            with open(baseline_path) as f:
                baseline = json.load(f)
            comparison = compare_results(baseline, analysis)
            analysis["comparison"] = comparison
        else:
            print(f"Warning: Baseline file {args.baseline} not found")
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"Results saved to {args.output}")
    
    # Generate AI report
    report = generate_ai_report(analysis, comparison)
    
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"AI report saved to {args.report}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    main()
