"""Example usage of the EscalationEngine for ticket prioritization."""

from services.escalation_engine import EscalationEngine
from services.ticket_analyzer import TicketAnalyzer
from models.escalation import EscalationRule, EscalationPriority


def print_escalation_result(result, ticket_content: str) -> None:
    """Pretty print an escalation result."""
    print(f"\nTicket ID: {result.ticket_id}")
    print(f"Content Preview: {ticket_content[:80]}...")
    print(f"\n{'='*70}")
    print(f"ESCALATION: {'YES ' if result.requires_escalation else 'NO '}")
    if result.requires_escalation:
        print(f"Priority: {result.escalation_priority.value.upper()}")
        print(f"Immediate Attention: {'YES ' if result.requires_immediate_attention else 'NO'}")
        print(f"Negative Indicators: {result.negative_indicator_count}")

        print(f"\nReasons ({len(result.escalation_reasons)}):")
        for i, reason in enumerate(result.escalation_reasons, 1):
            print(f"\n  {i}. {reason.reason.value.upper().replace('_', ' ')}")
            print(f"     {reason.description}")
            if reason.matched_keywords:
                print(f"     Matched: {', '.join(reason.matched_keywords)}")
            if reason.confidence_score is not None:
                print(f"     Confidence: {reason.confidence_score:.0%}")
    print(f"{'='*70}\n")


