#!/usr/bin/env python3
"""
GCP Cost Estimation for Sahay Platform
3-month hosting with 20-25 LLM calls analysis
"""

import pandas as pd
from datetime import datetime

def calculate_gcp_costs():
    """Calculate detailed GCP costs for Sahay platform"""
    
    print("=" * 60)
    print("GCP COST ESTIMATION - SAHAY PLATFORM")
    print("Duration: 3 Months | Usage: 20-25 LLM calls")
    print("=" * 60)
    
    # LLM API Costs (Google GenAI)
    print("\n1. GOOGLE GENAI API COSTS:")
    print("-" * 40)
    
    # Gemini 2.5 Flash pricing (as of 2024)
    input_cost_per_1k = 0.000075  # $0.000075 per 1K input tokens
    output_cost_per_1k = 0.0003   # $0.0003 per 1K output tokens
    
    # Estimated tokens per interaction
    avg_input_tokens = 150   # Student question + context
    avg_output_tokens = 400  # AI response + search results
    
    calls_per_month = 25  # Maximum estimate
    total_calls_3_months = calls_per_month * 3
    
    # Calculate token costs
    total_input_tokens = total_calls_3_months * avg_input_tokens
    total_output_tokens = total_calls_3_months * avg_output_tokens
    
    input_cost = (total_input_tokens / 1000) * input_cost_per_1k
    output_cost = (total_output_tokens / 1000) * output_cost_per_1k
    total_genai_cost = input_cost + output_cost
    
    print(f"Total LLM calls (3 months): {total_calls_3_months}")
    print(f"Input tokens: {total_input_tokens:,} tokens")
    print(f"Output tokens: {total_output_tokens:,} tokens")
    print(f"Input cost: ${input_cost:.4f}")
    print(f"Output cost: ${output_cost:.4f}")
    print(f"Total GenAI API cost: ${total_genai_cost:.2f}")
    
    # Google Search API (if using Search API separately)
    print("\n2. GOOGLE SEARCH API (Optional):")
    print("-" * 40)
    
    # Custom Search JSON API - $5 per 1000 queries
    # But Gemini grounding might be included, so this could be $0
    search_queries = total_calls_3_months * 0.5  # 50% of calls use search
    search_cost_per_1k = 5.0
    search_api_cost = (search_queries / 1000) * search_cost_per_1k
    
    print(f"Search queries: {search_queries}")
    print(f"Search API cost: ${search_api_cost:.2f}")
    print("Note: Search may be included in Gemini grounding (potentially $0)")
    
    # Cloud Infrastructure Costs
    print("\n3. CLOUD INFRASTRUCTURE:")
    print("-" * 40)
    
    # Cloud Run (for hosting the application)
    cloudrun_cpu_hours = 24 * 30 * 3 * 0.1  # 10% CPU utilization
    cloudrun_memory_gb_hours = 24 * 30 * 3 * 0.5  # 0.5GB memory
    cloudrun_requests = total_calls_3_months + 100  # Extra for health checks
    
    cpu_cost = cloudrun_cpu_hours * 0.00002400  # $0.000024 per vCPU-hour
    memory_cost = cloudrun_memory_gb_hours * 0.00000250  # $0.0000025 per GB-hour
    request_cost = cloudrun_requests * 0.0000004  # $0.0000004 per request
    
    cloudrun_cost = cpu_cost + memory_cost + request_cost
    
    print(f"Cloud Run CPU cost: ${cpu_cost:.4f}")
    print(f"Cloud Run Memory cost: ${memory_cost:.4f}")
    print(f"Cloud Run Request cost: ${request_cost:.4f}")
    print(f"Total Cloud Run: ${cloudrun_cost:.2f}")
    
    # Cloud Storage (for CSV files and logs)
    storage_gb = 0.1  # 100MB for CSV files
    storage_cost_per_gb = 0.020  # $0.020 per GB per month
    storage_cost = storage_gb * storage_cost_per_gb * 3
    
    print(f"Cloud Storage (3 months): ${storage_cost:.2f}")
    
    # Cloud Logging
    log_gb = 0.05  # Minimal logging
    logging_cost = log_gb * 0.50 * 3  # $0.50 per GB per month
    
    print(f"Cloud Logging: ${logging_cost:.2f}")
    
    # Load Balancer (if needed)
    lb_cost = 18.0 * 3  # $18/month for HTTP(S) Load Balancer
    print(f"Load Balancer (optional): ${lb_cost:.2f}")
    
    # Total Infrastructure
    total_infrastructure = cloudrun_cost + storage_cost + logging_cost
    total_infrastructure_with_lb = total_infrastructure + lb_cost
    
    print(f"Infrastructure (basic): ${total_infrastructure:.2f}")
    print(f"Infrastructure (with LB): ${total_infrastructure_with_lb:.2f}")
    
    # Domain and SSL
    print("\n4. ADDITIONAL COSTS:")
    print("-" * 40)
    
    domain_cost = 12.0  # Annual domain cost
    ssl_cost = 0.0  # Google-managed SSL is free
    
    print(f"Domain (annual): ${domain_cost:.2f}")
    print(f"SSL Certificate: ${ssl_cost:.2f} (Free with Google)")
    
    # Summary
    print("\n" + "=" * 60)
    print("COST SUMMARY (3 MONTHS)")
    print("=" * 60)
    
    # Scenario 1: Basic (no load balancer, search included in Gemini)
    basic_total = total_genai_cost + total_infrastructure + domain_cost/4  # 1/4 of annual domain
    
    # Scenario 2: With optional components
    full_total = total_genai_cost + search_api_cost + total_infrastructure_with_lb + domain_cost/4
    
    print(f"\nSCENARIO 1 - BASIC SETUP:")
    print(f"• GenAI API: ${total_genai_cost:.2f}")
    print(f"• Cloud Infrastructure: ${total_infrastructure:.2f}")
    print(f"• Domain (3 months): ${domain_cost/4:.2f}")
    print(f"• TOTAL: ${basic_total:.2f}")
    
    print(f"\nSCENARIO 2 - FULL SETUP:")
    print(f"• GenAI API: ${total_genai_cost:.2f}")
    print(f"• Search API: ${search_api_cost:.2f}")
    print(f"• Cloud Infrastructure + LB: ${total_infrastructure_with_lb:.2f}")
    print(f"• Domain (3 months): ${domain_cost/4:.2f}")
    print(f"• TOTAL: ${full_total:.2f}")
    
    # Monthly breakdown
    print(f"\nMONTHLY COSTS:")
    print(f"• Basic Setup: ${basic_total/3:.2f}/month")
    print(f"• Full Setup: ${full_total/3:.2f}/month")
    
    # Free tier benefits
    print("\n" + "=" * 60)
    print("FREE TIER BENEFITS")
    print("=" * 60)
    
    print("""
With Google Cloud Free Tier, you get:
• $300 credit for new accounts (covers 3+ months easily)
• Cloud Run: 2 million requests/month free
• Cloud Storage: 5GB free storage
• Cloud Functions: 2 million invocations free
• Generous GenAI API free tier limits

RECOMMENDATION:
For 20-25 calls with light usage, you'll likely stay within
free tier limits, making your actual cost $0-5 for 3 months!
""")
    
    # Create cost breakdown table
    cost_data = {
        'Component': [
            'GenAI API (Gemini 2.5 Flash)',
            'Search API (if separate)',
            'Cloud Run Hosting',
            'Cloud Storage',
            'Cloud Logging', 
            'Load Balancer (optional)',
            'Domain (3 months)',
            'SSL Certificate'
        ],
        'Basic Cost': [
            f"${total_genai_cost:.2f}",
            "$0.00 (included)",
            f"${cloudrun_cost:.2f}",
            f"${storage_cost:.2f}",
            f"${logging_cost:.2f}",
            "$0.00",
            f"${domain_cost/4:.2f}",
            "$0.00 (free)"
        ],
        'Full Setup': [
            f"${total_genai_cost:.2f}",
            f"${search_api_cost:.2f}",
            f"${cloudrun_cost:.2f}",
            f"${storage_cost:.2f}",
            f"${logging_cost:.2f}",
            f"${lb_cost:.2f}",
            f"${domain_cost/4:.2f}",
            "$0.00 (free)"
        ]
    }
    
    cost_df = pd.DataFrame(cost_data)
    print("\nDETAILED COST BREAKDOWN:")
    print(cost_df.to_string(index=False))
    
    return {
        'basic_total': basic_total,
        'full_total': full_total,
        'genai_cost': total_genai_cost,
        'infrastructure_cost': total_infrastructure,
        'monthly_basic': basic_total/3,
        'monthly_full': full_total/3
    }

if __name__ == "__main__":
    costs = calculate_gcp_costs()
    
    print(f"\n🎯 FINAL ESTIMATE FOR SAHAY PLATFORM:")
    print(f"Expected 3-month cost: ${costs['basic_total']:.2f} - ${costs['full_total']:.2f}")
    print(f"Monthly cost: ${costs['monthly_basic']:.2f} - ${costs['monthly_full']:.2f}")
    print(f"\n💡 With Google Cloud Free Tier: Likely $0-5 total!")
