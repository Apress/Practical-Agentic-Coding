"""Example usage of the ResponseGenerator with TicketAnalyzer."""

from services.response_generator import ResponseGenerator
from services.ticket_analyzer import TicketAnalyzer
from models.response import ResponseApproval


def main() -> None:
    """Demonstrate response generation workflow."""
    # Initialize services
    analyzer = TicketAnalyzer()
    generator = ResponseGenerator()

    print("=" * 70)
    print("SupportFlow Response Generation Demo")
    print("=" * 70)
    print()

    # Example 1: Billing complaint
    print("=" * 70)
    print("Example 1: Billing Complaint - Full Workflow")
    print("=" * 70)

    ticket_content = """
    I'm very frustrated with the duplicate charge on my account ACC-123456.
    I was charged twice for order ORD-2024-5678 and need this fixed immediately!
    """

    # Step 1: Analyze ticket
    print("\n1. ANALYZING TICKET...")
    analysis = analyzer.analyze("TKT-2024-001", ticket_content)
    print(f"   Category: {analysis.category.value}")
    print(f"   Urgency: {analysis.urgency.value}")
    print(f"   Sentiment: {analysis.sentiment.value}")
    print(f"   Priority Review: {analysis.requires_priority_review}")

    # Step 2: Generate response (always DRAFT)
    print("\n2. GENERATING RESPONSE...")
    response = generator.generate_from_analysis(
        response_id="RESP-2024-001",
        ticket_analysis=analysis,
        custom_substitutions={
            "customer_name": "John Smith",
            "issue_description": "the duplicate charge for order ORD-2024-5678",
            "resolution_details": "identified and reversed the duplicate charge",
            "balance_info": "Your corrected balance is now accurate",
        },
    )
    print(f"   Response ID: {response.response_id}")
    print(f"   Status: {response.status.value} (ALWAYS DRAFT)")
    print(f"   Requires Human Review: {response.requires_human_review} (ALWAYS TRUE)")
    print(f"\n   Subject: {response.subject}")
    print(f"\n   Body:\n   {response.body.replace(chr(10), chr(10) + '   ')}")

    # Step 3: Human review and approval
    print("\n3. HUMAN REVIEW PROCESS...")
    print("    Human agent reviews the generated response")
    print("    Verifies accuracy and tone")
    print("    Approves for sending")

    approval = ResponseApproval(
        response_id=response.response_id,
        reviewer_id="AGENT-042",
        approved=True,
        feedback="Response is accurate and empathetic. Approved for sending.",
    )

    approved_response = generator.approve_response(response, approval)
    print(f"\n   Status: {approved_response.status.value}")
    print(f"   Reviewed By: {approved_response.reviewed_by}")
    print(f"   Reviewed At: {approved_response.reviewed_at}")
    print(f"   Requires Human Review: {approved_response.requires_human_review}")
    print()

    # Example 2: Technical issue
    print("=" * 70)
    print("Example 2: Technical Issue with Rejection")
    print("=" * 70)

    tech_content = "The login page keeps crashing with errors. This is very frustrating!"

    # Analyze
    print("\n1. ANALYZING TICKET...")
    tech_analysis = analyzer.analyze("TKT-2024-002", tech_content)
    print(f"   Category: {tech_analysis.category.value}")
    print(f"   Sentiment: {tech_analysis.sentiment.value}")

    # Generate response
    print("\n2. GENERATING RESPONSE...")
    tech_response = generator.generate_from_analysis(
        response_id="RESP-2024-002",
        ticket_analysis=tech_analysis,
        custom_substitutions={
            "customer_name": "Jane Doe",
            "issue_summary": "You reported login page crashes",
            "resolution_action": "deployed a fix and cleared affected caches",
        },
    )
    print(f"   Status: {tech_response.status.value}")
    print(f"   Subject: {tech_response.subject}")

    # Human reviewer rejects it
    print("\n3. HUMAN REVIEW - REJECTED...")
    print("    Human agent finds response too technical")
    print("    Requests more customer-friendly language")

    rejection = ResponseApproval(
        response_id=tech_response.response_id,
        reviewer_id="AGENT-123",
        approved=False,
        feedback="Too technical. Use simpler language for non-technical users.",
    )

    rejected_response = generator.reject_response(tech_response, rejection)
    print(f"\n   Status: {rejected_response.status.value}")
    print(f"   Reviewer Feedback: {rejection.feedback}")
    print(f"    Response will be regenerated with feedback")
    print()

    # Example 3: List available templates
    print("=" * 70)
    print("Example 3: Available Response Templates")
    print("=" * 70)
    print()

    from models.response import TemplateCategory

    for category in TemplateCategory:
        templates = generator.list_templates_by_category(category)
        print(f"\n{category.value.upper()} Templates ({len(templates)} available):")
        for template in templates:
            print(f"  • {template.template_id}: {template.description}")
            print(f"    Placeholders: {', '.join(template.placeholders)}")

    print()
    print("=" * 70)
    print("CONSTITUTION COMPLIANCE SUMMARY")
    print("=" * 70)
    print("""
 All generated responses start with DRAFT status
 Human review is REQUIRED before sending
 No internal error codes or system details in responses
 Audit trail maintained (timestamps, reviewer IDs)
 Negative sentiment automatically flagged for priority
 Template validation prevents internal details from being added
 Substitution sanitization catches leaked internal details
    """)
    print("=" * 70)


if __name__ == "__main__":
    main()
