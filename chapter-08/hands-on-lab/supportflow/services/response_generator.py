"""Response generation service for creating customer-facing ticket responses."""

import re
from typing import Dict, List, Optional

from models.response import (
    GeneratedResponse,
    ResponseApproval,
    ResponseStatus,
    ResponseTemplate,
    TemplateCategory,
)
from models.ticket_analysis import TicketAnalysisResult, TicketCategory


class ResponseGenerator:
    """
    Generates customer-facing responses based on templates and ticket analysis.

    This class maintains a library of response templates and personalizes them
    with ticket-specific details. All generated responses are marked as DRAFT
    requiring mandatory human review per CLAUDE.md constitution.

    CRITICAL: No internal error codes or system details are included in responses.
    """

    def __init__(self) -> None:
        """Initialize ResponseGenerator with default template library."""
        self._templates: Dict[str, ResponseTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load default response templates into the library."""
        default_templates = [
            # Billing templates
            ResponseTemplate(
                template_id="TMPL-BILLING-001",
                category=TemplateCategory.BILLING,
                subject="Regarding Your Billing Inquiry",
                body=(
                    "Dear {customer_name},\n\n"
                    "Thank you for contacting us about {issue_description}. "
                    "We have reviewed your account and {resolution_details}.\n\n"
                    "Your updated balance is {balance_info}.\n\n"
                    "If you have any further questions, please don't hesitate to reach out.\n\n"
                    "Best regards,\nSupport Team"
                ),
                placeholders=["customer_name", "issue_description", "resolution_details", "balance_info"],
                description="General billing inquiry response",
            ),
            ResponseTemplate(
                template_id="TMPL-BILLING-002",
                category=TemplateCategory.BILLING,
                subject="Refund Processed",
                body=(
                    "Dear {customer_name},\n\n"
                    "We have processed your refund request. {refund_details}.\n\n"
                    "Please allow 5-7 business days for the refund to appear in your account.\n\n"
                    "We apologize for any inconvenience and appreciate your patience.\n\n"
                    "Best regards,\nSupport Team"
                ),
                placeholders=["customer_name", "refund_details"],
                description="Refund confirmation response",
            ),
            # Technical templates
            ResponseTemplate(
                template_id="TMPL-TECHNICAL-001",
                category=TemplateCategory.TECHNICAL,
                subject="Technical Issue Resolution",
                body=(
                    "Dear {customer_name},\n\n"
                    "Thank you for reporting the technical issue. {issue_summary}.\n\n"
                    "We have {resolution_action}. Please try again and let us know if you "
                    "continue to experience any difficulties.\n\n"
                    "Best regards,\nSupport Team"
                ),
                placeholders=["customer_name", "issue_summary", "resolution_action"],
                description="Technical issue resolution response",
            ),
            ResponseTemplate(
                template_id="TMPL-TECHNICAL-002",
                category=TemplateCategory.TECHNICAL,
                subject="Feature Clarification",
                body=(
                    "Dear {customer_name},\n\n"
                    "Thank you for your question about {feature_name}. {feature_explanation}.\n\n"
                    "To use this feature: {usage_instructions}.\n\n"
                    "Please let us know if you need any additional assistance.\n\n"
                    "Best regards,\nSupport Team"
                ),
                placeholders=["customer_name", "feature_name", "feature_explanation", "usage_instructions"],
                description="Feature explanation response",
            ),
            # Account templates
            ResponseTemplate(
                template_id="TMPL-ACCOUNT-001",
                category=TemplateCategory.ACCOUNT,
                subject="Account Update Confirmation",
                body=(
                    "Dear {customer_name},\n\n"
                    "Your account has been successfully updated. {update_details}.\n\n"
                    "If you did not make this change, please contact us immediately.\n\n"
                    "Best regards,\nSupport Team"
                ),
                placeholders=["customer_name", "update_details"],
                description="Account update confirmation",
            ),
            # General templates
            ResponseTemplate(
                template_id="TMPL-GENERAL-001",
                category=TemplateCategory.GENERAL,
                subject="Re: Your Support Inquiry",
                body=(
                    "Dear {customer_name},\n\n"
                    "Thank you for contacting us. {response_details}.\n\n"
                    "We're here to help if you have any additional questions.\n\n"
                    "Best regards,\nSupport Team"
                ),
                placeholders=["customer_name", "response_details"],
                description="General inquiry response",
            ),
        ]

        for template in default_templates:
            self._templates[template.template_id] = template

    def add_template(self, template: ResponseTemplate) -> None:
        """
        Add a new response template to the library.

        Args:
            template: The response template to add

        Raises:
            ValueError: If template_id already exists
        """
        if template.template_id in self._templates:
            raise ValueError(f"Template {template.template_id} already exists")
        self._templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[ResponseTemplate]:
        """
        Retrieve a template by ID.

        Args:
            template_id: The template identifier

        Returns:
            ResponseTemplate if found, None otherwise
        """
        return self._templates.get(template_id)

    def list_templates_by_category(self, category: TemplateCategory) -> List[ResponseTemplate]:
        """
        List all templates for a specific category.

        Args:
            category: The template category to filter by

        Returns:
            List of templates matching the category
        """
        return [
            template
            for template in self._templates.values()
            if template.category == category
        ]

    def generate_response(
        self,
        response_id: str,
        ticket_id: str,
        template_id: str,
        substitutions: Dict[str, str],
    ) -> GeneratedResponse:
        """
        Generate a customer response from a template with personalized details.

        IMPORTANT: All generated responses are marked as DRAFT and require human
        review before sending to customers (per CLAUDE.md constitution).

        Args:
            response_id: Unique identifier for this response
            ticket_id: Associated ticket ID
            template_id: Template to use for generation
            substitutions: Dictionary mapping placeholder names to values

        Returns:
            GeneratedResponse with status=DRAFT and requires_human_review=True

        Raises:
            ValueError: If template not found or required placeholders missing

        Example:
            >>> generator = ResponseGenerator()
            >>> response = generator.generate_response(
            ...     response_id="RESP-001",
            ...     ticket_id="TKT-001",
            ...     template_id="TMPL-BILLING-001",
            ...     substitutions={
            ...         "customer_name": "John",
            ...         "issue_description": "duplicate charge",
            ...         "resolution_details": "issued a full refund",
            ...         "balance_info": "$0.00"
            ...     }
            ... )
            >>> response.status
            <ResponseStatus.DRAFT: 'draft'>
            >>> response.requires_human_review
            True
        """
        template = self.get_template(template_id)
        if template is None:
            raise ValueError(f"Template {template_id} not found")

        # Verify all required placeholders are provided
        missing_placeholders = set(template.placeholders) - set(substitutions.keys())
        if missing_placeholders:
            raise ValueError(
                f"Missing required placeholders: {', '.join(missing_placeholders)}"
            )

        # Sanitize substitutions to prevent internal details from leaking
        sanitized_substitutions = self._sanitize_substitutions(substitutions)

        # Substitute placeholders in subject and body
        personalized_subject = self._substitute_placeholders(
            template.subject, sanitized_substitutions
        )
        personalized_body = self._substitute_placeholders(
            template.body, sanitized_substitutions
        )

        # Create response with DRAFT status (enforced by Pydantic model)
        return GeneratedResponse(
            response_id=response_id,
            ticket_id=ticket_id,
            template_id=template_id,
            subject=personalized_subject,
            body=personalized_body,
            status=ResponseStatus.DRAFT,  # Always DRAFT per constitution
            substitutions=sanitized_substitutions,
            requires_human_review=True,  # Always True per constitution
        )

    def generate_from_analysis(
        self,
        response_id: str,
        ticket_analysis: TicketAnalysisResult,
        custom_substitutions: Dict[str, str],
    ) -> GeneratedResponse:
        """
        Generate a response automatically selecting template based on ticket analysis.

        This method uses the ticket category from analysis to select an appropriate
        template, then generates a personalized response.

        Args:
            response_id: Unique identifier for this response
            ticket_analysis: Analysis result containing ticket category
            custom_substitutions: Customer-specific details for personalization

        Returns:
            GeneratedResponse with DRAFT status requiring human review

        Raises:
            ValueError: If no templates available for the ticket category
        """
        # Map ticket category to template category
        category_mapping = {
            TicketCategory.BILLING: TemplateCategory.BILLING,
            TicketCategory.TECHNICAL: TemplateCategory.TECHNICAL,
            TicketCategory.ACCOUNT: TemplateCategory.ACCOUNT,
            TicketCategory.GENERAL: TemplateCategory.GENERAL,
        }

        template_category = category_mapping[ticket_analysis.category]
        available_templates = self.list_templates_by_category(template_category)

        if not available_templates:
            raise ValueError(f"No templates available for category {template_category}")

        # Use the first available template (could be enhanced with more logic)
        template = available_templates[0]

        return self.generate_response(
            response_id=response_id,
            ticket_id=ticket_analysis.ticket_id,
            template_id=template.template_id,
            substitutions=custom_substitutions,
        )

    def approve_response(
        self, response: GeneratedResponse, approval: ResponseApproval
    ) -> GeneratedResponse:
        """
        Mark a response as approved by a human reviewer.

        This method updates the response status and records review metadata.
        Only DRAFT responses can be approved.

        Args:
            response: The generated response to approve
            approval: Approval details including reviewer ID

        Returns:
            Updated GeneratedResponse with APPROVED status

        Raises:
            ValueError: If response is not in DRAFT status
        """
        if response.status != ResponseStatus.DRAFT:
            raise ValueError(f"Cannot approve response with status {response.status}")

        if not approval.approved:
            raise ValueError("Use reject_response() for rejections")

        # Create updated response (Pydantic models are immutable)
        return GeneratedResponse(
            response_id=response.response_id,
            ticket_id=response.ticket_id,
            template_id=response.template_id,
            subject=response.subject,
            body=response.body,
            status=ResponseStatus.APPROVED,
            generated_at=response.generated_at,
            reviewed_at=approval.reviewed_at,
            reviewed_by=approval.reviewer_id,
            substitutions=response.substitutions,
            requires_human_review=False,  # No longer requires review after approval
        )

    def reject_response(
        self, response: GeneratedResponse, approval: ResponseApproval
    ) -> GeneratedResponse:
        """
        Mark a response as rejected by a human reviewer.

        This method updates the response status and records review metadata.
        Only DRAFT responses can be rejected.

        Args:
            response: The generated response to reject
            approval: Rejection details including reviewer ID and feedback

        Returns:
            Updated GeneratedResponse with REJECTED status

        Raises:
            ValueError: If response is not in DRAFT status
        """
        if response.status != ResponseStatus.DRAFT:
            raise ValueError(f"Cannot reject response with status {response.status}")

        if approval.approved:
            raise ValueError("Use approve_response() for approvals")

        # Create updated response
        return GeneratedResponse(
            response_id=response.response_id,
            ticket_id=response.ticket_id,
            template_id=response.template_id,
            subject=response.subject,
            body=response.body,
            status=ResponseStatus.REJECTED,
            generated_at=response.generated_at,
            reviewed_at=approval.reviewed_at,
            reviewed_by=approval.reviewer_id,
            substitutions=response.substitutions,
            requires_human_review=False,  # No longer requires review after rejection
        )

    def _substitute_placeholders(self, text: str, substitutions: Dict[str, str]) -> str:
        """
        Substitute placeholders in text with provided values.

        Args:
            text: Text containing {placeholder} markers
            substitutions: Dictionary mapping placeholder names to values

        Returns:
            Text with placeholders replaced
        """
        result = text
        for placeholder, value in substitutions.items():
            result = result.replace(f"{{{placeholder}}}", value)
        return result

    def _sanitize_substitutions(self, substitutions: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize substitution values to prevent internal details from leaking.

        CRITICAL per CLAUDE.md: Never include internal error codes or system details
        in customer-facing responses.

        Args:
            substitutions: Original substitution dictionary

        Returns:
            Sanitized substitution dictionary

        Raises:
            ValueError: If substitutions contain forbidden internal details
        """
        # Patterns that should never appear in customer-facing content
        forbidden_patterns = [
            r"error code:\s*\d+",
            r"exception:",
            r"stack trace:",
            r"internal id:\s*\d+",
            r"database error",
            r"sql error",
            r"\bsql\b",
            r"traceback",
            r"errno\s*\d+",
            r"500 error",
            r"404 error",
            r"sys\.",
            r"os\.",
        ]

        sanitized = {}
        for key, value in substitutions.items():
            value_lower = value.lower()

            # Check for forbidden patterns
            for pattern in forbidden_patterns:
                if re.search(pattern, value_lower):
                    raise ValueError(
                        f"Substitution for '{key}' contains forbidden internal detail pattern: {pattern}"
                    )

            sanitized[key] = value

        return sanitized
