# NOTE: the standalone Company model that used to live here has been consolidated
# into accounts.CompanyProfile (the model actually created at signup — see
# accounts/serializers.py RegisterSerializer). Keeping two separate "company"
# models was causing job postings to fail (Job.company expects CompanyProfile,
# but this app's views were creating/looking up the old Company model instead).
# This file intentionally has no models now; all company data lives in
# accounts.CompanyProfile.
