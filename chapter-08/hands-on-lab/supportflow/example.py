"""Example usage of the TicketAnalyzer."""

from services.ticket_analyzer import TicketAnalyzer


def main() -> None:
    """Demonstrate ticket analysis with various examples."""
    analyzer = TicketAnalyzer()

    # Example 1: Angry customer with billing issue
    print("=" * 70)
    print("Example 1: Angry Billing Complaint")
    print("=" * 70)
    result1 = analyzer.analyze(
        ticket_id="TKT-2024-001",
        content="""
        This is absolutely unacceptable! I've been charged twice for the same order!
        My account ACC-789456 shows duplicate charges for ORDER-2024-5678.
        I need an IMMEDIATE refund or I'm canceling my subscription!
        """,
    )
    print(f"Ticket ID: {result1.ticket_id}")
    print(f"Category: {result1.category.value} (confidence: {result1.category_confidence})")
    print(f"Urgency: {result1.urgency.value} (confidence: {result1.urgency_confidence})")
    print(f"Sentiment: {result1.sentiment.value} (confidence: {result1.sentiment_confidence})")
    print(f"Priority Review: {result1.requires_priority_review}")
    print(f"Entities: {len(result1.extracted_entities)} found")
    for entity in result1.extracted_entities:
        print(f"  - {entity.entity_type.value}: {entity.value} (confidence: {entity.confidence})")
    print()

    # Example 2: Technical issue with urgency
    print("=" * 70)
    print("Example 2: Critical Technical Issue")
    print("=" * 70)
    result2 = analyzer.analyze(
        ticket_id="TKT-2024-002",
        content="""
        CRITICAL: Our entire team cannot access the system. Login page shows
        error messages and keeps crashing. This is a business emergency - we
        need help ASAP!
        """,
    )
    print(f"Ticket ID: {result2.ticket_id}")
    print(f"Category: {result2.category.value} (confidence: {result2.category_confidence})")
    print(f"Urgency: {result2.urgency.value} (confidence: {result2.urgency_confidence})")
    print(f"Sentiment: {result2.sentiment.value} (confidence: {result2.sentiment_confidence})")
    print(f"Priority Review: {result2.requires_priority_review}")
    print()

    # Example 3: Happy customer with account question
    print("=" * 70)
    print("Example 3: Positive Account Inquiry")
    print("=" * 70)
    result3 = analyzer.analyze(
        ticket_id="TKT-2024-003",
        content="""
        Thank you for the excellent service! I appreciate all your help.
        I just need to update my email address in my account settings.
        Account: ACCT-555123
        """,
    )
    print(f"Ticket ID: {result3.ticket_id}")
    print(f"Category: {result3.category.value} (confidence: {result3.category_confidence})")
    print(f"Urgency: {result3.urgency.value} (confidence: {result3.urgency_confidence})")
    print(f"Sentiment: {result3.sentiment.value} (confidence: {result3.sentiment_confidence})")
    print(f"Priority Review: {result3.requires_priority_review}")
    print(f"Entities: {len(result3.extracted_entities)} found")
    for entity in result3.extracted_entities:
        print(f"  - {entity.entity_type.value}: {entity.value}")
    print()

    # Example 4: Neutral general inquiry
    print("=" * 70)
    print("Example 4: General Inquiry")
    print("=" * 70)
    result4 = analyzer.analyze(
        ticket_id="TKT-2024-004",
        content="I would like to know more about your premium plans and pricing.",
    )
    print(f"Ticket ID: {result4.ticket_id}")
    print(f"Category: {result4.category.value} (confidence: {result4.category_confidence})")
    print(f"Urgency: {result4.urgency.value} (confidence: {result4.urgency_confidence})")
    print(f"Sentiment: {result4.sentiment.value} (confidence: {result4.sentiment_confidence})")
    print(f"Priority Review: {result4.requires_priority_review}")
    print()


if __name__ == "__main__":
    main()
