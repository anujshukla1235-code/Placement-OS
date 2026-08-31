import re

import django_filters
from django.db import models

from .models import Application, Job


class JobFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    branch = django_filters.CharFilter(method="filter_branch")
    company = django_filters.CharFilter(method="filter_company")
    ctc_min = django_filters.NumberFilter(method="filter_ctc_min")
    ctc_max = django_filters.NumberFilter(method="filter_ctc_max")

    class Meta:
        model = Job
        fields = ["status", "branch", "company", "ctc_min", "ctc_max"]

    def filter_branch(self, queryset, name, value):
        # Expect branch to be a string like 'CSE'. For JSONField lists, use contains lookup
        try:
            return queryset.filter(eligibility_branch__contains=[value])
        except Exception:
            # fallback to icontains on string representations
            return queryset.filter(eligibility_branch__icontains=value)

    def filter_company(self, queryset, name, value):
        # Accept a company profile id or company name. (company_old no longer exists —
        # Job.company was consolidated onto accounts.CompanyProfile; this filter used to
        # reference the removed company_old/ctc_old fields and would crash on use.)
        # Only try the id= comparison when value actually looks like a UUID — Django
        # validates every Q() branch's type up front, so passing a plain name straight
        # into company__id=value raises ValidationError even though the OR'd
        # company_name branch would have matched fine.
        import uuid

        try:
            uuid.UUID(str(value))
            return queryset.filter(
                models.Q(company__id=value)
                | models.Q(company__company_name__icontains=value)
            )
        except ValueError:
            return queryset.filter(company__company_name__icontains=value)

    @staticmethod
    def _extract_ctc_number(ctc_text):
        """ctc is a free-text CharField like '12 LPA' or '10-15 LPA', not a numeric
        column (that changed when the old numeric ctc_old field was removed as part of
        consolidating the duplicate Company/CompanyProfile models). Extract the first
        number found so ctc_min/ctc_max filtering still works on a best-effort basis."""
        if not ctc_text:
            return None
        match = re.search(r"\d+(\.\d+)?", ctc_text)
        return float(match.group()) if match else None

    def filter_ctc_min(self, queryset, name, value):
        matching_ids = [
            j.id
            for j in queryset
            if (self._extract_ctc_number(j.ctc) or 0) >= float(value)
        ]
        return queryset.filter(id__in=matching_ids)

    def filter_ctc_max(self, queryset, name, value):
        matching_ids = [
            j.id
            for j in queryset
            if (self._extract_ctc_number(j.ctc) or 0) <= float(value)
        ]
        return queryset.filter(id__in=matching_ids)


class ApplicationFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    branch = django_filters.CharFilter(
        field_name="student__branch", lookup_expr="iexact"
    )

    class Meta:
        model = Application
        fields = ["status", "branch"]