def main() -> None:
    """Demonstrate escalation engine with various scenarios."""
    print("=" * 70)
    print("SupportFlow Escalation Engine Demonstration")
    print("=" * 70)

    # Initialize services
    analyzer = TicketAnalyzer()
    engine = EscalationEngine()

    # Example 1: Normal ticket - no escalation
    print("\n" + "=" * 70)
    print("Example 1: Normal Inquiry (No Escalation)")
    print("=" * 70)

    content1 = "Hello, I have a question about my account settings. How do I update my email?"
    analysis1 = analyzer.analyze("TKT-001", content1)
    result1 = engine.evaluate("TKT-001", content1, analysis1)
    print_escalation_result(result1, content1)

    # Example 2: Angry customer - HIGH priority
    print("\n" + "=" * 70)
    print("Example 2: Angry Customer (HIGH Priority)")
    print("=" * 70)

    content2 = "I am absolutely furious with your terrible service! This is unacceptable!"
    analysis2 = analyzer.analyze("TKT-002", content2)
    result2 = engine.evaluate("TKT-002", content2, analysis2)
    print_escalation_result(result2, content2)

    # Example 3: High refund - escalation but lower priority
    print("\n" + "=" * 70)
    print("Example 3: High Value Refund ($150)")
    print("=" * 70)

    content3 = "I was charged incorrectly and need a refund of $150 please."
    analysis3 = analyzer.analyze("TKT-003", content3)
    result3 = engine.evaluate("TKT-003", content3, analysis3, refund_amount_usd=150.0)
    print_escalation_result(result3, content3)

    # Example 4: Legal threat - HIGH priority
    print("\n" + "=" * 70)
    print("Example 4: Legal Threat (HIGH Priority)")
    print("=" * 70)

    content4 = "If this isn't fixed immediately, I'm contacting my lawyer and filing a lawsuit!"
    analysis4 = analyzer.analyze("TKT-004", content4)
    result4 = engine.evaluate("TKT-004", content4, analysis4)
    print_escalation_result(result4, content4)

    # Example 5: Social media threat - MEDIUM priority
    print("\n" + "=" * 70)
    print("Example 5: Social Media Threat (MEDIUM Priority)")
    print("=" * 70)

    content5 = "This is disappointing. I'm going to post a review on Yelp and Twitter about this."
    analysis5 = analyzer.analyze("TKT-005", content5)
    result5 = engine.evaluate("TKT-005", content5, analysis5)
    print_escalation_result(result5, content5)

    # Example 6: Competitor mention - MEDIUM priority
    print("\n" + "=" * 70)
    print("Example 6: Competitor Mention (MEDIUM Priority)")
    print("=" * 70)

    content6 = "I'm seriously considering switching to your competitor who has better pricing."
    analysis6 = analyzer.analyze("TKT-006", content6)
    result6 = engine.evaluate("TKT-006", content6, analysis6)
    print_escalation_result(result6, content6)

    # Example 7: Low confidence - escalation
    print("\n" + "=" * 70)
    print("Example 7: Low Confidence Analysis (Escalation)")
    print("=" * 70)

    content7 = "Something weird happening with thing."
    analysis7 = analyzer.analyze("TKT-007", content7)
    result7 = engine.evaluate("TKT-007", content7, analysis7)
    print_escalation_result(result7, content7)

    # Example 8: CRITICAL - Angry + Legal + High Refund
    print("\n" + "=" * 70)
    print("Example 8: CRITICAL Escalation (Multiple Severe Issues)")
    print("=" * 70)

    content8 = """
    I am absolutely FURIOUS! You charged me $500 incorrectly and this is completely
    unacceptable! I'm calling my lawyer first thing tomorrow morning and filing a
    lawsuit. I'm also posting about this nightmare on Twitter, Facebook, and leaving
    reviews everywhere. I'm done with your company and switching to a competitor!
    """
    analysis8 = analyzer.analyze("TKT-008", content8)
    result8 = engine.evaluate("TKT-008", content8, analysis8, refund_amount_usd=500.0)
    print_escalation_result(result8, content8)

    # Example 9: Custom rules
    print("\n" + "=" * 70)
    print("Example 9: Custom Rules (Lower Thresholds)")
    print("=" * 70)

    custom_rules = EscalationRule(
        refund_threshold_usd=50.0,  # Lower threshold
        min_category_confidence=0.70,  # Lower confidence threshold
        negative_indicator_threshold=1,  # More sensitive
    )
    custom_engine = EscalationEngine(custom_rules)

    content9 = "I need a $75 refund for this issue."
    analysis9 = analyzer.analyze("TKT-009", content9)
    result9 = custom_engine.evaluate("TKT-009", content9, analysis9, refund_amount_usd=75.0)
    print("Using custom rules: refund_threshold=$50 (vs. default $100)")
    print_escalation_result(result9, content9)

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    results = [result1, result2, result3, result4, result5, result6, result7, result8, result9]
    escalated = [r for r in results if r.requires_escalation]

    print(f"\nTotal Tickets Evaluated: {len(results)}")
    print(f"Escalated: {len(escalated)} ({len(escalated)/len(results)*100:.0f}%)")
    print(f"Not Escalated: {len(results) - len(escalated)}")

    priority_counts = {}
    for result in escalated:
        priority = result.escalation_priority.value
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    print(f"\nEscalation Priority Breakdown:")
    for priority in [EscalationPriority.CRITICAL, EscalationPriority.HIGH,
                     EscalationPriority.MEDIUM, EscalationPriority.LOW]:
        count = priority_counts.get(priority.value, 0)
        if count > 0:
            print(f"  {priority.value.upper()}: {count} tickets")

    print(f"\nImmediate Attention Required: {sum(1 for r in escalated if r.requires_immediate_attention)}")

    # Reason frequency
    from collections import Counter
    all_reasons = []
    for result in escalated:
        all_reasons.extend([r.reason for r in result.escalation_reasons])

    reason_counts = Counter(all_reasons)
    print(f"\nMost Common Escalation Reasons:")
    for reason, count in reason_counts.most_common(5):
        print(f"  {reason.value.replace('_', ' ').title()}: {count} occurrences")

    print("\n" + "=" * 70)
    print("ESCALATION RULES")
    print("=" * 70)
    print("""
The escalation engine checks for:
 Angry sentiment
 Multiple negative indicators (negative sentiment, low confidence, etc.)
 Refunds over $100 (configurable)
 Legal threats (lawyer, sue, lawsuit, etc.)
 Social media threats (Twitter, Facebook, review sites)
 Competitor mentions (switching, better service, etc.)
 Low confidence scores (< 80% by default)
 Unknown categories (GENERAL with low confidence)

Priority Levels:
• CRITICAL: Angry + legal threat, or 4+ negative indicators
• HIGH: Angry sentiment, legal threat, or 3+ negative indicators
• MEDIUM: Social media, competitor mention, or 2 negative indicators
• LOW: Single indicator (high refund, low confidence)
    """)
    print("=" * 70)


if __name__ == "__main__":
    main()
